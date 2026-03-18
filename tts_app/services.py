"""
Service LAfricaMobile TTS
Gère l'authentification OAuth2, la traduction et la synthèse vocale.
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

    BASE_URL = getattr(settings, 'LAM_API_BASE', 'https://api.lafricamobile.com')
    TARGET_LANG = "wo"  # code ISO Wolof

    def __init__(self):
        self.token = None

    # ------------------------------------------------------------------ #
    #  AUTHENTIFICATION OAuth2                                             #
    # ------------------------------------------------------------------ #
    def authenticate(self):
        """
        Récupère un Bearer token via login/password.
        Endpoint : POST /auth/login  (à confirmer avec LAM)
        """
        url = f"{self.BASE_URL}/auth/login"
        payload = {
            "login": settings.LAM_LOGIN,
            "password": settings.LAM_PASSWORD,
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            self.token = data.get("access_token") or data.get("token")
            return {"success": True, "token": self.token}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

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
        Traduit un texte français en Wolof.
        POST /tts/translate
        Body : { "text": "...", "to_lang": "wo" }
        Réponse : { "text", "to_lang", "translated_text", "post_created_at" }
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
                "success": True,
                "original": text,
                "translated": data.get("translated_text", ""),
                "lang": data.get("to_lang", self.TARGET_LANG),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e),
                    "detail": getattr(e.response, 'text', '') if hasattr(e, 'response') else ''}

    # ------------------------------------------------------------------ #
    #  SYNTHÈSE VOCALE  Texte Wolof → Audio                               #
    # ------------------------------------------------------------------ #
    def synthesize(self, text: str, pitch: float = 0.0, speed: float = 1.0) -> dict:
        """
        Génère un fichier audio à partir d'un texte Wolof déjà traduit.
        POST /tts/vocalize
        Body : { "text": "...", "to_lang": "wo", "pitch": 0.0, "speed": 1.0 }
        Réponse : { "text", "to_lang", "path_audio", "post_created_at" }
        """
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/vocalize"
        payload = {
            "text": text,
            "to_lang": self.TARGET_LANG,
            "pitch": pitch,
            "speed": speed,
        }

        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return {
                "success": True,
                "audio_url": data.get("path_audio", ""),
                "text": data.get("text", text),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e),
                    "detail": getattr(e.response, 'text', '') if hasattr(e, 'response') else ''}

    # ------------------------------------------------------------------ #
    #  PIPELINE COMPLET  Français → Wolof → Audio (1 seul appel API)      #
    # ------------------------------------------------------------------ #
    def full_pipeline(self, text: str, pitch: float = 0.0, speed: float = 1.0) -> dict:
        """
        Traduction + synthèse en une seule requête.
        POST /tts/
        Body : { "text": "...", "to_lang": "wo", "pitch": 0.0, "speed": 1.0 }
        Réponse : { "text", "to_lang", "path_audio", "post_created_at" }
        """
        self._ensure_authenticated()
        if len(text) > 512:
            return {"success": False, "error": "Texte trop long (max 512 caractères)"}

        url = f"{self.BASE_URL}/tts/"
        payload = {
            "text": text,
            "to_lang": self.TARGET_LANG,
            "pitch": pitch,
            "speed": speed,
        }

        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return {
                "success": True,
                "audio_url": data.get("path_audio", ""),
                "text": data.get("text", text),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e),
                    "detail": getattr(e.response, 'text', '') if hasattr(e, 'response') else ''}

    # ------------------------------------------------------------------ #
    #  HISTORIQUE  (GET /tts/)                                             #
    # ------------------------------------------------------------------ #
    def get_history(self) -> dict:
        """
        Récupère l'historique de toutes les requêtes TTS.
        GET /tts/
        """
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
