document.addEventListener("DOMContentLoaded", () => {

  const $ = sel => document.querySelector(sel);
  const dniInput  = $("#dni-input");
  let   personaNombre = "";      // cache del nombre devuelto por el backend
  let   countdownId   = null;    // para limpiar contadores

  /* gestión de pantallas */
  const show = id => {
    document.querySelectorAll(".pantalla").forEach(p => p.classList.remove("activa"));
    $(id).classList.add("activa");
  };

  /* teclado numérico */
  document.querySelectorAll(".key.num").forEach(btn => {
    btn.onclick = () => {
      if (dniInput.value.length < 8) {          // máximo 8 dígitos
        dniInput.value += btn.dataset.num;
      }
      toggleOk();
    };
  });
  $("#back").onclick  = () => { dniInput.value = dniInput.value.slice(0, -1); toggleOk(); };
  $("#clear").onclick = () => { dniInput.value = "";              toggleOk(); };
  const toggleOk      = () => $("#dni-ok").disabled = dniInput.value.length !== 8;

  /* confirmar DNI → validar y traer nombre */
  $("#dni-ok").onclick = () => {
    const dniNum = parseInt(dniInput.value, 10);

    fetch("/api/personas/buscar/", {
      method: "POST",
      headers: {"Content-Type":"application/json", "X-CSRFToken": csrftoken},
      body: JSON.stringify({dni: dniNum})
    })
    .then(async r => {
      const data = await r.json();
      if (!r.ok) throw data.detail || "Error";
      return data;
    })
    .then(datos => {
      personaNombre = `${datos.apellido}, ${datos.nombre}`;
      /* ahora traemos categorías y pasamos a pantalla 2 */
      return fetch("/turnos/categorias.json");
    })
    .then(r => r.json())
    .then(renderCategorias)
    .then(() => show("#pantalla-cat"))
    .catch(alert);
  };

  /* render dinámico de categorías */
  function renderCategorias(lista){
    const cont = $("#cat-container");
    cont.innerHTML = "";
    lista.forEach(cat => {
      cont.insertAdjacentHTML("beforeend",
        `<div class="col-12 col-md-6">
           <button class="btn categoria-btn w-100" data-id="${cat.id}">${cat.nombre}</button>
         </div>`);
    });
    cont.querySelectorAll(".categoria-btn").forEach(btn => {
      btn.onclick = () => confirmarTurno(btn.dataset.id, btn.textContent);
    });
  }

  $("#cat-back").onclick = () => show("#pantalla-dni");

  /* confirmación: emitir turno */
  function confirmarTurno(catId, catNombre){
    const payload = { categoria_id: catId, dni: parseInt(dniInput.value, 10) };

    fetch("/api/turnos/emitir/", {
      method: "POST",
      headers: {"Content-Type":"application/json", "X-CSRFToken": csrftoken},
      body: JSON.stringify(payload)
    })
    .then(async r => {
      const data = await r.json();
      if (!r.ok) throw data.detail || "Error";
      return data;
    })
    .then(data => {
      mostrarPantallaOK(data.nombre, data.categoria, data.espera, 15);
      show("#pantalla-ok");
    })
    .catch(alert);
  }

  /* botones pantalla OK */
  $("#otro-btn").onclick = () => show("#pantalla-cat");
  $("#salir-btn").onclick = resetAll;

  /* util */
  function resetAll(){
    if (countdownId) { clearInterval(countdownId); countdownId = null; }
    dniInput.value = "";
    personaNombre  = "";
    toggleOk();
    show("#pantalla-dni");
  }

  /* contador y relleno */
  function mostrarPantallaOK(nombre, categoria, espera, segundos=15){
    $("#ok-nombre").textContent = nombre;
    $("#ok-cat").textContent    = categoria;
    $("#ok-espera").innerHTML   =
      `Tiene <strong>${espera}</strong> persona(s) en espera antes que usted.`;

    const c = $("#ok-countdown"), n=$("#count-num");
    let t = segundos;
    c.classList.remove("visually-hidden");
    n.textContent = t;

    if (countdownId) clearInterval(countdownId);
    countdownId = setInterval(()=>{
      n.textContent = --t;
      if (t<=0){
        clearInterval(countdownId);
        countdownId = null;
        resetAll();
      }
    },1000);
  }
});
