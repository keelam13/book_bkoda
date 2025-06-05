document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = document.getElementById('booking-form');
    const submitButton = document.getElementById('submit-booking-btn');
    const cardRadio = document.getElementById('creditCard');
    const otherRadio = document.getElementById('otherPayment');
    const selectedPaymentMethodInput = document.getElementById('selected-payment-method');
    const cardPaymentDetails = document.getElementById('cardPaymentDetails');
    const otherPaymentDetails = document.getElementById('otherPaymentDetails');
    const cardErrors = document.getElementById('card-errors');
    const paymentIntentIdInput = document.getElementById('payment-intent-id');

    if (cardRadio.checked) {
        cardPaymentDetails.style.display = 'block';
        otherPaymentDetails.style.display = 'none';
    } else {
        cardPaymentDetails.style.display = 'none';
        otherPaymentDetails.style.display = 'block';
    }

    cardRadio.addEventListener('change', function() {
        if (this.checked) {
            selectedPaymentMethodInput.value = 'card';
            cardPaymentDetails.style.display = 'block';
            otherPaymentDetails.style.display = 'none';
        }
    });

    otherRadio.addEventListener('change', function() {
        if (this.checked) {
            selectedPaymentMethodInput.value = 'other';
            cardPaymentDetails.style.display = 'none';
            otherPaymentDetails.style.display = 'block';
        }
    });

    var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
    var clientSecret = $('#id_client_secret').text().slice(1, -1);
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();
    var style = {
        base: {
            color: '#000',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };
    var card = elements.create('card', {style: style});
    card.mount('#card-element');

    // Handle realtime validation errors on the card element
    card.addEventListener('change', function (event) {
        var errorDiv = document.getElementById('card-errors');
        if (event.error) {
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
            $(errorDiv).html(html);
        } else {
            errorDiv.textContent = '';
        }
    });


    // Handle form submission
    bookingForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        submitButton.disabled = true;
        cardErrors.textContent = '';

        const paymentMethod = selectedPaymentMethodInput.value;

        if (paymentMethod === 'card') {
            const clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);

            // Confirm the card payment with Stripe
            const {paymentIntent, error} = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                },
            });

            if (error) {
                if (error.type === "card_error" || error.type === "validation_error") {
                    cardErrors.textContent = error.message;
                } else {
                    cardErrors.textContent = "An unexpected error occurred. Please try again.";
                }
                submitButton.disabled = false;
            } else {
                if (paymentIntent.status === 'succeeded') {
                    paymentIntentIdInput.value = paymentIntent.id;
                    bookingForm.submit();
                } else {
                    cardErrors.textContent = "Payment not successful. Status: " + paymentIntent.status;
                    submitButton.disabled = false;
                }
            }
        } else {
            bookingForm.submit();
        }
    });
});