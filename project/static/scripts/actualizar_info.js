function updateEmployeeInfo(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    fetch('/actualizar_empleado', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.reload();
        } else {
            alert('Error al actualizar la información');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al actualizar la información');
    });
}