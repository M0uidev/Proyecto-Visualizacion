/**
 * Aplica un código de cupón desde el modal de chequera.
 * @param {string} code - Código de cupón a aplicar.
 */
function applyWalletCoupon(code) {
    const couponCodeInput = document.getElementById('couponCode');
    if (couponCodeInput) {
        couponCodeInput.value = code;
        
        // Cierra el modal
        const modalEl = document.getElementById('walletModal');
        if (modalEl && window.bootstrap) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) {
                modal.hide();
            }
        }
        
        // Envía el formulario
        const couponForm = document.getElementById('couponForm');
        if (couponForm) {
            couponForm.dispatchEvent(new Event('submit'));
        }
    }
}

/**
 * Alterna visibilidad y estado requerido de campos de envío según el método de entrega.
 */
function toggleDeliveryFields() {
    const deliveryDispatch = document.getElementById('deliveryDispatch');
    // Si el elemento no existe, retorna de forma segura
    if (!deliveryDispatch) return;

    const isDispatch = deliveryDispatch.checked;
    const shippingFields = document.getElementById('shippingFields');
    
    if (shippingFields) {
        const inputs = shippingFields.querySelectorAll('input, select');
        
        if (isDispatch) {
            shippingFields.style.display = 'block';
            inputs.forEach(input => input.required = true);
        } else {
            shippingFields.style.display = 'none';
            inputs.forEach(input => input.required = false);
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Inicializa estado de campos de entrega
    toggleDeliveryFields();

    // Manejo AJAX del cupón
    const couponForm = document.getElementById('couponForm');
    if (couponForm) {
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const codeInput = document.getElementById('couponCode');
            const errorDiv = document.getElementById('couponError');
            
            if (!codeInput) return;
            
            const code = codeInput.value.trim();
            if (!code) return;

            // Limpia error anterior
            if (errorDiv) {
                errorDiv.style.display = 'none';
                errorDiv.textContent = '';
            }

            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualiza UI con información del descuento
                    const couponSection = document.getElementById('couponSection');
                    if (couponSection) couponSection.style.display = 'none';
                    
                    const couponLabel = document.getElementById('couponLabel');
                    const couponAmount = document.getElementById('couponAmount');
                    const finalTotalDisplay = document.getElementById('finalTotalDisplay');
                    
                    if (couponLabel) couponLabel.textContent = `Cupón (${data.code})`;
                    if (couponAmount) couponAmount.textContent = `-$${data.discount_amount}`;
                    if (finalTotalDisplay) finalTotalDisplay.textContent = `$${data.new_total}`;
                    
                    const couponSummaryRow = document.getElementById('couponSummaryRow');
                    if (couponSummaryRow) couponSummaryRow.style.display = 'flex';
                    
                    const removeCouponRow = document.getElementById('removeCouponRow');
                    if (removeCouponRow) removeCouponRow.style.display = 'block';
                    
                } else {
                    // Muestra mensaje de error
                    if (errorDiv) {
                        errorDiv.textContent = data.message;
                        errorDiv.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (errorDiv) {
                    errorDiv.textContent = 'Error al procesar el cupón.';
                    errorDiv.style.display = 'block';
                }
            });
        });
    }
});
