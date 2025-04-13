const Cart = {
    init() {
        this.bindEvents();
        this.initQuantityValidation();
    },

    bindEvents() {
        // MODIFICACIÓN: Eliminada la lógica para .decrease-quantity e .increase-quantity
        // Esto ahora es manejado por cart.js para evitar duplicación de eventos
    },

    initQuantityValidation() {
        if (typeof $ !== 'undefined') {
            $('input[name="quantity"]').off('input').on('input', function() {
                const input = $(this);
                const value = parseInt(input.val()) || 0;
                const min = parseInt(input.attr('min')) || 1;
                const stock = parseInt(input.attr('max')) || 0;

                if (value < min) {
                    input.val(min);
                } else if (value > stock) {
                    input.val(stock);
                    Toast.show('La cantidad no puede exceder el stock disponible', 'danger');
                }
            });
        }
    },

    updateStockDisplayMain(form, newStock) {
        const productCard = form instanceof jQuery ? form.closest('.card')[0] : form.closest('.card');
        if (!productCard) return;

        const stockDisplay = productCard.querySelector('.stock-display');
        const addButton = form instanceof jQuery ? form.find('button[type="submit"]')[0] : form.querySelector('button[type="submit"]');
        const quantityInput = form instanceof jQuery ? form.find('input[name="quantity"]')[0] : form.querySelector('input[name="quantity"]');

        if (stockDisplay) {
            stockDisplay.classList.remove('text-success', 'text-danger', 'fw-bold');
            productCard.classList.remove('out-of-stock');

            if (newStock <= 0) {
                stockDisplay.innerHTML = '<i class="fas fa-times-circle me-2"></i>Sin stock';
                stockDisplay.classList.add('text-danger', 'fw-bold');
                if (addButton) addButton.disabled = true;
                if (quantityInput) {
                    quantityInput.disabled = true;
                    quantityInput.value = 0;
                }
                productCard.classList.add('out-of-stock');
            } else {
                stockDisplay.innerHTML = `<i class="fas fa-check-circle me-2"></i>Stock disponible: ${newStock}`;
                stockDisplay.classList.add('text-success');
                if (addButton) addButton.disabled = false;
                if (quantityInput) {
                    quantityInput.disabled = false;
                    if (parseInt(quantityInput.value) > newStock) {
                        quantityInput.value = newStock;
                    }
                }
            }
        }
    },
};

// Inicialización cuando el documento está listo
document.addEventListener('DOMContentLoaded', () => {
    if (typeof bootstrap === 'undefined') {
        console.warn('Bootstrap no está cargado - Algunas funcionalidades pueden no estar disponibles');
    }

    if (typeof bootstrap !== 'undefined') {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    }

    Cart.init();

    if (typeof $ !== 'undefined') {
        $('.card, .toast').addClass('fade-in');

        $('form').on('submit', function(e) {
            if (this.checkValidity() === false) {
                e.preventDefault();
                e.stopPropagation();
            }
            $(this).addClass('was-validated');
        });
    }
});