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

let ingredientes = [];
let categorias = [];

document.getElementById('agregarIngrediente').addEventListener('click', function(event) {
    event.preventDefault();
    
    let ingrediente = document.getElementById('ingrediente').value;
    let cantidad = document.getElementById('cantidad').value;
    
    if (ingrediente && cantidad) {
        ingredientes.push(`${cantidad} de ${ingrediente}`);
        
        document.getElementById('listaIngredientes').value = ingredientes.join(', ');

        document.getElementById('ingrediente').value = '';
        document.getElementById('cantidad').value = '';
    }
});

document.getElementById('agregarCategoria').addEventListener('click', function(event) {
    event.preventDefault();
    
    let select = document.getElementById('categorias');
    let categoriaTexto = select.options[select.selectedIndex].text;

        if (categoriaTexto) {
            categorias.push(categoriaTexto);
            document.getElementById('listaCategorias').value = categorias.join(', ');
            document.getElementById('categorias').selectedIndex = 0;
        }
    });
