from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import os
import requests


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_api(request):
    text = ((request.data or {}).get('message') or '').strip()
    if not text:
        return Response({'reply': 'Escribe un mensaje para poder ayudarte.'}, status=400)

    t = text.lower()
    if 'horario' in t or 'horarios' in t:
        return Response({'reply': 'Nuestro horario es Lunes a Viernes 9:00-18:00.'})
    if 'envío' in t or 'envios' in t:
        return Response({'reply': 'Envíos dentro de 3-5 días hábiles. Ver sección Envíos para más detalles.'})

    gemini_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not gemini_key:
        return Response({'reply': 'Chat inteligente no disponible temporalmente. Configura GEMINI_API_KEY para habilitarlo.'})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    payload = {
        'contents': [
            {
                'parts': [
                    {
                        'text': (
                            'Eres el asistente virtual de una tienda de perfumes llamada Aura Essence. '
                            'Responde en español de forma breve, clara y amable. '
                            'Si el usuario pregunta por precios, disponibilidad o envíos específicos, '
                            'indica que confirme en el catálogo o con soporte para datos actualizados.\n\n'
                            f'Pregunta del usuario: {text}'
                        )
                    }
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0.6,
            'maxOutputTokens': 220,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        candidates = data.get('candidates') or []
        parts = (((candidates[0] if candidates else {}).get('content') or {}).get('parts') or [])
        model_reply = ''.join(part.get('text', '') for part in parts).strip()
        if not model_reply:
            model_reply = 'No pude generar una respuesta en este momento. Intenta nuevamente.'
        return Response({'reply': model_reply})
    except requests.RequestException:
        return Response({'reply': 'No pude conectar con el asistente en este momento. Intenta nuevamente en unos minutos.'})
