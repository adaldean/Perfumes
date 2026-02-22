from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

@login_required
@user_passes_test(lambda u: u.is_staff)
def gestion_usuarios_view(request):
    """Vista para gestionar usuarios en el panel administrativo."""
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'gestion_clientes.html', {
        'usuarios': usuarios
    })
