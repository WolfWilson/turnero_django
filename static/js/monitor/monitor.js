// static/js/monitor.js
(() => {
  /* === Reloj ======================================================= */
  const clock = document.getElementById("clock");
  const tick  = () =>
    clock.textContent = new Date().toLocaleTimeString("es-AR",
      {hour:"2-digit",minute:"2-digit",second:"2-digit"});
  tick(); setInterval(tick, 1000);

  /* === Overlay de aviso =========================================== */
  const overlay  = document.getElementById("alert-overlay");
  const wrapper  = document.getElementById("alert-wrapper");
  let hideTimer  = null;

  /**
   * Muestra los turnos llamados.
   * @param {Array<{nombre:string, box:number}>} data
   */
  function showAlert(data){
    // Limpia y crea tarjetas
    wrapper.innerHTML = "";
    data.slice(0,4).forEach(t => {
      const card = document.createElement("article");
      card.className = "alert-card";
      card.innerHTML = `
        <span class="material-icons-outlined bell">notifications_active</span>
        <div class="info">
          <span class="name">${t.nombre}</span>
          <span class="box">BOX&nbsp;${t.box}</span>
        </div>`;
      wrapper.appendChild(card);
    });

    // Muestra overlay
    overlay.classList.add("show");
    overlay.hidden = false;

    // Reinicia temporizador
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(hideAlert, 10000); // 10 s
  }

  function hideAlert(){
    overlay.classList.remove("show");
    // Espera transición CSS antes de ocultar del flujo
    setTimeout(() => overlay.hidden = true, 500);
  }

  /* === Wire de demo (quitar en producción) ========================= */
  document.getElementById("demo-call").addEventListener("click", () => {
    showAlert([
      {nombre:"PÉREZ, ANA", box:2},
      {nombre:"BENITEZ, JOSE", box:5}
    ]);
  });

  /* === Integración futura con WebSockets ========================== *
     Ejemplo (pseudo-código):
     const ws = new WebSocket("wss://…/monitor/");
     ws.onmessage = e => {
       const msg = JSON.parse(e.data);
       if (msg.type === "call") showAlert(msg.turnos);
       if (msg.type === "list")  updateList(msg.turnos);
     };
  */

  /* ===== Refresco de lista (placeholder para REST polling) ======== */
  // async function updateListRemote(){
  //   const html = await (await fetch("{% url 'turnos:api-monitor' %}")).text();
  //   document.getElementById("turn-container").innerHTML = html;
  // }
  // setInterval(updateListRemote, 8000);
})();
