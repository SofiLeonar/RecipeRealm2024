function mostrarFiltros(filtro) {
    const dietas = document.getElementById('filtros-dietas');
    const tipos = document.getElementById('filtros-tipos');
    const internacional = document.getElementById('filtros-internacional');

    const filtroSeleccionado = document.getElementById('filtros-' + filtro);

    if (!filtroSeleccionado.classList.contains('oculto')) {
        filtroSeleccionado.classList.add('oculto');
        return;
    }

    dietas.classList.add('oculto');
    tipos.classList.add('oculto');
    internacional.classList.add('oculto');

    filtroSeleccionado.classList.remove('oculto');
}

document.addEventListener('click', function(event) {
    const filtrosCuadro = document.querySelectorAll('.filtrosCuadro');
    const clickedElement = event.target;

    let clickedInsideFilter = false;
    
    filtrosCuadro.forEach(function(filtro) {
        if (filtro.contains(clickedElement)) {
            clickedInsideFilter = true;
        }
    });

    if (!clickedInsideFilter && !clickedElement.closest('.filtro')) {
        filtrosCuadro.forEach(function(filtro) {
            filtro.classList.add('oculto');
        });
    }
});
