from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Module, UserModule

User = get_user_model()

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

    #Check if user ownd this module
    user_owns_module = UserModule.objects.filter(
        user=request.user,
        module=module
    ).exists()

    context = {
        'module': module,
        'user_owns_module': user_owns_module,
    }

    return render(request, 'shop/module_detail.html', context)
