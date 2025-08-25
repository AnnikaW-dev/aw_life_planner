# checkout/views.py
import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from shop.models import Module, UserModule
from .forms import OrderForm
from .models import Order, OrderLineItem
from .webhooks import webhook


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY

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

            # MOVED: Calculate total and add line items BEFORE using total
            total = 0
            for module_id in cart:
                try:
                    module = Module.objects.get(id=module_id)

                    order_line_item = OrderLineItem(
                        order=order,
                        module=module,
                    )
                    # Note: We'll save this after the order is saved
                    total += module.price

                    # Grant user access to the module
                    UserModule.objects.get_or_create(
                        user=request.user,
                        module=module
                    )

                except Module.DoesNotExist:
                    messages.error(
                        request,
                        "One of the modules in your cart wasn't found."
                        )
                    if order.pk:  # Only delete if order was saved
                        order.delete()
                    return redirect('shop:modules')

            # NOW we can set the total and save the order
            order.total = total
            order.save()

            # Now save the line items (they need the order to exist first)
            for module_id in cart:
                try:
                    module = Module.objects.get(id=module_id)
                    order_line_item = OrderLineItem(
                        order=order,
                        module=module,
                    )
                    order_line_item.save()
                except Module.DoesNotExist:
                    continue  # Already handled above

            # Send confirmation email
            try:
                subject = render_to_string(
                    'checkout/confirmation_emails/'
                    'confirmation_email_subject.txt',
                    {'order': order})
                body = render_to_string(
                    'checkout/confirmation_emails/confirmation_email_body.txt',
                    {'order': order,
                     'contact_email': settings.DEFAULT_FROM_EMAIL})

                send_mail(
                    subject.strip(),
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=True,  # Don't break checkout if email fails
                )
            except Exception as e:
                # Log error but don't break the checkout process
                print(f"Failed to send confirmation email: {e}")

            # Clear the cart
            if 'cart' in request.session:
                del request.session['cart']

            messages.success(
                request,
                f'Order successfully processed!'
                f' Order number:{order.order_number}'
                )
            return redirect(
                'checkout:checkout_success', order_number=order.order_number
                )

        else:
            messages.error(
                request,
                'There was an error with your form. '
                'Please check your information.'
                )

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
            except (Module.DoesNotExist, ValueError, TypeError):
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
        order = get_object_or_404(
            Order, order_number=order_number, user=request.user
            )

        context = {'order': order}
        return render(request, 'checkout/checkout_success.html', context)

    except Exception:
        messages.error(request, 'There was an error processing your order.')
        return redirect('shop:modules')


# The webhook view is now imported from webhooks.py
stripe_webhook = webhook
