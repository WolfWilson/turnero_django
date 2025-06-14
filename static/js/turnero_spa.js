document.addEventListener("DOMContentLoaded", () => {

  /* helpers */
  const $ = sel => document.querySelector(sel);
  const dniInput = $("#dni-input");

  /*  gestión de pantallas  */
  const show = id => {
    document.querySelectorAll(".pantalla").forEach(p => p.classList.remove("activa"));
    $(id).classList.add("activa");
  };

  /*  teclado numérico  */
  document.querySelectorAll(".key.num").forEach(btn => {
    btn.onclick = () => { dniInput.value += btn.dataset.num; toggleOk(); };
  });
  $("#back").onclick  = () => { dniInput.value = dniInput.value.slice(0, -1); toggleOk(); };
  $("#clear").onclick = () => { dniInput.value = "";              toggleOk(); };
  const toggleOk      = () => $("#dni-ok").disabled = dniInput.value.length < 7;

  /*  paso a categorías  */
  $("#dni-ok").onclick = () => {
    fetch("/turnos/categorias.json")
      .then(r => r.json())
      .then(renderCategorias);
    show("#pantalla-cat");
  };

  /*  render dinámico de categorías  */
  function renderCategorias(lista){
    const cont = $("#cat-container");
    cont.innerHTML = "";
    lista.forEach(cat => {
      const col = document.createElement("div");
      col.className = "col-12 col-md-6";
      col.innerHTML =
        `<button class="btn categoria-btn w-100" data-id="${cat.id}">${cat.nombre}</button>`;
      cont.appendChild(col);
    });
    cont.querySelectorAll(".categoria-btn").forEach(btn => {
      btn.onclick = () => confirmarTurno(btn.dataset.id, btn.textContent);
    });
  }

  $("#cat-back").onclick = () => show("#pantalla-dni");

  /*  confirmación  */
  function confirmarTurno(catId, catNombre){
    const espera = Math.floor(Math.random()*4) + 1;   // simulación cola

    mostrarPantallaOK(
      dniInput.value,      // sustituye por el nombre cuando esté disponible
      catNombre,
      espera,
      15                   // segundos antes de volver
    );

    show("#pantalla-ok");
  }

  /*  botones pantalla OK  */
  $("#otro-btn").onclick = () => show("#pantalla-cat");
  $("#salir-btn").onclick = resetAll;

  /*  util  */
  function resetAll(){
    dniInput.value = "";
    toggleOk();
    show("#pantalla-dni");
  }

  /* ========= función contador + relleno ========= */
  function mostrarPantallaOK(nombre, categoria, personasEnEspera, segundosAuto = 15){

    $("#ok-nombre").textContent  = nombre;
    $("#ok-cat").textContent     = categoria;
    $("#ok-espera").innerHTML    =
      `Tiene <strong>${personasEnEspera}</strong> persona(s) en espera antes que usted.`;

    /* contador */
    const countdownEl = $("#ok-countdown");
    const numEl       = $("#count-num");
    let   tiempo      = segundosAuto;

    countdownEl.classList.remove("visually-hidden");
    numEl.textContent = tiempo;

    const t = setInterval(() => {
      tiempo--;
      numEl.textContent = tiempo;
      if (tiempo <= 0){
        clearInterval(t);
        resetAll();                    // vuelve a la pantalla inicial
      }
    }, 1000);
  }
});
