function actualizarContador() {
    fetch('/api/total-usuarios')
        .then(response => response.json())
        .then(data => {
            document.getElementById('contador-usuarios').textContent = data.total;
        })
        .catch(error => console.error('Error:', error));
}

// Actualizar cada 30 segundos
setInterval(actualizarContador, 30000);