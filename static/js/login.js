// Lista de rutas de imágenes disponibles (ajustá según tengas más)
const bgImages = [
    "/static/media/login/bg.jpg",
    "/static/media/login/bg1.jpg",
    "/static/media/login/bg2.jpg",
    "/static/media/login/bg3.jpg"
  ];
  
  // Elementos
  const loginBg = document.getElementById("login-bg");
  const btnShuffle = document.getElementById("btn-random-bg");
  const btnPin = document.getElementById("btn-pin-bg");
  const pinIcon = document.getElementById("pin-icon");
  
  // Devuelve la imagen a cargar al iniciar (favorito o aleatorio)
  function getInitialBackground() {
    const pinned = localStorage.getItem("pinnedBg");
    return pinned && bgImages.includes(pinned)
      ? pinned
      : bgImages[Math.floor(Math.random() * bgImages.length)];
  }
  
  // Aplica el fondo y actualiza el estado visual
  function setBackground(imgPath) {
    loginBg.style.backgroundImage = `url('${imgPath}')`;
    loginBg.setAttribute("data-current", imgPath);
  
    const pinned = localStorage.getItem("pinnedBg");
  
    if (pinned === imgPath) {
      pinIcon.textContent = "push_pin";
      pinIcon.style.color = "limegreen"; // Fondo fijado → verde
    } else {
      pinIcon.textContent = "push_pin";
      pinIcon.style.color = ""; // Reset color
    }
  }
  
  // Cambia el fondo por uno nuevo al azar
  btnShuffle.addEventListener("click", () => {
    const current = loginBg.getAttribute("data-current");
    let random = current;
  
    while (random === current && bgImages.length > 1) {
      random = bgImages[Math.floor(Math.random() * bgImages.length)];
    }
  
    setBackground(random);
  });
  
  // Alterna el fondo fijado
  btnPin.addEventListener("click", () => {
    const current = loginBg.getAttribute("data-current");
    const pinned = localStorage.getItem("pinnedBg");
  
    if (pinned === current) {
      localStorage.removeItem("pinnedBg");
    } else {
      localStorage.setItem("pinnedBg", current);
    }
  
    setBackground(current);
  });
  
  // Inicialización
  setBackground(getInitialBackground());
  