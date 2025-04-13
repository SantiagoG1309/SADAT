$(document).ready(function() {
    function showToast(message, type = 'success') {
        const toast = $('<div>')
            .addClass('toast position-fixed bottom-0 end-0 m-3')
            .attr('role', 'alert')
            .attr('aria-live', 'assertive')
            .attr('aria-atomic', 'true');

        const toastBody = $('<div>')
            .addClass(`toast-body alert alert-${type} mb-0 d-flex align-items-center rounded`)
            .html(`<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>${message}`);

        toast.append(toastBody);
        $('body').append(toast);

        const bsToast = new bootstrap.Toast(toast[0], {
            autohide: true,
            delay: 3000
        });
        bsToast.show();

        toast.on('hidden.bs.toast', function () {
            toast.remove();
        });
    }

    // Función para obtener el token CSRF (copiada de cart.js para evitar dependencia)
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $('.add-to-cart-form').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const url = form.attr('action');
        const data = form.serialize();
        const productCard = form.closest('.card');
        const quantityInput = form.find('input[name="quantity"]');
        const stockDisplay = productCard.find('.stock-display');
        let currentStockText = stockDisplay.text().replace('Stock disponible: ', '');
        const currentStock = parseInt(currentStockText);
        const requestedQuantity = parseInt(quantityInput.val());

        if (isNaN(currentStock) || isNaN(requestedQuantity)) {
            showToast('Error: No se pudo determinar el stock o la cantidad.', 'danger');
            return;
        }

        if (requestedQuantity > currentStock) {
            showToast('La cantidad solicitada excede el stock disponible', 'danger');
            return;
        }
        
        const csrftoken = getCookie('csrftoken');
        if (!csrftoken) {
            showToast('Error: No se encontró el token CSRF. Asegúrate de estar autenticado.', 'danger');
            return;
        }

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            dataType: 'json',
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(response) {
                try {
                    if (response.success) {
                        showToast('¡Producto agregado al carrito exitosamente!');
                        stockDisplay.html(`<i class="fas fa-check-circle me-2 text-success"></i>Stock disponible: ${response.new_stock}`);
                        
                        if (response.new_stock <= 0) {
                            form.find('button[type="submit"]').prop('disabled', true);
                            quantityInput.prop('disabled', true);
                        }

                        // Emitir evento de actualización de stock
                        const stockUpdateEvent = {
                            productId: response.product_id,
                            newStock: response.new_stock,
                            timestamp: Date.now()
                        };
                        localStorage.setItem('stockUpdate', JSON.stringify(stockUpdateEvent));
                    } else {
                        showToast(response.error || 'Error al agregar al carrito', 'danger');
                    }
                // } catch (e) {
                //     showToast('Error al procesar la respuesta del servidor', 'danger');
                // }
            },
            error: function(xhr) {
                showToast('Error al agregar al carrito. Por favor, intente nuevamente.', 'danger');
            }
        });
    });

    // Escuchar eventos de actualización de stock con manejo de errores
    window.addEventListener('storage', (event) => {
        if (event.key !== 'stockUpdate') return;

        let stockUpdate;
        try {
            stockUpdate = JSON.parse(event.newValue);
        } catch (e) {
            console.warn('Error al parsear stockUpdate:', e);
            return;
        }

        if (!stockUpdate || !stockUpdate.productId || stockUpdate.newStock === undefined) {
            console.warn('Datos de stockUpdate inválidos:', stockUpdate);
            return;
        }

        const form = document.querySelector(`[data-product-id="${stockUpdate.productId}"]`);
        if (!form) {
            console.warn(`No se encontró el formulario para el productId: ${stockUpdate.productId}`);
            return;
        }

        const stockDisplay = form.closest('.card')?.querySelector('.stock-display');
        const quantityInput = form.querySelector('.product-quantity');
        const addButton = form.querySelector('button[type="submit"]');

        if (stockDisplay) {
            if (stockUpdate.newStock <= 0) {
                stockDisplay.innerHTML = '<i class="fas fa-times-circle me-2 text-danger"></i>Sin stock';
                stockDisplay.classList.remove('text-success');
                stockDisplay.classList.add('text-danger');
                if (addButton) addButton.disabled = true;
                if (quantityInput) quantityInput.closest('.input-group')?.remove();
            } else {
                stockDisplay.innerHTML = `<i class="fas fa-check-circle me-2 text-success"></i>Stock disponible: ${stockUpdate.newStock}`;
                stockDisplay.classList.remove('text-danger');
                stockDisplay.classList.add('text-success');
                if (addButton) addButton.disabled = false;
            }
        }

        if (quantityInput) {
            quantityInput.setAttribute('max', stockUpdate.newStock);
            if (parseInt(quantityInput.value) > stockUpdate.newStock) {
                quantityInput.value = stockUpdate.newStock;
            }
        }
    });
});