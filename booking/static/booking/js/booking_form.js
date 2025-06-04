document.addEventListener('DOMContentLoaded', function() {
    const paymentMethodRadios = document.querySelectorAll('input[name="payment_method"]');
    const cardPaymentDetails = document.getElementById('cardPaymentDetails');
    const otherPaymentDetails = document.getElementById('otherPaymentDetails');
    const cardInputs = cardPaymentDetails.querySelectorAll('input');
  
    // Function to update the visibility of payment details sections
    function updatePaymentDetailsVisibility() {
        let selectedMethod = null;
        for (const radio of paymentMethodRadios) {
            if (radio.checked) {
                selectedMethod = radio.value;
                break;
            }
        }

        if (selectedMethod === 'card') {
            cardPaymentDetails.style.display = 'block';
            otherPaymentDetails.style.display = 'none';
            cardInputs.forEach(input => input.disabled = false);
        } else if (selectedMethod === 'other') {
            cardPaymentDetails.style.display = 'none';
            otherPaymentDetails.style.display = 'block';
            cardInputs.forEach(input => input.disabled = true);
        }
    }

    paymentMethodRadios.forEach(radio => {
        radio.addEventListener('change', updatePaymentDetailsVisibility);
    });

    updatePaymentDetailsVisibility();

});