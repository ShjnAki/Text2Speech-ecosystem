"""
API REST TTS — FastAPI
======================
Déploiement sur VPS Contabo (Debian) avec systemd.

Démarrage manuel (dev) :
    cd api && source .venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Démarrage production (systemd) :
    sudo systemctl start tts-api
"""
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from auth import verify_user, create_access_token, decode_access_token, AuthError
from tts import generate_tts_audio, TTSError

app = FastAPI(title="TTS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["Authorization", "Content-Type"],
)

security = HTTPBearer(auto_error=False)


# ─── Schémas ──────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class TTSRequest(BaseModel):
    text: str


# ─── Dépendance d'authentification ────────────────────────────────────────────

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extrait et valide le token JWT depuis le header Authorization."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
        return payload["sub"]
    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.post("/auth/login")
def login(request: LoginRequest):
    """Authentifie un utilisateur et retourne un token JWT."""
    if not verify_user(request.email, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = create_access_token(request.email)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/tts")
def text_to_speech(request: TTSRequest, current_user: str = Depends(get_current_user)):
    """Convertit du texte en audio MP3 via Google Cloud TTS."""
    try:
        audio_bytes = generate_tts_audio(request.text)
    except TTSError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response(content=audio_bytes, media_type="audio/mpeg")
