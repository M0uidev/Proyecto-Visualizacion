/**
 * Applies a coupon code from the wallet modal.
 * @param {string} code - The coupon code to apply.
 */
function applyWalletCoupon(code) {
    const couponCodeInput = document.getElementById('couponCode');
    if (couponCodeInput) {
        couponCodeInput.value = code;
        
        // Close modal
        const modalEl = document.getElementById('walletModal');
        if (modalEl && window.bootstrap) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) {
                modal.hide();
            }
        }
        
        // Submit form
        const couponForm = document.getElementById('couponForm');
        if (couponForm) {
            couponForm.dispatchEvent(new Event('submit'));
        }
    }
}

/**
 * Toggles the visibility and required state of shipping fields based on delivery method.
 */
function toggleDeliveryFields() {
    const deliveryDispatch = document.getElementById('deliveryDispatch');
    // If the element doesn't exist (e.g. on a different page), return safely
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
    // Initialize delivery fields state
    toggleDeliveryFields();

    // Coupon AJAX handling
    const couponForm = document.getElementById('couponForm');
    if (couponForm) {
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const codeInput = document.getElementById('couponCode');
            const errorDiv = document.getElementById('couponError');
            
            if (!codeInput) return;
            
            const code = codeInput.value.trim();
            if (!code) return;

            // Clear previous error
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
                    // Update UI with discount info
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
                    // Show error message
                    if (errorDiv) {
                        errorDiv.textContent = data.message;
                        errorDiv.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (errorDiv) {
                    errorDiv.textContent = 'Ocurrió un error al procesar el cupón.';
                    errorDiv.style.display = 'block';
                }
            });
        });
    }
});
