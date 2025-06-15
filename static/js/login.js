/**
 * Fondos disponibles (bg.jpg + bg1…bg9.jpg)
 * Añade aquí más rutas si lo necesitas.
 */
const bgImages = Array.from({ length: 10 }, (_, i) =>
    i === 0
      ? "/static/media/login/bg.jpg"
      : `/static/media/login/bg${i}.jpg`
  );
  
  /* === Elementos clave === */
  const loginBg   = document.getElementById("login-bg");
  const loginBody = document.getElementById("login-body");
  const btnShuffle = document.getElementById("btn-random-bg");
  const btnPin     = document.getElementById("btn-pin-bg");
  const pinIcon    = document.getElementById("pin-icon");
  
  /* === Utilidades === */
  const LS_KEY = "pinnedBg";
  
  /* Pre-carga para evitar flashes */
  bgImages.forEach(src => new Image().src = src);
  
  /**
   * Devuelve un fondo inicial (favorito o aleatorio).
   */
  function pickInitialBackground() {
    const pinned = localStorage.getItem(LS_KEY);
    return pinned && bgImages.includes(pinned)
      ? pinned
      : bgImages[Math.floor(Math.random() * bgImages.length)];
  }
  
  /**
   * Aplica visualmente un fondo y refleja estado pin.
   */
  function applyBackground(src) {
    loginBg.style.backgroundImage = `url('${src}')`;
    loginBg.dataset.current = src;
  
    const isPinned = localStorage.getItem(LS_KEY) === src;
    pinIcon.textContent = isPinned ? "pin_end" : "push_pin";
    pinIcon.style.color = isPinned ? "limegreen" : ""; // fuerza color
    loginBody.classList.toggle("bg-pinned", isPinned); // mantiene la rotación
  }
  
  /**
   * Elige un fondo distinto aleatorio y lo aplica.
   */
  function shuffleBackground() {
    const current = loginBg.dataset.current;
    let candidate = current;
    while (candidate === current && bgImages.length > 1) {
      candidate = bgImages[Math.floor(Math.random() * bgImages.length)];
    }
    applyBackground(candidate);
  }
  
  /**
   * Alterna el fondo actual como pineado.
   */
  function togglePin() {
    const current = loginBg.dataset.current;
    const alreadyPinned = localStorage.getItem(LS_KEY) === current;
  
    if (alreadyPinned) {
      localStorage.removeItem(LS_KEY);
    } else {
      localStorage.setItem(LS_KEY, current);
    }
    applyBackground(current);
  }
  
  /* === Event listeners === */
  btnShuffle?.addEventListener("click", shuffleBackground);
  btnPin?.addEventListener("click", togglePin);
  
  /* === Inicialización === */
  document.addEventListener("DOMContentLoaded", () => {
    applyBackground(pickInitialBackground());
  });
  