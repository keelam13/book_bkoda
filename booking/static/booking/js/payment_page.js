$(document).ready(function () {
    const paymentForm = $('#payment-form');
    const cardRadio = $('#creditCard');
    const otherRadio = $('#otherPayment');
    const selectedPaymentMethodInput = $('#selected-payment-method-hidden');
    const cardPaymentDetails = $('#cardPaymentDetails');
    const otherPaymentDetails = $('#otherPaymentDetails');
    const cardErrors = $('#card-errors');
    const paymentIntentIdInput = $('#payment_intent_id');
    const submitButton = $('#submit-button');
    const cardholderNameInput = $('#cardholder-name');
    const firstPassengerEmail = $('#firstPassengerEmail').val();
    const firstPassengerContactNumber =$('#firstPassengerContactNumber').val();
    const termsCheck = $('#termsCheck');

    // Initial display logic
    if (cardRadio.prop('checked')) {
        cardPaymentDetails.css('display', 'block');
        otherPaymentDetails.css('display', 'none');
        submitButton.text('Confirm Card Payment');
    } else {
        cardPaymentDetails.css('display', 'none');
        otherPaymentDetails.css('display', 'block');
        submitButton.text('Confirm Booking');
    }

    // Radio button change event listener
    cardRadio.on('change', function () {
        if ($(this).prop('checked')) {
            selectedPaymentMethodInput.val('card');
            cardPaymentDetails.css('display', 'block');
            cardholderNameInput.attr('required', true);
            otherPaymentDetails.css('display', 'none');
            submitButton.text('Confirm Card Payment');
            cardErrors.text('');
        }
    });

    otherRadio.on('change', function () {
        if ($(this).prop('checked')) {
            selectedPaymentMethodInput.val('other');
            cardPaymentDetails.css('display', 'none');
            cardholderNameInput.removeAttr('required');
            otherPaymentDetails.css('display', 'block');
            submitButton.text('Confirm Booking');
            cardErrors.text('');
        }
    });

    // Stripe setup
    var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
    var clientSecret = $('#client_secret').val();
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
    var card = elements.create('card', { style: style });
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
    paymentForm.on('submit', async function (event) {
        event.preventDefault();
        card.update({ disabled: true });
        submitButton.attr('disabled', true);
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);

        cardErrors.text('');

        const paymentMethod = selectedPaymentMethodInput.val();

        if (!termsCheck.prop('checked')) {
            cardErrors.text("Please agree to the Terms & Conditions.");
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            card.update({ 'disabled': false });
            submitButton.attr('disabled', false);
            return;
        }

        if (paymentMethod === 'card') {
            if (!cardholderNameInput.val().trim()) {
                cardErrors.text("Please enter the name on the card.");
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false });
                submitButton.attr('disabled', false);
                return;
            }

            // Confirm the card payment with Stripe
            const { paymentIntent, error, authenticationFlow } = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: $.trim(cardholderNameInput.val()),
                        phone: $.trim(firstPassengerContactNumber),
                        email: $.trim(firstPassengerEmail),
                    },
                },
            });

            if (error) {
                cardErrors.text(error.message);

                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false });
                submitButton.attr('disabled', false);

            } else if (paymentIntent.status === 'succeeded') {
                paymentIntentIdInput.val(paymentIntent.id);
                paymentForm.off('submit').submit();
            } else if (paymentIntent.status === 'requires_action') {
                const { error: actionError, paymentIntent: actionPaymentIntent } = await stripe.handleCardAction(paymentIntent.client_secret);

                if (actionError) {
                    cardErrors.text(actionError.message);
                    $('#payment-form').fadeToggle(100);
                    $('#loading-overlay').fadeToggle(100);
                    card.update({ 'disabled': false });
                    submitButton.attr('disabled', false);
                } else if (actionPaymentIntent.status === 'succeeded') {
                    paymentIntentIdInput.val(actionPaymentIntent.id);
                    paymentForm.off('submit').submit();
                } else {
                    console.warn("Payment still not succeeded after action. Status:", actionPaymentIntent.status); // Debugging
                    cardErrors.text("Payment not successful after action. Status: " + actionPaymentIntent.status);
                    $('#payment-form').fadeToggle(100);
                    $('#loading-overlay').fadeToggle(100);
                    card.update({ 'disabled': false });
                    submitButton.attr('disabled', false);
                }
            } else {
                console.warn("Payment not succeeded. Status:", paymentIntent.status);
                cardErrors.text("Payment not successful. Status: " + paymentIntent.status + ". Please check details or try another method.");
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false });
                submitButton.attr('disabled', false);
            }
        } else {
            paymentForm.off('submit').submit();
        }
    });
})