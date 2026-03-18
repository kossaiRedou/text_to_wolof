"""
Service LAfricaMobile TTS
Base URL : https://ttsapi.lafricamobile.com
Spec     : openapi.json confirmée le 2026-03-18
"""
import requests
from django.conf import settings


class LAfricaMobileService:

    TARGET_LANG = "wo"

    def __init__(self):
        self.token = None
        self.refresh_token = None
        self.BASE_URL = getattr(settings, 'LAM_API_BASE', 'https://ttsapi.lafricamobile.com').rstrip('/')

    # ------------------------------------------------------------------ #
    #  AUTH  POST /login  (application/x-www-form-urlencoded)             #
    # ------------------------------------------------------------------ #
    def authenticate(self):
        """
        Réponse : { access_token, refresh_token, token_type }
        ⚠️  grant_type doit valoir exactement "password" (pattern requis)
        """
        url = f"{self.BASE_URL}/login"
        payload = {
            "username":      settings.LAM_LOGIN,
            "password":      settings.LAM_PASSWORD,
            "grant_type":    "password",   # ← obligatoire, pattern="password"
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
            resp.raise_for_status()
            data = resp.json()
            self.token         = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            return {"success": True, "token": self.token}
        except requests.exceptions.RequestException as e:
            detail = ""
            if hasattr(e, "response") and e.response is not None:
                detail = e.response.text
            return {"success": False, "error": str(e), "detail": detail}

    # ------------------------------------------------------------------ #
    #  REFRESH  POST /refresh  { refresh_token }                          #
    # ------------------------------------------------------------------ #
    def refresh(self):
        """Renouvelle le access_token via le refresh_token."""
        if not self.refresh_token:
            return self.authenticate()
        url = f"{self.BASE_URL}/refresh"
        try:
            resp = requests.post(
                url,
                json={"refresh_token": self.refresh_token},
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            self.token = data.get("access_token")
            return {"success": True, "token": self.token}
        except requests.exceptions.RequestException as e:
            return self.authenticate()  # fallback → re-login complet

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type":  "application/json",
        }

    def _ensure_authenticated(self):
        if not self.token:
            result = self.authenticate()
            if not result["success"]:
                raise ConnectionError(
                    f"Authentification échouée : {result.get('error')} "
                    f"| detail: {result.get('detail', '')}"
                )

    # ------------------------------------------------------------------ #
    #  CRÉDITS  GET /users/me/credits                                     #
    # ------------------------------------------------------------------ #
    def get_credits(self) -> dict:
        """Retourne le solde restant en minutes."""
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/users/me/credits"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------ #
    #  LANGUES DISPONIBLES  GET /tts/languages                            #
    # ------------------------------------------------------------------ #
    def get_languages(self) -> dict:
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/languages"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            return {"success": True, "languages": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------ #
    #  TRADUCTION  POST /tts/translate                                    #
    #  Body : { text, to_lang }                                           #
    #  Réponse : { text, to_lang, translated_text, post_created_at }      #
    # ------------------------------------------------------------------ #
    def translate(self, text: str) -> dict:
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/translate"
        try:
            resp = requests.post(
                url,
                json={"text": text, "to_lang": self.TARGET_LANG},
                headers=self._headers(),
                timeout=30
            )
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
    #  SYNTHÈSE  POST /tts/vocalize                                       #
    #  Body : { text, to_lang, pitch, speed }                             #
    #  Réponse : { text, to_lang, path_audio, duration, post_created_at } #
    # ------------------------------------------------------------------ #
    def synthesize(self, text: str, pitch: float = 0.0, speed: float = 1.0) -> dict:
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/vocalize"
        try:
            resp = requests.post(
                url,
                json={"text": text, "to_lang": self.TARGET_LANG, "pitch": pitch, "speed": speed},
                headers=self._headers(),
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "success":    True,
                "audio_url":  data.get("path_audio", ""),
                "text":       data.get("text", text),
                "duration":   data.get("duration"),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            detail = getattr(getattr(e, "response", None), "text", "")
            return {"success": False, "error": str(e), "detail": detail}

    # ------------------------------------------------------------------ #
    #  PIPELINE COMPLET  POST /tts/                                       #
    #  Body : { text, to_lang, pitch, speed }                             #
    #  Réponse : { text, to_lang, path_audio, duration, post_created_at } #
    # ------------------------------------------------------------------ #
    def full_pipeline(self, text: str, pitch: float = 0.0, speed: float = 1.0) -> dict:
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/"
        try:
            resp = requests.post(
                url,
                json={"text": text, "to_lang": self.TARGET_LANG, "pitch": pitch, "speed": speed},
                headers=self._headers(),
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "success":    True,
                "audio_url":  data.get("path_audio", ""),
                "text":       data.get("text", text),
                "translated": data.get("translated_text", ""),
                "duration":   data.get("duration"),
                "created_at": data.get("post_created_at", ""),
            }
        except requests.exceptions.RequestException as e:
            detail = getattr(getattr(e, "response", None), "text", "")
            return {"success": False, "error": str(e), "detail": detail}

    # ------------------------------------------------------------------ #
    #  HISTORIQUE  GET /tts/                                              #
    # ------------------------------------------------------------------ #
    def get_history(self) -> dict:
        self._ensure_authenticated()
        url = f"{self.BASE_URL}/tts/"
        try:
            resp = requests.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
