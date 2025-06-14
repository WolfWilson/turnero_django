document.addEventListener("DOMContentLoaded", () => {

  const $ = s => document.querySelector(s);
  const dniInput  = $("#dni-input");
  const dniAlert  = $("#dni-alert");

  let countdownId = null;

  /* helpers */
  const show      = id => { document.querySelectorAll(".pantalla").forEach(p=>p.classList.remove("activa")); $(id).classList.add("activa"); };
  const showAlert = (msg, type="danger") => {
      dniAlert.className = `alert alert-${type}`;      // color Bootstrap
      dniAlert.textContent = msg;
      dniAlert.classList.remove("d-none");
      setTimeout(()=>dniAlert.classList.add("d-none"), 6000); //desaparece en 6 segundos
  };

  /* teclado */
  document.querySelectorAll(".key.num").forEach(btn=>{
    btn.onclick = () => {
      if (dniInput.value.length < 8) dniInput.value += btn.dataset.num;
      toggleOk(); dniAlert.classList.add("d-none");
    };
  });
  $("#back").onclick  = () => { dniInput.value = dniInput.value.slice(0,-1); toggleOk(); };
  $("#clear").onclick = () => { dniInput.value = ""; toggleOk(); dniAlert.classList.add("d-none"); };
  const toggleOk      = () => $("#dni-ok").disabled = dniInput.value.length !== 8;

  /* confirmar DNI */
  $("#dni-ok").onclick = () => {
    fetch("/api/personas/buscar/", {
      method:"POST",
      headers:{"Content-Type":"application/json","X-CSRFToken":csrftoken},
      body:JSON.stringify({dni:parseInt(dniInput.value,10)})
    })
    .then(r=>r.json().then(d=>({ok:r.ok, data:d})))
    .then(({ok,data})=>{
        if(!ok) return Promise.reject(data.detail || "Error");
        personaNombre = `${data.apellido}, ${data.nombre}`;
        return fetch("/turnos/categorias.json").then(r=>r.json());
    })
    .then(renderCategorias)
    .then(()=>show("#pantalla-cat"))
    .catch(err=>showAlert(err,"warning"));
  };

  /* categorías */
  function renderCategorias(lista){
    const cont = $("#cat-container"); cont.innerHTML="";
    lista.forEach(cat=>cont.insertAdjacentHTML("beforeend",
      `<div class="col-12 col-md-6"><button class="btn categoria-btn w-100" data-id="${cat.id}">${cat.nombre}</button></div>`));
    cont.querySelectorAll(".categoria-btn").forEach(b=>b.onclick=()=>confirmarTurno(b.dataset.id,b.textContent));
  }
  $("#cat-back").onclick=()=>show("#pantalla-dni");

  /* emitir turno */
  function confirmarTurno(catId,catNombre){
    fetch("/api/turnos/emitir/",{
      method:"POST",
      headers:{"Content-Type":"application/json","X-CSRFToken":csrftoken},
      body:JSON.stringify({categoria_id:catId,dni:parseInt(dniInput.value,10)})
    })
    .then(r=>r.json().then(d=>({ok:r.ok,data:d})))
    .then(({ok,data})=>{
        if(!ok) return Promise.reject(data.detail||"Error");
        mostrarPantallaOK(data.nombre,data.categoria,data.espera,15);
        show("#pantalla-ok");
    })
    .catch(err=>showAlert(err,"warning"));
  }

  /* reset + contador limpio */
  $("#otro-btn").onclick = () => show("#pantalla-cat");
  $("#salir-btn").onclick = resetAll;
  function resetAll(){
    if(countdownId){clearInterval(countdownId);countdownId=null;}
    dniInput.value="";toggleOk();show("#pantalla-dni");
  }

  /* pantalla OK */
  function mostrarPantallaOK(nombre,categoria,espera,seg=15){
    $("#ok-nombre").textContent=nombre;
    $("#ok-cat").textContent=categoria;
    $("#ok-espera").innerHTML=`Tiene <strong>${espera}</strong> persona(s) en espera antes que usted.`;
    const c=$("#ok-countdown"),n=$("#count-num");let t=seg;
    c.classList.remove("visually-hidden");n.textContent=t;
    if(countdownId)clearInterval(countdownId);
    countdownId=setInterval(()=>{n.textContent=--t;if(t<=0){clearInterval(countdownId);countdownId=null;resetAll();}},1000);
  }
});
