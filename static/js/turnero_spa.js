document.addEventListener("DOMContentLoaded", () => {
  /* helpers */
  const $ = (sel)=>document.querySelector(sel);
  const dniInput=$("#dni-input");

  /* gestión pantallas */
  const show=(id)=>{
    document.querySelectorAll(".pantalla").forEach(p=>p.classList.remove("activa"));
    $(id).classList.add("activa");
  };

  /* TECLADO NUMÉRICO */
  document.querySelectorAll(".key.num").forEach(btn=>{
    btn.onclick=()=>{ dniInput.value += btn.dataset.num; toggleOk(); };
  });
  $("#back").onclick=()=>{ dniInput.value=dniInput.value.slice(0,-1); toggleOk(); };
  $("#clear").onclick=()=>{ dniInput.value=""; toggleOk(); };
  const toggleOk=()=>$("#dni-ok").disabled = dniInput.value.length<7;

  /* DNI confirmado → a categorías */
  $("#dni-ok").onclick=()=>{
    fetch("/turnos/categorias.json")
      .then(r=>r.json())
      .then(renderCategorias);
    show("#pantalla-cat");
  };

  /* Render dinámico de categorías */
  function renderCategorias(lista){
    const cont = $("#cat-container");
    cont.innerHTML="";
    lista.forEach(cat=>{
      const col=document.createElement("div");
      col.className="col-12 col-md-6";
      col.innerHTML=`<button class="btn categoria-btn w-100" data-id="${cat.id}">${cat.nombre}</button>`;
      cont.appendChild(col);
    });
    // listeners botón
    cont.querySelectorAll(".categoria-btn").forEach(btn=>{
      btn.onclick=()=>confirmarTurno(btn.dataset.id, btn.textContent);
    });
  }

  $("#cat-back").onclick=()=>show("#pantalla-dni");

  /* Confirmación */
  function confirmarTurno(catId,catNombre){
    // TODO: POST al endpoint Django para crear turno y devolver posición en cola
    // Simulación rápida:
    const espera=Math.floor(Math.random()*4)+1;
    $("#ok-nombre").textContent=dniInput.value;
    $("#ok-cat").textContent=`Turno confirmado para ${catNombre}`;
    $("#ok-espera").innerHTML=`Tiene <strong>${espera}</strong> persona(s) en espera antes que usted.`;

    show("#pantalla-ok");
    // timeout auto-reset
    setTimeout(resetAll, 10000);
  }

  /* botones pantalla OK */
  $("#otro-btn").onclick=()=>{
    show("#pantalla-cat");
  };
  $("#salir-btn").onclick=resetAll;

  function resetAll(){
    dniInput.value="";
    toggleOk();
    show("#pantalla-dni");
  }
});
// Fin del script