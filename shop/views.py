from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Module, UserModule


def all_modules(request):
    modules = Module.objects.all()

    # Get users purshaceed modules
    purchased_modules = []
    if request.user.is_authenticated:
        purchased_modules = UserModule.objects.filter(
            user=request.user
        ).values_list('module_id', flat=True)

    context = {
        'modules': modules,
        'purchased_modules': purchased_modules,
    }

    return render(request, 'shop/modules.html', context)


@login_required
def module_detail(request, module_id):
    module = get_object_or_404(Module, pk=module_id)

    # Check if user ownd this module
    user_owns_module = UserModule.objects.filter(
        user=request.user,
        module=module
    ).exists()

    context = {
        'module': module,
        'user_owns_module': user_owns_module,
    }

    return render(request, 'shop/module_detail.html', context)


@login_required
def add_to_cart(request, module_id):
    """ Add a module to the shopping cart """
    module = get_object_or_404(Module, pk=module_id)

    # Check if user already owns this module
    if UserModule.objects.filter(user=request.user, module=module).exists():
        messages.error(request, 'You already own this module!')
        return redirect('shop:module_detail', module_id=module_id)

    # Get the cart from session or create empty dict
    cart = request.session.get('cart', {})

    # Add module to cart
    cart[str(module_id)] = 1

    # Save cart back to session
    request.session['cart'] = cart
    messages.success(request, f'{module.name} added to cart!')

    return redirect('shop:modules')


def view_cart(request):
    """Display the shopping cart"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for module_id, quantity in cart.items():
        module = get_object_or_404(Module, pk=module_id)
        total += module.price
        cart_items.append({
            'module': module,
            'quantity': quantity,
        })
    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'shop/cart.html', context)


@login_required
def remove_from_cart(request, module_id):
    """ Remove a module from the shopping cart via AJAX """
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if str(module_id) in cart:
            del cart[str(module_id)]
            request.session['cart'] = cart

            # Calculate new total
            total = 0

            for mid in cart.keys():
                module = Module.objects.get(pk=mid)
                total += module.price

            return JsonResponse({
                'success': True,
                'cart_count': len(cart),
                'cart_total': float(total),
                'message': 'Item removed successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Item not found in cart'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def clear_cart(request):
    """ Clear the entire shopping cart via AJAX """
    if request.method == 'POST':
        request.session['cart'] = {}
        return JsonResponse({
            'success': True,
            'cart_count': 0,
            'cart_total': 0.0,
            'message': 'Cart cleared successfully!'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'})
