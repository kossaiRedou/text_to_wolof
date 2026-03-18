import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import LAfricaMobileService


def index(request):
    """Page principale de l'application Fatou BRAVO TTS."""
    return render(request, 'tts_app/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def api_translate(request):
    """
    Traduit du texte français en Wolof.
    POST /api/translate/
    Body JSON : { "text": "..." }
    """
    try:
        body = json.loads(request.body)
        text = body.get("text", "").strip()
        if not text:
            return JsonResponse({"success": False, "error": "Le texte est vide."}, status=400)

        svc = LAfricaMobileService()
        result = svc.translate(text)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON invalide."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_synthesize(request):
    """
    Génère l'audio depuis un texte Wolof déjà traduit.
    POST /api/synthesize/
    Body JSON : { "text": "...", "pitch": 0.0, "speed": 1.0 }
    """
    try:
        body = json.loads(request.body)
        text = body.get("text", "").strip()
        pitch = float(body.get("pitch", 0.0))
        speed = float(body.get("speed", 1.0))

        if not text:
            return JsonResponse({"success": False, "error": "Le texte est vide."}, status=400)

        svc = LAfricaMobileService()
        result = svc.synthesize(text, pitch=pitch, speed=speed)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON invalide."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_full_pipeline(request):
    """
    Pipeline complet : Français → Wolof → Audio (1 seul appel API LAM).
    POST /api/generate/
    Body JSON : { "text": "...", "pitch": 0.0, "speed": 1.0 }
    """
    try:
        body = json.loads(request.body)
        text = body.get("text", "").strip()
        pitch = float(body.get("pitch", 0.0))
        speed = float(body.get("speed", 1.0))

        if not text:
            return JsonResponse({"success": False, "error": "Le texte est vide."}, status=400)

        svc = LAfricaMobileService()
        result = svc.full_pipeline(text, pitch=pitch, speed=speed)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON invalide."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def api_history(request):
    """
    Récupère l'historique des requêtes TTS.
    GET /api/history/
    """
    try:
        svc = LAfricaMobileService()
        result = svc.get_history()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def api_debug_auth(request):
    """
    Endpoint de diagnostic : teste l'authentification LAM et affiche le résultat.
    GET /api/debug/
    """
    from django.conf import settings as s
    svc = LAfricaMobileService()
    result = svc.authenticate()
    return JsonResponse({
        "config": {
            "LAM_API_BASE": s.LAM_API_BASE,
            "LAM_LOGIN": s.LAM_LOGIN[:3] + "***" if s.LAM_LOGIN else "(vide)",
            "LAM_PASSWORD": "***" if s.LAM_PASSWORD else "(vide)",
        },
        "auth_result": result
    })
