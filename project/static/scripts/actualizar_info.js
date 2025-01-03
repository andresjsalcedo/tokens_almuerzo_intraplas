function updateEmployeeInfo(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);

    fetch('/actualizar_empleado', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            window.location.reload();
        } else {
            alert('Error al actualizar empleado');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al actualizar empleado');
    });
}