import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import LAfricaMobileService


def index(request):
    return render(request, 'tts_app/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def api_translate(request):
    try:
        body = json.loads(request.body)
        text = body.get("text", "").strip()
        if not text:
            return JsonResponse({"success": False, "error": "Le texte est vide."}, status=400)
        svc = LAfricaMobileService()
        return JsonResponse(svc.translate(text))
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_synthesize(request):
    try:
        body = json.loads(request.body)
        text  = body.get("text", "").strip()
        pitch = float(body.get("pitch", 0.0))
        speed = float(body.get("speed", 1.0))
        if not text:
            return JsonResponse({"success": False, "error": "Le texte est vide."}, status=400)
        svc = LAfricaMobileService()
        return JsonResponse(svc.synthesize(text, pitch=pitch, speed=speed))
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_full_pipeline(request):
    try:
        body = json.loads(request.body)
        text  = body.get("text", "").strip()
        pitch = float(body.get("pitch", 0.0))
        speed = float(body.get("speed", 1.0))
        if not text:
            return JsonResponse({"success": False, "error": "Le texte est vide."}, status=400)
        svc = LAfricaMobileService()
        return JsonResponse(svc.full_pipeline(text, pitch=pitch, speed=speed))
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def api_history(request):
    try:
        svc = LAfricaMobileService()
        return JsonResponse(svc.get_history())
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def api_credits(request):
    """GET /api/credits/ — solde restant en minutes"""
    try:
        svc = LAfricaMobileService()
        return JsonResponse(svc.get_credits())
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def api_languages(request):
    """GET /api/languages/ — langues disponibles"""
    try:
        svc = LAfricaMobileService()
        return JsonResponse(svc.get_languages())
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_http_methods(["GET"])
def api_debug_auth(request):
    """GET /api/debug/ — teste l'authentification et affiche le résultat"""
    from django.conf import settings as s
    svc = LAfricaMobileService()
    result = svc.authenticate()
    return JsonResponse({
        "config": {
            "LAM_API_BASE": s.LAM_API_BASE,
            "LAM_LOGIN":    s.LAM_LOGIN[:3] + "***" if s.LAM_LOGIN else "(vide)",
            "LAM_PASSWORD": "***" if s.LAM_PASSWORD else "(vide)",
        },
        "auth_result": result
    })
