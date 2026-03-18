"""
Service LAfricaMobile TTS
Gère l'authentification OAuth2, la traduction et la synthèse vocale.
Base URL : https://ttsapi.lafricamobile.com
"""
import requests
from django.conf import settings


class LAfricaMobileService:

    TARGET_LANG = "wo"

    # Endpoints — testés avec et sans trailing slash
    ENDPOINTS = {
        "login":      "/login",
        "tts":        "/tts/",
        "translate":  "/tts/translate",
        "vocalize":   "/tts/vocalize",
    }

    def __init__(self):
        self.token = None
        self.BASE_URL = getattr(settings, 'LAM_API_BASE', 'https://ttsapi.lafricamobile.com').rstrip('/')

    # ------------------------------------------------------------------ #
    #  AUTHENTIFICATION OAuth2                                             #
    # ------------------------------------------------------------------ #
    def authenticate(self):
        """
        POST /login
        Content-Type: application/x-www-form-urlencoded
        Réponse : { "access_token": "...", "token_type": "bearer" }
        """
        # On essaie /login puis /login/ si 404
        for path in ["/login", "/login/"]:
            url = f"{self.BASE_URL}{path}"
            payload = {
                "username":      settings.LAM_LOGIN,
                "password":      settings.LAM_PASSWORD,
                "grant_type":    "password",
                "scope":         "",
                "client_id":     "",
                "client_secret": "",
            }
            try:
                resp = requests.post(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=15
                )
                if resp.status_code == 404:
                    continue  # essaie la variante suivante
                resp.raise_for_status()
                data = resp.json()
                self.token = data.get("access_token") or data.get("token")
                return {"success": True, "token": self.token, "url_used": url}
            except requests.exceptions.HTTPError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "status": resp.status_code,
                    "detail": resp.text,
                    "url_tried": url,
                }
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "error": "Endpoint /login introuvable (404 sur toutes les variantes)."}

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _ensure_authenticated(self):
        if not self.token:
            result = self.authenticate()
            if not result["success"]:
                raise ConnectionError(f"Authentification échouée : {result.get('error')} | detail: {result.get('detail','')}")

    # ------------------------------------------------------------------ #
    #  TRADUCTION  Français → Wolof                                        #
    # ------------------------------------------------------------------ #
    def translate(self, text: str) -> dict:
        """POST /tts/translate"""
        self._ensure_authenticated()
        if len(text) > 512:
            return {"success": False, "error": "Texte trop long (max 512 caractères)"}

        url = f"{self.BASE_URL}/tts/translate"
        payload = {"text": text, "to_lang": self.TARGET_LANG}
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return {
                "success":    True,
                "original":   text,
                "translated": data.get("translated_text", ""),
                "lang":       data.get("to_lang", self.TARGET_LANG),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            detail = getattr(getattr(e, "response", None), "text", "")
            return {"success": False, "error": str(e), "detail": detail}

    # ------------------------------------------------------------------ #
    #  SYNTHÈSE VOCALE  Texte Wolof → Audio                               #
    # ------------------------------------------------------------------ #
    def synthesize(self, text: str, pitch: float = 0.0, speed: float = 1.0) -> dict:
        """POST /tts/vocalize"""
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/vocalize"
        payload = {
            "text":    text,
            "to_lang": self.TARGET_LANG,
            "pitch":   pitch,
            "speed":   speed,
        }
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return {
                "success":   True,
                "audio_url": data.get("path_audio", ""),
                "text":      data.get("text", text),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            detail = getattr(getattr(e, "response", None), "text", "")
            return {"success": False, "error": str(e), "detail": detail}

    # ------------------------------------------------------------------ #
    #  PIPELINE COMPLET  Français → Wolof → Audio                         #
    # ------------------------------------------------------------------ #
    def full_pipeline(self, text: str, pitch: float = 0.0, speed: float = 1.0) -> dict:
        """POST /tts/ — traduction + synthèse en une seule requête"""
        self._ensure_authenticated()
        if len(text) > 512:
            return {"success": False, "error": "Texte trop long (max 512 caractères)"}

        url = f"{self.BASE_URL}/tts/"
        payload = {
            "text":    text,
            "to_lang": self.TARGET_LANG,
            "pitch":   pitch,
            "speed":   speed,
        }
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return {
                "success":   True,
                "audio_url": data.get("path_audio", ""),
                "text":      data.get("text", text),
                "translated": data.get("translated_text", ""),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            detail = getattr(getattr(e, "response", None), "text", "")
            return {"success": False, "error": str(e), "detail": detail}

    # ------------------------------------------------------------------ #
    #  HISTORIQUE  GET /tts/                                               #
    # ------------------------------------------------------------------ #
    def get_history(self) -> dict:
        """GET /tts/"""
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
