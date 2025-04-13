// Usamos las funciones getCookie y Toast definidas en cart.js.

// Función para cancelar el pedido (eliminar todos los productos del carrito)
function cancelOrder() {
    console.log("Iniciando cancelOrder..."); // Depuración
    const csrftoken = getCookie('csrftoken');
    console.log("CSRF Token:", csrftoken); // Depuración

    if (!csrftoken) {
        Toast.show('Error: No se encontró el token CSRF. Asegúrate de estar autenticado.', 'danger');
        return;
    }

    fetch('/cart/clear/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: '' // No necesitamos enviar datos adicionales
    })
    .then(response => {
        console.log("Respuesta del servidor:", response); // Depuración
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Datos recibidos:", data); // Depuración
        if (data.success) {
            Toast.show('Pedido cancelado exitosamente', 'success');
            // Recargar la página para reflejar los cambios
            setTimeout(() => location.reload(), 1000);
        } else if (data.error) {
            Toast.show(data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Error al cancelar el pedido:', error);
        Toast.show('Error al cancelar el pedido: ' + error.message, 'danger');
    });
}

// Código que se ejecuta al cargar la página
// Función para eliminar un producto específico del carrito
function removeFromCart(productId) {
    console.log("Iniciando removeFromCart para producto:", productId);
    const csrftoken = getCookie('csrftoken');

    if (!csrftoken) {
        Toast.show('Error: No se encontró el token CSRF. Asegúrate de estar autenticado.', 'danger');
        return;
    }

    fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.message) {
            Toast.show(data.message, 'success');
            const row = document.querySelector(`tr[data-product-id="${productId}"]`);
            if (row) {
                row.remove();
                // Actualizar la interfaz sin recargar la página
                updateCartInterface();
            }
        } else if (data.error) {
            Toast.show(data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Error al eliminar el producto:', error);
        Toast.show('Error al eliminar el producto: ' + error.message, 'danger');
    });
}

// Función para actualizar la interfaz del carrito
function updateCartInterface() {
    const cartItems = document.querySelectorAll('tr[data-product-id]');
    const cartEmpty = cartItems.length === 0;
    const cartContainer = document.querySelector('.cart-container');
    const emptyCartMessage = document.querySelector('.empty-cart-message');

    if (cartEmpty) {
        if (cartContainer) cartContainer.style.display = 'none';
        if (emptyCartMessage) {
            emptyCartMessage.style.display = 'block';
        } else {
            const message = document.createElement('div');
            message.className = 'empty-cart-message alert alert-info';
            message.textContent = 'Tu carrito está vacío';
            document.querySelector('main').appendChild(message);
        }
    }
}
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM cargado, configurando manejadores de eventos..."); // Depuración

    // Lógica para el modal de pago
    const paymentMethod = document.getElementsByName('paymentMethod');
    const paymentForm = document.getElementById('paymentForm');

    if (paymentMethod && paymentForm) {
        paymentMethod.forEach(function(radio) {
            radio.addEventListener('change', function() {
                if (this.id === 'creditCard') {
                    paymentForm.style.display = 'block';
                } else {
                    paymentForm.style.display = 'none';
                }
            });
        });
    }

    // Manejador para el botón de Cancelar Pedido (X)
    const cancelButtons = document.querySelectorAll('.cancel-order-btn');
    console.log("Botones de cancelar encontrados:", cancelButtons.length); // Depuración
    cancelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Botón de cancelar pedido clicado"); // Depuración
            if (confirm('¿Estás seguro de que deseas cancelar el pedido? Esto eliminará todos los productos del carrito.')) {
                cancelOrder();
            }
        });
    });

    // Escuchar eventos de actualización de stock
    window.addEventListener('storage', (event) => {
        if (event.key === 'stockUpdate') {
            const stockUpdate = JSON.parse(event.newValue);
            if (stockUpdate && stockUpdate.productId && stockUpdate.newStock !== undefined) {
                const row = document.querySelector(`tr[data-product-id="${stockUpdate.productId}"]`);
                if (row) {
                    const quantityInput = row.querySelector('.product-quantity');
                    const currentQuantity = parseInt(quantityInput.value);
                    if (stockUpdate.newStock < currentQuantity) {
                        quantityInput.value = stockUpdate.newStock;
                        Toast.show(`El stock del producto ha cambiado. Cantidad ajustada a ${stockUpdate.newStock}.`, 'warning');
                    }
                }
            }
        }
    });

    // Manejador para los botones de eliminar producto individual
    const removeButtons = document.querySelectorAll('.remove-item-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            if (confirm('¿Estás seguro de que deseas eliminar este producto del carrito?')) {
                removeFromCart(productId);
            }
        });
    });
});