# TTS App Mobile Capacitor — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Application mobile légère (HTML/CSS/JS vanilla + Capacitor) permettant aux collaborateurs de convertir du texte en audio MP3 via l'API TTS — distribuée via APK généré automatiquement par GitHub Actions.

**Architecture:** SPA deux-écrans (login → app principale). Authentification JWT stockée dans `localStorage`. Appels directs à l'API TTS via `fetch`. Lecture audio via `<audio>` HTML natif. Capacitor encapsule le tout en APK Android.

**Tech Stack:** HTML/CSS/JS vanilla, Capacitor 6+, Node 20+, GitHub Actions (ubuntu-latest)

**Prérequis :** L'API REST (plan `2026-06-04-api-rest.md`) doit être déployée et accessible depuis le mobile (même réseau ou URL publique).

---

## Structure des fichiers

```
mobile/
├── src/
│   ├── index.html    # Écran de login
│   ├── app.html      # Écran principal (après login)
│   ├── style.css     # Styles globaux (sans framework)
│   ├── config.js     # URL de l'API (à modifier avant déploiement)
│   ├── auth.js       # Gestion login / token JWT / déconnexion
│   └── app.js        # Logique TTS + lecture fichiers + lecteur audio
├── capacitor.config.json
├── package.json
└── .github/
    └── workflows/
        └── build-apk.yml
```

---

## Tâche 1 : Setup Capacitor

**Fichiers :**
- Créer : `mobile/package.json`
- Créer : `mobile/capacitor.config.json`

- [ ] **Étape 1 : Créer `mobile/package.json`**

```json
{
  "name": "tts-mobile",
  "version": "1.0.0",
  "description": "Application mobile TTS pour collaborateurs",
  "scripts": {
    "build": "echo 'No build step - vanilla HTML/CSS/JS'",
    "cap:sync": "npx cap sync",
    "cap:open:android": "npx cap open android"
  },
  "dependencies": {
    "@capacitor/android": "^6.0.0",
    "@capacitor/core": "^6.0.0",
    "@capacitor/filesystem": "^6.0.0"
  },
  "devDependencies": {
    "@capacitor/cli": "^6.0.0"
  }
}
```

- [ ] **Étape 2 : Créer `mobile/capacitor.config.json`**

```json
{
  "appId": "com.tts.mobile",
  "appName": "TTS Mobile",
  "webDir": "src",
  "server": {
    "androidScheme": "https"
  },
  "android": {
    "allowMixedContent": true
  }
}
```

Note : `allowMixedContent: true` est nécessaire tant que l'API n'est pas en HTTPS. À désactiver après passage en HTTPS.

- [ ] **Étape 3 : Installer les dépendances**

```bash
cd mobile && npm install
```

- [ ] **Étape 4 : Commit**

```bash
git add mobile/package.json mobile/capacitor.config.json
git commit -m "chore(mobile): setup Capacitor 6 et configuration Android"
```

---

## Tâche 2 : Configuration et styles

**Fichiers :**
- Créer : `mobile/src/config.js`
- Créer : `mobile/src/style.css`

- [ ] **Étape 1 : Créer `mobile/src/config.js`**

```js
// Remplacer IP_VPS par l'adresse IP réelle du serveur, ou le domaine quand disponible
// Exemple : "http://192.168.1.100:8000" ou "https://api.tondomaine.com"
export const API_URL = "http://IP_VPS:8000";
```

- [ ] **Étape 2 : Créer `mobile/src/style.css`**

```css
/* Reset et base */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --couleur-fond: #0f172a;
  --couleur-surface: #1e293b;
  --couleur-bordure: #334155;
  --couleur-primaire: #6366f1;
  --couleur-primaire-hover: #818cf8;
  --couleur-texte: #f1f5f9;
  --couleur-texte-secondaire: #94a3b8;
  --couleur-erreur: #ef4444;
  --couleur-succes: #22c55e;
  --couleur-avertissement: #f59e0b;
  --radius: 12px;
  --radius-sm: 8px;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--couleur-fond);
  color: var(--couleur-texte);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Écran centré (login) */
.ecran-centré {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

/* Carte */
.carte {
  background: var(--couleur-surface);
  border: 1px solid var(--couleur-bordure);
  border-radius: var(--radius);
  padding: 32px 24px;
  width: 100%;
  max-width: 400px;
}

.carte h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
  text-align: center;
}

.carte .sous-titre {
  font-size: 0.875rem;
  color: var(--couleur-texte-secondaire);
  text-align: center;
  margin-bottom: 28px;
}

/* Formulaires */
.groupe-champ {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--couleur-texte-secondaire);
}

input[type="email"],
input[type="password"],
textarea {
  background: var(--couleur-fond);
  border: 1px solid var(--couleur-bordure);
  border-radius: var(--radius-sm);
  color: var(--couleur-texte);
  font-size: 1rem;
  padding: 12px 14px;
  width: 100%;
  transition: border-color 0.2s;
  outline: none;
}

input:focus, textarea:focus {
  border-color: var(--couleur-primaire);
}

textarea {
  resize: vertical;
  min-height: 140px;
  font-family: inherit;
}

/* Boutons */
.btn {
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  padding: 12px 20px;
  transition: background 0.2s, opacity 0.2s;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primaire {
  background: var(--couleur-primaire);
  color: #fff;
}
.btn-primaire:hover:not(:disabled) { background: var(--couleur-primaire-hover); }

.btn-secondaire {
  background: transparent;
  border: 1px solid var(--couleur-bordure);
  color: var(--couleur-texte-secondaire);
  font-size: 0.875rem;
}
.btn-secondaire:hover:not(:disabled) { border-color: var(--couleur-primaire); color: var(--couleur-texte); }

/* Messages */
.message {
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  margin-top: 12px;
  padding: 10px 14px;
  display: none;
}
.message.visible { display: block; }
.message.erreur { background: #450a0a; border: 1px solid var(--couleur-erreur); color: var(--couleur-erreur); }
.message.succes { background: #052e16; border: 1px solid var(--couleur-succes); color: var(--couleur-succes); }

/* Layout app principale */
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background: var(--couleur-surface);
  border-bottom: 1px solid var(--couleur-bordure);
  padding: 14px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-header h1 { font-size: 1.125rem; font-weight: 700; }

.app-body {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 640px;
  margin: 0 auto;
  width: 100%;
}

/* Compteur de caractères */
.compteur {
  font-size: 0.8rem;
  color: var(--couleur-texte-secondaire);
  text-align: right;
  margin-top: 4px;
  transition: color 0.2s;
}
.compteur.avertissement { color: var(--couleur-avertissement); font-weight: 600; }

/* Lecteur audio */
.lecteur-audio {
  background: var(--couleur-surface);
  border: 1px solid var(--couleur-bordure);
  border-radius: var(--radius);
  padding: 16px;
  display: none;
}
.lecteur-audio.visible { display: block; }
.lecteur-audio audio { width: 100%; margin-top: 8px; }

/* Spinner — caché par défaut, affiché via JS (style.display) sans innerHTML */
.btn-spinner {
  display: none;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive (desktop) */
@media (min-width: 640px) {
  .app-body { padding: 32px 24px; }
}
```

- [ ] **Étape 3 : Commit**

```bash
git add mobile/src/config.js mobile/src/style.css
git commit -m "feat(mobile): configuration API et styles CSS globaux"
```

---

## Tâche 3 : Logique d'authentification

**Fichiers :**
- Créer : `mobile/src/auth.js`

- [ ] **Étape 1 : Créer `mobile/src/auth.js`**

```js
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
```

- [ ] **Étape 2 : Commit**

```bash
git add mobile/src/auth.js
git commit -m "feat(mobile): logique auth JWT (login/logout/persistance localStorage)"
```

---

## Tâche 4 : Écran de login

**Fichiers :**
- Créer : `mobile/src/index.html`

- [ ] **Étape 1 : Créer `mobile/src/index.html`**

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>TTS Mobile — Connexion</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="ecran-centré">
    <div class="carte">
      <h1>TTS Mobile</h1>
      <p class="sous-titre">Connectez-vous pour accéder à la synthèse vocale</p>

      <form id="formulaire-login" novalidate>
        <div class="groupe-champ">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            placeholder="vous@example.com"
            autocomplete="email"
            required
          >
        </div>

        <div class="groupe-champ">
          <label for="mot-de-passe">Mot de passe</label>
          <input
            type="password"
            id="mot-de-passe"
            name="mot-de-passe"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          >
        </div>

        <button type="submit" class="btn btn-primaire" id="btn-connexion">
          <span class="btn-spinner" aria-hidden="true"></span>
          <span class="btn-texte">Se connecter</span>
        </button>
      </form>

      <div class="message erreur" id="message-erreur"></div>
    </div>
  </div>

  <script type="module">
    import { login, estConnecte } from './auth.js';

    // Redirection automatique si déjà connecté
    if (estConnecte()) {
      window.location.href = 'app.html';
    }

    const formulaire = document.getElementById('formulaire-login');
    const btnConnexion = document.getElementById('btn-connexion');
    const spinnerConnexion = btnConnexion.querySelector('.btn-spinner');
    const labelConnexion = btnConnexion.querySelector('.btn-texte');
    const messageErreur = document.getElementById('message-erreur');

    function afficherErreur(texte) {
      messageErreur.textContent = texte;
      messageErreur.classList.add('visible');
    }

    function cacherErreur() {
      messageErreur.classList.remove('visible');
    }

    function setChargement(chargement) {
      btnConnexion.disabled = chargement;
      spinnerConnexion.style.display = chargement ? 'inline-block' : 'none';
      labelConnexion.textContent = chargement ? 'Connexion...' : 'Se connecter';
    }

    formulaire.addEventListener('submit', async (e) => {
      e.preventDefault();
      cacherErreur();

      const email = document.getElementById('email').value.trim();
      const motDePasse = document.getElementById('mot-de-passe').value;

      if (!email || !motDePasse) {
        afficherErreur('Veuillez remplir tous les champs.');
        return;
      }

      setChargement(true);

      try {
        await login(email, motDePasse);
        window.location.href = 'app.html';
      } catch (err) {
        afficherErreur(err.message);
      } finally {
        setChargement(false);
      }
    });
  </script>
</body>
</html>
```

- [ ] **Étape 2 : Commit**

```bash
git add mobile/src/index.html
git commit -m "feat(mobile): écran de login avec redirection JWT automatique"
```

---

## Tâche 5 : Logique de l'app principale

**Fichiers :**
- Créer : `mobile/src/app.js`

- [ ] **Étape 1 : Créer `mobile/src/app.js`**

```js
import { API_URL } from './config.js';
import { getToken, logout } from './auth.js';

const MAX_CHARS = 2500;

/**
 * Envoie le texte à l'API TTS et retourne un Blob audio.
 * @param {string} texte
 * @returns {Promise<Blob>}
 */
export async function genererAudio(texte) {
  const token = getToken();
  const response = await fetch(`${API_URL}/tts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ text: texte }),
  });

  if (response.status === 401) {
    logout(); // Token expiré → redirection login
    throw new Error('Session expirée. Reconnexion...');
  }

  if (response.status === 400) {
    const data = await response.json();
    throw new Error(data.detail || 'Texte invalide.');
  }

  if (!response.ok) {
    throw new Error(`L'API est indisponible (erreur ${response.status}). Vérifiez votre connexion.`);
  }

  return await response.blob();
}

/**
 * Lit un fichier .txt ou .md depuis un objet File et retourne le contenu texte.
 * @param {File} fichier
 * @returns {Promise<string>}
 */
export function lireFichier(fichier) {
  return new Promise((resolve, reject) => {
    const ext = fichier.name.split('.').pop().toLowerCase();
    if (!['txt', 'md'].includes(ext)) {
      reject(new Error(`Format non supporté : .${ext}. Accepté : .txt, .md`));
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target.result);
    reader.onerror = () => reject(new Error('Impossible de lire le fichier.'));
    reader.readAsText(fichier, 'utf-8');
  });
}

// ─── Interface utilisateur ────────────────────────────────────────────────────

const textarea = document.getElementById('textarea-texte');
const compteur = document.getElementById('compteur-chars');
const btnFichier = document.getElementById('btn-charger-fichier');
const inputFichier = document.getElementById('input-fichier');
const btnEcouter = document.getElementById('btn-ecouter');
const spinnerEcouter = btnEcouter.querySelector('.btn-spinner');
const labelEcouter = btnEcouter.querySelector('.btn-texte');
const lecteurAudio = document.getElementById('lecteur-audio');
const elementAudio = document.getElementById('audio');
const messageErreur = document.getElementById('message-erreur');
const btnDeconnexion = document.getElementById('btn-deconnexion');

// Compteur de caractères
textarea.addEventListener('input', () => {
  const n = textarea.value.length;
  compteur.textContent = `${n} / ${MAX_CHARS} caractères`;
  compteur.classList.toggle('avertissement', n > MAX_CHARS);
  btnEcouter.disabled = n > MAX_CHARS || n === 0;
});

// Bouton "Charger un fichier"
btnFichier.addEventListener('click', () => inputFichier.click());
inputFichier.addEventListener('change', async () => {
  const fichier = inputFichier.files[0];
  if (!fichier) return;
  try {
    const contenu = await lireFichier(fichier);
    textarea.value = contenu;
    textarea.dispatchEvent(new Event('input'));
    cacherErreur();
  } catch (err) {
    afficherErreur(err.message);
  }
  inputFichier.value = '';
});

// Bouton "Écouter" — état de chargement géré via DOM, pas innerHTML
function setEcouterChargement(chargement) {
  btnEcouter.disabled = chargement;
  spinnerEcouter.style.display = chargement ? 'inline-block' : 'none';
  labelEcouter.textContent = chargement ? 'Génération...' : '▶ Écouter';
}

btnEcouter.addEventListener('click', async () => {
  const texte = textarea.value.trim();
  if (!texte) return;
  cacherErreur();

  setEcouterChargement(true);
  lecteurAudio.classList.remove('visible');

  try {
    const blob = await genererAudio(texte);
    const url = URL.createObjectURL(blob);
    elementAudio.src = url;
    lecteurAudio.classList.add('visible');
    elementAudio.play();
  } catch (err) {
    afficherErreur(err.message);
  } finally {
    setEcouterChargement(false);
  }
});

// Déconnexion
btnDeconnexion.addEventListener('click', logout);

function afficherErreur(texte) {
  messageErreur.textContent = texte;
  messageErreur.classList.add('visible');
}
function cacherErreur() {
  messageErreur.classList.remove('visible');
}
```

- [ ] **Étape 2 : Commit**

```bash
git add mobile/src/app.js
git commit -m "feat(mobile): logique TTS, lecture fichier et lecteur audio"
```

---

## Tâche 6 : Écran principal

**Fichiers :**
- Créer : `mobile/src/app.html`

- [ ] **Étape 1 : Créer `mobile/src/app.html`**

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>TTS Mobile</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="app-layout">
    <!-- En-tête -->
    <header class="app-header">
      <h1>TTS Mobile</h1>
      <button class="btn btn-secondaire" id="btn-deconnexion" style="width:auto;padding:8px 14px;">
        Se déconnecter
      </button>
    </header>

    <!-- Corps -->
    <main class="app-body">
      <!-- Zone de texte -->
      <div class="groupe-champ">
        <label for="textarea-texte">Texte à lire</label>
        <textarea
          id="textarea-texte"
          placeholder="Collez ou saisissez le texte ici..."
          rows="7"
        ></textarea>
        <div class="compteur" id="compteur-chars">0 / 2500 caractères</div>
      </div>

      <!-- Boutons d'action -->
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <button class="btn btn-secondaire" id="btn-charger-fichier" style="flex:1;min-width:140px;">
          Charger un fichier
        </button>
        <button class="btn btn-primaire" id="btn-ecouter" disabled style="flex:2;min-width:140px;">
          <span class="btn-spinner" aria-hidden="true"></span>
          <span class="btn-texte">▶ Écouter</span>
        </button>
      </div>

      <!-- Input fichier caché -->
      <input type="file" id="input-fichier" accept=".txt,.md" style="display:none;">

      <!-- Message d'erreur -->
      <div class="message erreur" id="message-erreur"></div>

      <!-- Lecteur audio -->
      <div class="lecteur-audio" id="lecteur-audio">
        <label style="font-size:0.875rem;color:var(--couleur-texte-secondaire);">Audio généré</label>
        <audio id="audio" controls></audio>
      </div>
    </main>
  </div>

  <script type="module">
    import { estConnecte } from './auth.js';
    // Redirection si non connecté
    if (!estConnecte()) {
      window.location.href = 'index.html';
    }
  </script>
  <script type="module" src="app.js"></script>
</body>
</html>
```

- [ ] **Étape 2 : Commit**

```bash
git add mobile/src/app.html
git commit -m "feat(mobile): écran principal avec textarea, compteur et lecteur audio"
```

---

## Tâche 7 : GitHub Actions — Build APK

**Fichiers :**
- Créer : `mobile/.github/workflows/build-apk.yml`

- [ ] **Étape 1 : Créer `.github/workflows/build-apk.yml`**

```yaml
name: Build APK

on:
  push:
    branches: [main]
    paths:
      - 'mobile/**'
  workflow_dispatch:  # Déclenchement manuel depuis GitHub Actions

jobs:
  build-apk:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout du code
        uses: actions/checkout@v4

      - name: Setup Java 17 (requis par Gradle/Android)
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Setup Node 20
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: mobile/package-lock.json

      - name: Installation des dépendances Node
        working-directory: mobile
        run: npm ci

      - name: Setup Android SDK
        uses: android-actions/setup-android@v3

      - name: Ajout de la plateforme Android dans Capacitor
        working-directory: mobile
        run: |
          npx cap add android || echo "Android déjà ajouté"
          npx cap sync android

      - name: Rendre gradlew exécutable
        working-directory: mobile/android
        run: chmod +x gradlew

      - name: Build APK (debug)
        working-directory: mobile/android
        run: ./gradlew assembleDebug --no-daemon

      - name: Upload APK en artifact
        uses: actions/upload-artifact@v4
        with:
          name: tts-mobile-debug.apk
          path: mobile/android/app/build/outputs/apk/debug/app-debug.apk
          retention-days: 30
```

- [ ] **Étape 2 : Ajouter `mobile/android/` dans .gitignore (il sera généré par CI)**

Le fichier `.gitignore` racine contient déjà `mobile/android/` et `mobile/ios/` — rien à faire.

- [ ] **Étape 3 : Commit**

```bash
git add mobile/.github/workflows/build-apk.yml
git commit -m "ci(mobile): GitHub Actions build APK Android sur push main"
```

---

## Tâche 8 : Initialisation Capacitor Android (locale — pour dev uniquement)

Cette étape est optionnelle pour le CI mais nécessaire pour tester sur un appareil physique.

- [ ] **Étape 1 : Ajouter la plateforme Android localement**

```bash
cd mobile
npx cap add android
npx cap sync android
```

Attendu : dossier `mobile/android/` créé (non versionné grâce au .gitignore).

- [ ] **Étape 2 : Ouvrir dans Android Studio (optionnel)**

```bash
npx cap open android
```

Puis dans Android Studio : Build → Generate Signed Bundle / APK.

- [ ] **Étape 3 : Commit (rien à ajouter — android/ est ignoré)**

Aucun commit nécessaire — le dossier android/ est dans .gitignore.

---

## Vérification finale (self-review)

- [x] Spec coverage : écran login, champ email+mdp, stockage JWT, redirection auto, déconnexion, textarea, bouton fichier (.txt/.md), compteur 2500 chars avec avertissement, bouton Écouter, indicateur de chargement, audio HTML natif, redirection 401→login, message erreur API, config.js, GitHub Actions APK artifact
- [x] Pas de placeholders
- [x] Noms cohérents : `getToken()`, `estConnecte()`, `login()`, `logout()` dans auth.js, `genererAudio()`, `lireFichier()` dans app.js — utilisés correctement dans les HTML
