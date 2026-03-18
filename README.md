# 🎙️ Fatou BRAVO — Générateur de Voix Wolof
### Application Django · Powered by LAfricaMobile TTS API

---

## 📋 Description
Application web Django permettant de :
1. **Traduire** du texte français en Wolof via l'API LAfricaMobile
2. **Synthétiser** un texte Wolof en fichier audio (voix naturelle)
3. **Pipeline complet** : Français → Wolof → Audio en 1 clic
4. **Consulter** l'historique des générations

---

## 🚀 Installation

### 1. Cloner et installer
```bash
cd fatou_tts
pip install -r requirements.txt
```

### 2. Configurer les credentials LAfricaMobile
Créer un fichier `.env` à la racine du projet :
```env
LAM_LOGIN=votre_login_lafricamobile
LAM_PASSWORD=votre_password_lafricamobile
```
Ou définir les variables d'environnement directement :
```bash
export LAM_LOGIN="votre_login"
export LAM_PASSWORD="votre_password"
```

> **Obtenir un compte** : Inscription sur https://monespace.lafricamobile.com/register
> Pour l'URL de production, contacter : assistance@lafricamobile.com

### 3. Lancer le serveur
```bash
python manage.py runserver
```
Ouvrir : http://localhost:8000

---

## 🔌 Endpoints API

| Méthode | URL | Description |
|---------|-----|-------------|
| `POST` | `/api/generate/` | Pipeline complet : FR → Wolof → Audio |
| `POST` | `/api/translate/` | Traduction français → Wolof uniquement |
| `POST` | `/api/synthesize/` | Synthèse vocale d'un texte Wolof |
| `GET`  | `/api/history/` | Historique des requêtes TTS |

### Exemples de requêtes

**Pipeline complet (recommandé)**
```bash
curl -X POST http://localhost:8000/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour tout le monde, je suis Fatou BRAVO.", "pitch": 0.0, "speed": 1.0}'
```

**Traduction seule**
```bash
curl -X POST http://localhost:8000/api/translate/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Les produits BRAVO sont bons pour toute la famille."}'
```

**Synthèse seule (texte Wolof déjà traduit)**
```bash
curl -X POST http://localhost:8000/api/synthesize/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Maa ngi tudd Fatou BRAVO", "pitch": 0.2, "speed": 0.9}'
```

---

## 📦 Structure du projet

```
fatou_tts/
├── manage.py
├── requirements.txt
├── .env                          ← À créer (credentials LAM)
├── fatou_tts/
│   ├── settings.py               ← Configuration Django + LAM
│   └── urls.py
└── tts_app/
    ├── services.py               ← Client API LAfricaMobile
    ├── views.py                  ← Vues Django (API endpoints)
    ├── urls.py                   ← Routes
    └── templates/tts_app/
        └── index.html            ← Interface web
```

---

## 🎛️ Paramètres audio

| Paramètre | Défaut | Plage | Description |
|-----------|--------|-------|-------------|
| `pitch` | `0.0` | `-2.0` à `+2.0` | Tonalité de la voix (+ = plus aigu) |
| `speed` | `1.0` | `0.5` à `2.0` | Vitesse de parole (+ = plus rapide) |
| `to_lang` | `wo` | — | Code ISO Wolof (fixé automatiquement) |

---

## 🔗 API LAfricaMobile — Référence

Documentation officielle : https://developers.lafricamobile.com/docs/tts/introduction

| Endpoint LAM | Méthode | Description |
|---|---|---|
| `/auth/login` | POST | Authentification OAuth2 → Bearer token |
| `/tts/` | POST | Pipeline FR → Wolof → Audio |
| `/tts/translate` | POST | Traduction uniquement (max 512 chars) |
| `/tts/vocalize` | POST | Synthèse vocale uniquement |
| `/tts/` | GET | Historique des requêtes |

---

## 🌍 Langues supportées par LAfricaMobile TTS
- **Wolof** (`wo`) ← utilisé dans cette app
- Bambara, Lingala, Dioula et autres langues africaines

---

## 📞 Support
- LAfricaMobile : assistance@lafricamobile.com
- Doc API : https://developers.lafricamobile.com
