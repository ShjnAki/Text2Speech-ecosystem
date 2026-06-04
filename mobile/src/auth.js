import { API_URL } from './config.js';

const CLE_TOKEN = 'tts_jwt_token';
const CLE_EXPIRATION = 'tts_jwt_expiration';

/**
 * Vérifie si un token JWT valide est stocké (non expiré).
 * @returns {boolean}
 */
export function estConnecte() {
  const token = localStorage.getItem(CLE_TOKEN);
  const expiration = localStorage.getItem(CLE_EXPIRATION);
  if (!token || !expiration) return false;
  return Date.now() < parseInt(expiration, 10);
}

/**
 * Retourne le token JWT stocké ou null.
 * @returns {string|null}
 */
export function getToken() {
  return localStorage.getItem(CLE_TOKEN);
}

/**
 * Effectue un appel POST /auth/login et stocke le token.
 * @param {string} email
 * @param {string} motDePasse
 * @throws {Error} si l'authentification échoue
 */
export async function login(email, motDePasse) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password: motDePasse }),
  });

  if (response.status === 401) {
    throw new Error('Email ou mot de passe incorrect.');
  }
  if (!response.ok) {
    throw new Error(`Erreur serveur (${response.status}). Réessayez plus tard.`);
  }

  const data = await response.json();
  // Stocker le token et calculer la date d'expiration (7 jours par défaut)
  const expiration = Date.now() + 7 * 24 * 60 * 60 * 1000;
  localStorage.setItem(CLE_TOKEN, data.access_token);
  localStorage.setItem(CLE_EXPIRATION, String(expiration));
}

/**
 * Supprime le token et redirige vers l'écran de login.
 */
export function logout() {
  localStorage.removeItem(CLE_TOKEN);
  localStorage.removeItem(CLE_EXPIRATION);
  window.location.href = 'index.html';
}
