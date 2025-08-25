# checkout/webhook_handler.py
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

from .models import Order, OrderLineItem
from shop.models import Module, UserModule

import time
import logging

logger = logging.getLogger(__name__)


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        try:
            cust_email = order.email
            subject = render_to_string(
                'checkout/confirmation_emails/confirmation_email_subject.txt',
                {'order': order})
            body = render_to_string(
                'checkout/confirmation_emails/confirmation_email_body.txt',
                {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [cust_email]
            )
            logger.info(f"✅ Confirmation email sent to {cust_email}")
        except Exception as e:
            logger.error(f"❌ Failed to send confirmation email: {e}")

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        event_type = event['type'] if isinstance(event, dict) else event.type
        logger.info(f"🔔 Unhandled webhook received: {event_type}")
        return HttpResponse(
            content=f'Unhandled webhook received: {event_type}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        # Handle both real Stripe events and test dictionary events
        if hasattr(event, 'data'):
            # Real Stripe event object
            intent = event.data.object
        else:
            # Test dictionary event
            intent = event['data']['object']

        pid = intent['id'] if isinstance(intent, dict) else intent.id
        amount = (
            intent['amount'] if isinstance(intent, dict)
            else intent.amount
        )
        total = round(amount / 100, 2)

        logger.info(f"🎯 Processing payment_intent.succeeded for {pid}")

        # Get metadata - handle both dict and object formats
        if isinstance(intent, dict):
            metadata = intent.get('metadata', {})
            charges_data = intent.get('charges', {}).get('data', [])
        else:
            metadata = getattr(intent, 'metadata', {})
            charges = getattr(intent, 'charges', None)
            charges_data = charges.data if charges else []

        username = metadata.get('username')
        cart_items = metadata.get('cart_items', '')

        # Get billing details
        if charges_data:
            billing_details = (
                charges_data[0].get('billing_details', {})
                if isinstance(charges_data[0], dict)
                else charges_data[0].billing_details
            )
            if isinstance(billing_details, dict):
                email = billing_details.get('email', '')
                name = billing_details.get('name', '')
            else:
                email = getattr(billing_details, 'email', '')
                name = getattr(billing_details, 'name', '')
        else:
            email = ''
            name = ''

        # Try to find existing order first (5 attempts with delays)
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(stripe_pid=pid)
                order_exists = True
                logger.info(f"✅ Order already exists: {order.order_number}")
                break
            except Order.DoesNotExist:
                attempt += 1
                if attempt <= 5:
                    time.sleep(1)

        if order_exists:
            # Order already exists, send confirmation email
            self._send_confirmation_email(order)
            event_type = (
                event["type"] if isinstance(event, dict)
                else event.type
            )
            return HttpResponse(
                content=(
                    f'Webhook received: {event_type} | '
                    f'SUCCESS: Verified order already in database'
                ),
                status=200)
        else:
            # Create order from webhook (backup mechanism)
            logger.warning(
                f"⚠️  Creating order from webhook for payment: {pid}"
            )

            # Check if we have username - if not, we can't create order
            if not username or username == 'AnonymousUser':
                logger.error(f"❌ No username in payment metadata for {pid}")
                event_type = (
                    event["type"] if isinstance(event, dict)
                    else event.type
                )
                return HttpResponse(
                    content=(
                        f'Webhook received: {event_type} | '
                        f'ERROR: No username in metadata'
                    ),
                    status=200)  # Return 200 but don't create order

            order = None
            try:
                # Get user
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    logger.error(f"❌ User not found: {username}")
                    event_type = (
                        event["type"] if isinstance(event, dict)
                        else event.type
                    )
                    return HttpResponse(
                        content=(
                            f'Webhook received: {event_type} | '
                            f'ERROR: User not found'
                        ),
                        status=200)  # Return 200 but don't create order

                # Create order
                full_name = (
                    name or
                    (f"{user.first_name} {user.last_name}"
                     f" if user else username")
                )
                order = Order.objects.create(
                    user=user,
                    full_name=full_name,
                    email=email or user.email,
                    phone_number="",  # Not available in webhook
                    total=total,
                    stripe_pid=pid,
                )

                # Create order line items from cart_items metadata
                if cart_items:
                    try:
                        cart_item_ids = cart_items.split(',')
                        for module_id in cart_item_ids:
                            if module_id.strip():
                                try:
                                    module = Module.objects.get(
                                        id=int(module_id.strip())
                                    )
                                    OrderLineItem.objects.create(
                                        order=order,
                                        module=module,
                                    )
                                    # Grant user access to module
                                    UserModule.objects.get_or_create(
                                        user=user,
                                        module=module
                                    )
                                    logger.info(
                                        f"✅ Added module {module.name} "
                                        f"to order {order.order_number}"
                                    )
                                except (Module.DoesNotExist, ValueError) as e:
                                    logger.error(
                                        f"❌ Error processing module "
                                        f"{module_id}: {e}"
                                    )
                    except Exception as e:
                        logger.error(f"❌ Error processing cart items: {e}")

                logger.info(
                    f"✅ Order created from webhook: {order.order_number}"
                )

            except Exception as e:
                logger.error(f"❌ Error creating order from webhook: {e}")
                if order:
                    order.delete()
                event_type = (
                    event["type"] if isinstance(event, dict)
                    else event.type
                )
                return HttpResponse(
                    content=f'Webhook received: {event_type} | ERROR: {e}',
                    status=500)

            # Send confirmation email for webhook-created order
            self._send_confirmation_email(order)
            event_type = (
                event["type"] if isinstance(event, dict)
                else event.type
            )
            return HttpResponse(
                content=(
                    f'Webhook received: {event_type} | '
                    f'SUCCESS: Created order in webhook'
                ),
                status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        # Handle both real Stripe events and test dictionary events
        if hasattr(event, 'data'):
            intent = event.data.object
            event_type = event.type
        else:
            intent = event['data']['object']
            event_type = event['type']

        pid = intent['id'] if isinstance(intent, dict) else intent.id
        logger.warning(f"❌ Payment failed for {pid}")

        return HttpResponse(
            content=f'Webhook received: {event_type} | Payment failed: {pid}',
            status=200)
