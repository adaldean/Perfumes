from django.shortcuts import render

def contacto_view(request):
    """Vista para mostrar el formulario de contacto."""
    if request.method == 'POST':
        # Aquí iría la lógica para enviar el correo
        success = True
        return render(request, 'contacto.html', {'success': success})
    return render(request, 'contacto.html')

def terminos_view(request):
    """Vista de Términos de Servicio."""
    return render(request, 'legal/terminos.html')

def privacidad_view(request):
    """Vista de Política de Privacidad."""
    return render(request, 'legal/privacidad.html')

def devoluciones_view(request):
    """Vista de Política de Devoluciones."""
    return render(request, 'legal/devoluciones.html')

def cookies_view(request):
    """Vista de Política de Cookies."""
    return render(request, 'legal/cookies.html')
