document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = $('#booking-form');
    const cardRadio = $('#creditCard');
    const otherRadio = $('#otherPayment');
    const selectedPaymentMethodInput = $('#selected-payment-method');
    const cardPaymentDetails = $('#cardPaymentDetails');
    const otherPaymentDetails = $('#otherPaymentDetails');
    const cardErrors = $('#card-errors');
    const paymentIntentIdInput = $('#payment-intent-id');
    const submitButton = $('#submit-booking-btn');

    if (cardRadio.prop('checked')) {
        cardPaymentDetails.css('display', 'block');
        otherPaymentDetails.css('display', 'none');
    } else {
        cardPaymentDetails.css('display', 'none');
        otherPaymentDetails.css('display', 'block');
    }

    cardRadio.on('change', function() {
        if ($(this).prop('checked')) {
            selectedPaymentMethodInput.val('card');
            cardPaymentDetails.css('display', 'block');
            otherPaymentDetails.css('display', 'none');
        }
    });

    otherRadio.on('change', function() {
        if ($(this).prop('checked')) {
            selectedPaymentMethodInput.val('other');
            cardPaymentDetails.css('display', 'none');
            otherPaymentDetails.css('display', 'block');
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
        if (event.error) {
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
            cardErrors.html(html);
        } else {
            cardErrors.text('');
        }
    });

    // Handle form submission
    bookingForm.on('submit', async function(event) {
        event.preventDefault();
        card.update({disabled: true});
        submitButton.attr('disabled', true);
        $('#booking-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);

        cardErrors.text('');;

        const paymentMethod = selectedPaymentMethodInput.val();

        if (paymentMethod === 'card') {
            const clientSecret = JSON.parse($('#id_client_secret').text());
            const passengerName1 = $('#passenger_name1').val();
            const passengerEmail1 = $('#passenger_email1').val();
            const passengerContactNumber1 = $('#passenger_contact_number1').val();

            // Confirm the card payment with Stripe
            const {paymentIntent, error} = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                    name: $.trim(passengerName1),
                    phone: $.trim(passengerContactNumber1),
                    email: $.trim(passengerEmail1),
                    },
                }
            });

            if (error) {
                if (error.type === "card_error" || error.type === "validation_error") {
                    cardErrors.text(error.message);
                } else {
                    cardErrors.text("An unexpected error occurred. Please try again.");
                }

                $('#booking-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false });
                submitButton.attr('disabled', false);

            } else {
                if (paymentIntent.status === 'succeeded') {
                    paymentIntentIdInput.val(paymentIntent.id);
                    bookingForm.off('submit').submit();
                } else {
                    cardErrors.text("Payment not successful. Status: " + paymentIntent.status);
                    $('#booking-form').fadeToggle(100);
                    $('#loading-overlay').fadeToggle(100);
                    card.update({ 'disabled': false});
                    submitButton.attr('disabled', false);
                }
            }
        } else {
            bookingForm.off('submit').submit();
        }
    });
});