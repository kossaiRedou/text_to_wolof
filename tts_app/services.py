"""
Service LAfricaMobile TTS
Gère l'authentification OAuth2, la traduction et la synthèse vocale.

⚠️  URL de PRODUCTION : contactez assistance@lafricamobile.com
    puis renseignez LAM_API_BASE dans votre .env
"""
import requests
from django.conf import settings


class LAfricaMobileService:
    """
    Client pour l'API LAfricaMobile TTS.

    Workflow disponible :
    1. authenticate()       → récupère le Bearer token OAuth2
    2. translate(text)      → traduit le français en Wolof (max 512 chars)
    3. synthesize(text)     → génère l'audio depuis un texte Wolof
    4. full_pipeline(text)  → traduction + synthèse en une seule opération (POST /tts/)
    """

    # ⚠️  L'URL de prod est fournie par LAM sur demande : assistance@lafricamobile.com
    TARGET_LANG = "wo"  # code ISO Wolof

    def __init__(self):
        self.token = None
        self.BASE_URL = getattr(settings, 'LAM_API_BASE', 'https://ttsapi.lafricamobile.com').rstrip('/')

    def _check_base_url(self):
        if not self.BASE_URL:
            raise ValueError(
                "LAM_API_BASE non configuré dans le .env. "
                "Contactez assistance@lafricamobile.com pour obtenir l'URL de production."
            )

    # ------------------------------------------------------------------ #
    #  AUTHENTIFICATION OAuth2                                             #
    # ------------------------------------------------------------------ #
    def authenticate(self):
        """
        Récupère un Bearer token OAuth2.
        Endpoint  : POST /login
        Body type : application/x-www-form-urlencoded (PAS du JSON !)
        Champs    : username, password, grant_type, scope, client_id, client_secret
        Réponse   : { "access_token": "...", "token_type": "bearer" }
        """
        self._check_base_url()
        url = f"{self.BASE_URL}/login"

        # ⚠️ form-urlencoded — utiliser data= et non json=
        payload = {
            "username":      settings.LAM_LOGIN,
            "password":      settings.LAM_PASSWORD,
            "grant_type":    "",
            "scope":         "",
            "client_id":     "",
            "client_secret": "",
        }
        try:
            resp = requests.post(url, data=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self.token = data.get("access_token") or data.get("token")
            return {"success": True, "token": self.token}
        except requests.exceptions.RequestException as e:
            detail = ""
            if hasattr(e, "response") and e.response is not None:
                detail = e.response.text
            return {"success": False, "error": str(e), "detail": detail}

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _ensure_authenticated(self):
        if not self.token:
            result = self.authenticate()
            if not result["success"]:
                raise ConnectionError(f"Authentification échouée : {result['error']}")

    # ------------------------------------------------------------------ #
    #  TRADUCTION  Français → Wolof                                        #
    # ------------------------------------------------------------------ #
    def translate(self, text: str) -> dict:
        """
        POST /tts/translate
        Body JSON : { "text": "...", "to_lang": "wo" }
        Réponse   : { "text", "to_lang", "translated_text", "post_created_at" }
        """
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
        """
        POST /tts/vocalize
        Body JSON : { "text": "...", "to_lang": "wo", "pitch": 0.0, "speed": 1.0 }
        Réponse   : { "text", "to_lang", "path_audio", "post_created_at" }
        """
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
                "success":    True,
                "audio_url":  data.get("path_audio", ""),
                "text":       data.get("text", text),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            detail = getattr(getattr(e, "response", None), "text", "")
            return {"success": False, "error": str(e), "detail": detail}

    # ------------------------------------------------------------------ #
    #  PIPELINE COMPLET  Français → Wolof → Audio                         #
    # ------------------------------------------------------------------ #
    def full_pipeline(self, text: str, pitch: float = 0.0, speed: float = 1.0) -> dict:
        """
        POST /tts/
        Body JSON : { "text": "...", "to_lang": "wo", "pitch": 0.0, "speed": 1.0 }
        Réponse   : { "text", "to_lang", "path_audio", "post_created_at" }
        """
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
                "success":    True,
                "audio_url":  data.get("path_audio", ""),
                "text":       data.get("text", text),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            detail = getattr(getattr(e, "response", None), "text", "")
            return {"success": False, "error": str(e), "detail": detail}

    # ------------------------------------------------------------------ #
    #  HISTORIQUE  GET /tts/                                               #
    # ------------------------------------------------------------------ #
    def get_history(self) -> dict:
        """GET /tts/ — Historique des requêtes TTS."""
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
