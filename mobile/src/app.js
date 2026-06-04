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
    logout();
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
