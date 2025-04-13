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

    $('.add-to-cart-form').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var data = form.serialize();
        var productCard = form.closest('.card');
        var quantityInput = form.find('input[name="quantity"]');
        var stockDisplay = productCard.find('.stock-display');
        var currentStock = parseInt(stockDisplay.text());
        var requestedQuantity = parseInt(quantityInput.val());

        if (requestedQuantity > currentStock) {
            showToast('La cantidad solicitada excede el stock disponible', 'danger');
            return;
        }
        
        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            dataType: 'json',
            success: function(response) {
                try {
                    if (response.success) {
                        showToast('¡Producto agregado al carrito exitosamente!');
                        stockDisplay.text(response.new_stock + ' unidades');
                        
                        if (response.new_stock <= 0) {
                            form.find('button[type="submit"]').prop('disabled', true);
                            quantityInput.prop('disabled', true);
                        }
                    } else {
                        showToast(response.error || 'Error al agregar al carrito', 'danger');
                    }
                } catch (e) {
                    showToast('Error al procesar la respuesta del servidor', 'danger');
                }
            },
            error: function(xhr) {
                showToast('Error al agregar al carrito. Por favor, intente nuevamente.', 'danger');
            }
        });
    });
});