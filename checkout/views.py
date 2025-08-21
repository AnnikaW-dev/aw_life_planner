# checkout/views.py
import stripe
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import HttpResponse
from shop.models import Module, UserModule

from .forms import OrderForm
from .models import Order, OrderLineItem

import stripe
import json
import time

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        cart = request.session.get('cart', {})

        if not cart:
            messages.error(request, "Your cart is empty!")
            return redirect('shop:modules')

        form_data = {
            'full_name': request.POST.get('full_name', ''),
            'email': request.POST.get('email', ''),
            'phone_number': request.POST.get('phone_number', ''),
        }

        order_form = OrderForm(form_data)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.user = request.user

            # Get payment intent ID
            client_secret = request.POST.get('client_secret', '')
            payment_intent_id = request.POST.get('payment_intent_id', '')

            if payment_intent_id:
                order.stripe_pid = payment_intent_id
            elif client_secret:
                pid = client_secret.split('_secret')[0]
                order.stripe_pid = pid
            else:
                order.stripe_pid = f"temp_{timezone.now().timestamp()}"

            order.save()

            # Add line items and create UserModule entries
            total = 0
            for module_id in cart:
                try:
                    module = Module.objects.get(id=module_id)

                    order_line_item = OrderLineItem(
                        order=order,
                        module=module,
                    )
                    order_line_item.save()
                    total += module.price

                    # Grant user access to the module
                    UserModule.objects.get_or_create(
                        user=request.user,
                        module=module
                    )

                except Module.DoesNotExist:
                    messages.error(request, "One of the modules in your cart wasn't found.")
                    order.delete()
                    return redirect('shop:modules')

            # Update order total
            order.total = total
            order.save()

            # Clear the cart
            if 'cart' in request.session:
                del request.session['cart']

            messages.success(request, f'Order successfully processed! Order number: {order.order_number}')
            return redirect('checkout:checkout_success', order_number=order.order_number)

        else:
            messages.error(request, 'There was an error with your form. Please check your information.')

    else:
        # GET request - show checkout form
        cart = request.session.get('cart', {})

        if not cart:
            messages.error(request, "There's nothing in your cart!")
            return redirect('shop:modules')

        # Calculate total
        total = 0
        cart_items = []
        for module_id in cart:
            try:
                module = get_object_or_404(Module, pk=module_id)
                total += module.price
                cart_items.append({'module': module})
            except:
                messages.error(request, "Invalid item in cart.")
                return redirect('shop:modules')

        # Create Stripe payment intent
        stripe_total = round(total * 100)

        try:
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
                metadata={
                    'username': request.user.username,
                    'cart_items': ','.join(cart.keys())
                }
            )
        except Exception as e:
            messages.error(request, f'Payment system error: {str(e)}')
            return redirect('shop:view_cart')

        order_form = OrderForm()

        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing!')

        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
            'cart_items': cart_items,
            'total': total,
        }

        return render(request, 'checkout/checkout.html', context)

@login_required
def checkout_success(request, order_number):
    """Handle successful checkouts"""
    try:
        order = get_object_or_404(Order, order_number=order_number, user=request.user)

        context = {'order': order}
        return render(request, 'checkout/checkout_success.html', context)

    except Exception as e:
        messages.error(request, 'There was an error processing your order.')
        return redirect('shop:modules')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Listen for webhooks from Stripe"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WH_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print(f"❌ Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"❌ Invalid signature: {e}")
        return HttpResponse(status=400)

    # Handle the event
    print(f"🎯 Webhook received: {event['type']}")

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"✅ Payment succeeded: {payment_intent['id']} for ${payment_intent['amount']/100}")

        # Webhook backup: Ensure order exists
        _handle_payment_intent_succeeded(payment_intent)

    elif event['type'] == 'payment_intent.created':
        payment_intent = event['data']['object']
        print(f"💳 Payment intent created: {payment_intent['id']}")

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"❌ Payment failed: {payment_intent['id']}")

    else:
        print(f"🔔 Unhandled event type: {event['type']}")

    return HttpResponse(status=200)

def _handle_payment_intent_succeeded(payment_intent):
    """
    Handle successful payment - backup for webhook reliability
    This ensures orders are created even if the main flow fails
    """
    pid = payment_intent['id']

    try:
        # Check if order already exists
        order = Order.objects.get(stripe_pid=pid)
        print(f"✅ Order already exists: {order.order_number}")
        return order

    except Order.DoesNotExist:
        # Order doesn't exist - create it from webhook
        print(f"⚠️  Creating order from webhook for payment: {pid}")

        # Extract metadata
        metadata = payment_intent.get('metadata', {})
        username = metadata.get('username')

        if not username:
            print("❌ No username in payment metadata")
            return None

        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=username)

            # Create order from webhook
            order = Order.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}" or username,
                email=user.email,
                phone_number="",  # Not available in webhook
                total=payment_intent['amount'] / 100,
                stripe_pid=pid,
            )

            print(f"✅ Order created from webhook: {order.order_number}")
            return order

        except User.DoesNotExist:
            print(f"❌ User not found: {username}")
            return None

    except Exception as e:
        print(f"❌ Error in webhook handler: {e}")
        return None
