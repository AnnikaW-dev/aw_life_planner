from django.shortcuts import render, redirect, get_object_or_404
from django. contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

from shop.models import Module
from .forms import OrderForm

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "There's nothing in your cart!")
        return redirect('shop:modules')

    # Calculate total
    total = 0
    cart_items = []
    for module_id in cart:
        module = get_object_or_404(Module, pk=module_id)
        total += module.price
        cart_items.append({
            'module': module,
        })

    # Stripe payment intent
    stripe_total = round(total * 100)  # Stripe expects ammount in cents
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    order_form = OrderForm()
    if not stripe_public_key:
        messages.warning(request, 'Stripe publickey is missing!')

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
    """ Handle successful checkouts """
    messages.success(
        request,
        f'Order successfully processed! Your order Number is {order_number}'
        )

    if 'cart' in request.session:
        del request.session['cart']

    return render(
        request,
        'checkout/checkout_success.html', {'order_number': order_number}
        )
