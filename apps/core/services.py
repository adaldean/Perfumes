import requests
import os
from django.conf import settings

def validate_email(email):
    """
    Valida un correo electrónico utilizando la API de Hunter.io.

    Args:
        email (str): El correo electrónico a validar.

    Returns:
        dict: Un diccionario con 'status' (valid, risky, invalid) y 'score' (float).
              En caso de error, devuelve {'status': 'error', 'score': 0.0}
    """
    api_key = settings.HUNTER_API_KEY
    if not api_key:
        return {'status': 'error', 'score': 0.0, 'message': 'API key no configurada'}

    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={api_key}"

    try:
        response = requests.get(url, timeout=10)  # Timeout de 10 segundos
        response.raise_for_status()  # Lanza excepción si status no es 2xx
        data = response.json()

        # Extraer status y score de la respuesta
        status = data.get('data', {}).get('status', 'invalid')
        score = data.get('data', {}).get('score', 0.0)

        return {'status': status, 'score': score}

    except requests.exceptions.Timeout:
        return {'status': 'error', 'score': 0.0, 'message': 'Timeout en la solicitud'}
    except requests.exceptions.RequestException as e:
        return {'status': 'error', 'score': 0.0, 'message': f'Error de conexión: {str(e)}'}
    except ValueError:
        return {'status': 'error', 'score': 0.0, 'message': 'Respuesta JSON inválida'}