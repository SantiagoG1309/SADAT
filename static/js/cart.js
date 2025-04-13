// Clase Toast para manejar notificaciones
const Toast = {
    show(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container') || this.createContainer();
        const toast = document.createElement('div');
        toast.className = `toast bg-${type} text-white fade show`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        const icon = type === 'success' ? 'check-circle' : 'exclamation-circle';
        toast.innerHTML = `
            <div class="toast-body d-flex align-items-center">
                <i class="fas fa-${icon} me-2"></i>
                <span class="me-auto">${message}</span>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        
        if (typeof bootstrap === 'undefined') {
            console.error('Bootstrap no está cargado');
            return;
        }

        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 3000
        });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    createContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }
};

// Función para obtener el token CSRF de las cookies
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

// Función para actualizar el stock en la interfaz
function updateStockDisplay(productId, newStock) {
    const form = document.querySelector(`[data-product-id="${productId}"]`);
    if (form) {
        const stockDisplay = form.closest('.card')?.querySelector('.stock-display');
        const quantityInput = form.querySelector('.product-quantity');
        const addButton = form.querySelector('button[type="submit"]');

        if (stockDisplay) {
            if (newStock <= 0) {
                stockDisplay.innerHTML = '<i class="fas fa-times-circle me-2"></i>Sin stock';
                stockDisplay.classList.remove('text-success');
                stockDisplay.classList.add('text-danger');
                if (addButton) addButton.disabled = true;
                if (quantityInput) quantityInput.closest('.input-group')?.remove();
                const outOfStockMessage = document.createElement('button');
                outOfStockMessage.className = 'btn btn-secondary w-100';
                outOfStockMessage.disabled = true;
                outOfStockMessage.innerHTML = '<i class="fas fa-ban me-2"></i>Sin Stock';
                form.appendChild(outOfStockMessage);
            } else {
                stockDisplay.innerHTML = `<i class="fas fa-check-circle me-2"></i>Stock disponible: ${newStock}`;
                stockDisplay.classList.remove('text-danger');
                stockDisplay.classList.add('text-success');
                if (addButton) addButton.disabled = false;
            }
        }
        if (quantityInput) {
            quantityInput.setAttribute('max', newStock);
            if (parseInt(quantityInput.value) > newStock) {
                quantityInput.value = newStock;
            }
        }
    }
}

// Función para agregar productos al carrito (usando el backend)
function addToCart(productId, quantityInputId, maxStock) {
    if (!productId) {
        Toast.show('Error: ID de producto no válido', 'danger');
        return;
    }

    const quantityInput = document.getElementById(quantityInputId);
    if (!quantityInput) {
        console.error(`No se encontró el elemento con ID: ${quantityInputId}`);
        Toast.show('Error: No se pudo procesar la solicitud', 'danger');
        return;
    }

    const quantity = parseInt(quantityInput.value);
    if (isNaN(quantity) || quantity < 1) {
        Toast.show('La cantidad debe ser un número válido mayor a 0', 'danger');
        return;
    }

    if (quantity > maxStock) {
        Toast.show('La cantidad excede el stock disponible', 'danger');
        return;
    }

    const form = document.querySelector(`[data-product-id="${productId}"]`);
    if (!form) {
        console.error(`No se encontró el formulario para el producto: ${productId}`);
        Toast.show('Error: ID de producto no válido', 'danger');
        return;
    }

    const baseUrl = window.location.origin;
    const addToCartUrl = `${baseUrl}/cart/add/${productId}/`;

    fetch(addToCartUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ quantity })
    })
    .then(response => {
        if (response.redirected) {
            throw new Error('Debes iniciar sesión para agregar productos al carrito');
        }
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('La ruta para agregar al carrito no está disponible. Verifica que el servidor esté funcionando y que la URL sea correcta.');
            } else if (response.status === 400) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Solicitud inválida');
                });
            } else if (response.status === 403) {
                throw new Error('Debes iniciar sesión como cliente para agregar al carrito');
            }
            throw new Error(`Error HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success || data.message) {
            Toast.show(data.message || '¡Producto agregado con éxito!', 'success');
            
            if (data.new_stock !== undefined && data.product_id) {
                updateStockDisplay(data.product_id, data.new_stock);
                const stockUpdateEvent = {
                    productId: data.product_id,
                    newStock: data.new_stock,
                    timestamp: Date.now()
                };
                localStorage.setItem('stockUpdate', JSON.stringify(stockUpdateEvent));
            }
        } else if (data.error) {
            Toast.show(data.error, 'danger');
        } else {
            Toast.show('Producto agregado al carrito', 'success');
            console.log('Respuesta inesperada del servidor:', data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (error.message.includes('Debes iniciar sesión')) {
            Toast.show(error.message + '. <a href="/login/" class="text-white text-decoration-underline">Inicia sesión aquí</a>', 'danger');
        } else {
            Toast.show(error.message || 'Error al procesar la solicitud', 'danger');
        }
    });
}

// Inicializar manejadores de eventos
document.addEventListener('DOMContentLoaded', () => {
    const decreaseQuantity = (e) => {
        e.preventDefault();
        e.stopPropagation();
        const input = e.currentTarget.parentElement.querySelector('.product-quantity');
        if (input) {
            const currentValue = parseInt(input.value) || 1;
            if (currentValue > 1) {
                input.value = currentValue - 1; // Decremento de 1
                input.dispatchEvent(new Event('change'));
            }
        }
    };

    const increaseQuantity = (e) => {
        e.preventDefault();
        e.stopPropagation();
        const input = e.currentTarget.parentElement.querySelector('.product-quantity');
        if (input) {
            const maxStock = parseInt(input.getAttribute('max')) || parseInt(e.currentTarget.dataset.stock) || 0;
            const currentValue = parseInt(input.value) || 1;
            if (currentValue < maxStock) {
                input.value = currentValue + 1; // Incremento de 1
                input.dispatchEvent(new Event('change'));
            } else {
                Toast.show('No hay suficiente stock disponible', 'danger');
            }
        }
    };

    const initQuantityButtons = () => {
        // Asegurarse de que los eventos se asignen solo una vez
        document.querySelectorAll('.decrease-quantity').forEach(button => {
            button.removeEventListener('click', decreaseQuantity); // Remover manejadores previos
            button.addEventListener('click', decreaseQuantity);
        });

        document.querySelectorAll('.increase-quantity').forEach(button => {
            button.removeEventListener('click', increaseQuantity); // Remover manejadores previos
            button.addEventListener('click', increaseQuantity);
        });
    };

    const initQuantityInputs = () => {
        document.querySelectorAll('.product-quantity').forEach(input => {
            input.addEventListener('change', () => {
                const maxStock = parseInt(input.getAttribute('max')) || 0;
                let value = parseInt(input.value) || 0;

                if (value < 1) {
                    input.value = 1;
                    Toast.show('La cantidad mínima es 1', 'warning');
                } else if (value > maxStock) {
                    input.value = maxStock;
                    Toast.show('La cantidad no puede exceder el stock disponible', 'warning');
                }
            });
        });
    };

    const handleCartFormSubmit = (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const form = e.currentTarget;
        const productId = form.querySelector('input[name="product_id"]')?.value;
        const quantityInput = form.querySelector('.product-quantity');

        if (!productId || !quantityInput) {
            Toast.show('Error en el formulario', 'danger');
            return;
        }

        quantityInput.id = quantityInput.id || `quantity-input-${productId}`;
        const maxStock = parseInt(quantityInput.getAttribute('max')) || 0;
        addToCart(productId, quantityInput.id, maxStock);
    };

    const initCartForms = () => {
        if (!window.cartFormsInitialized) {
            document.querySelectorAll('.add-to-cart-form').forEach(form => {
                form.removeEventListener('submit', handleCartFormSubmit);
                form.addEventListener('submit', handleCartFormSubmit);
            });
            window.cartFormsInitialized = true;
        }
    };

    window.addEventListener('storage', (event) => {
        if (event.key === 'stockUpdate') {
            const stockUpdate = JSON.parse(event.newValue);
            if (stockUpdate && stockUpdate.productId && stockUpdate.newStock !== undefined) {
                updateStockDisplay(stockUpdate.productId, stockUpdate.newStock);
            }
        }
    });

    initQuantityButtons();
    initQuantityInputs();
    initCartForms();

    if (!document.getElementById('toast-container')) {
        Toast.createContainer();
    }
});