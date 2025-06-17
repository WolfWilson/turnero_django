// Cierra la pestaña / redirige al monitor tras 10 s
setTimeout(() => {
  window.close();      // si se abrió con window.open(...)
  // o location.href = "{% url 'turnos:monitor' %}";
}, 10000);
