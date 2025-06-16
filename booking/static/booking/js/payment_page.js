$(document).ready(function () {
    const paymentForm = $('#payment-form');
    const cardPaymentRadio = $('#creditCard');
    const cashPaymentRadio = $('#cashPayment');
    const gcashPaymentRadio = $('#gcashPayment');
    const selectedPaymentMethodInput = $('#selected-payment-method-hidden');
    const cardPaymentDetails = $('#cardPaymentDetails');
    const otherPaymentDetails = $('#otherPaymentDetails');
    const cardErrors = $('#card-errors');
    const paymentIntentIdInput = $('#payment_intent_id');
    const submitButton = $('#submit-button');
    const cardholderNameInput = $('#cardholder-name');
    const firstPassengerEmail = $('#firstPassengerEmail').val();
    const firstPassengerContactNumber = $('#firstPassengerContactNumber').val();
    const termsCheck = $('#termsCheck');
    
    let stripe = null;
    let elements = null;
    let card = null;
    let clientSecret = null;

    // Function to initialize Stripe elements
    function initializeStripe() {
        if (stripe === null) {
            var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
            clientSecret = $('#client_secret').val();
            stripe = Stripe(stripePublicKey);
            elements = stripe.elements();
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
            card = elements.create('card', { style: style });
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
        }
    }

    // Function to tear down Stripe elements
    function teardownStripe() {
        if (card) {
            card.unmount();
            card = null;
            elements = null;
        }
    }

    // Initial display logic based on which radio is checked on page load
    if (cardPaymentRadio.prop('checked')) {
        selectedPaymentMethodInput.val('card');
        cardPaymentDetails.css('display', 'block');
        otherPaymentDetails.css('display', 'none');
        submitButton.text('Confirm Card Payment');
        cardholderNameInput.attr('required', true);
        initializeStripe();
    } else if (cashPaymentRadio.prop('checked')) {
        selectedPaymentMethodInput.val('CASH');
        cardPaymentDetails.css('display', 'none');
        otherPaymentDetails.css('display', 'block');
        submitButton.text('Confirm Booking');
        cardholderNameInput.removeAttr('required');
    } else if (gcashPaymentRadio.prop('checked')) {
        selectedPaymentMethodInput.val('GCASH');
        cardPaymentDetails.css('display', 'none');
        otherPaymentDetails.css('display', 'block');
        submitButton.text('Confirm Booking');
        cardholderNameInput.removeAttr('required');
    }

    // Radio button change event listeners
    cardPaymentRadio.on('change', function () {
        if ($(this).prop('checked')) {
            selectedPaymentMethodInput.val('card');
            cardPaymentDetails.css('display', 'block');
            otherPaymentDetails.css('display', 'none');
            cardholderNameInput.attr('required', true);
            submitButton.text('Confirm Card Payment');
            cardErrors.text('');
            initializeStripe();
        }
    });

    cashPaymentRadio.on('change', function () {
        if ($(this).prop('checked')) {
            selectedPaymentMethodInput.val('CASH');
            cardPaymentDetails.css('display', 'none');
            otherPaymentDetails.css('display', 'block');
            cardholderNameInput.removeAttr('required');
            submitButton.text('Confirm Booking');
            cardErrors.text('');
            teardownStripe();
        }
    });

    gcashPaymentRadio.on('change', function () {
        if ($(this).prop('checked')) {
            selectedPaymentMethodInput.val('GCASH');
            cardPaymentDetails.css('display', 'none');
            otherPaymentDetails.css('display', 'block');
            cardholderNameInput.removeAttr('required');
            submitButton.text('Confirm Booking');
            cardErrors.text('');
            teardownStripe();
        }
    });
    
    // Handle form submission
    paymentForm.on('submit', async function (event) {
        event.preventDefault();
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);

        const paymentMethod = selectedPaymentMethodInput.val();

        if (!termsCheck.prop('checked')) {
            cardErrors.text("Please agree to the Terms & Conditions.");
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            if (paymentMethod === 'card' && card) card.update({ 'disabled': false });
            submitButton.attr('disabled', false);
            return;
        }

        if (paymentMethod === 'card') {
            if (card) card.update({ disabled: true });
            submitButton.attr('disabled', true);
            cardErrors.text('');

            if (!cardholderNameInput.val().trim()) {
                cardErrors.text("Please enter the name on the card.");
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                if (card) card.update({ 'disabled': false });
                submitButton.attr('disabled', false);
                return;
            }

            // Confirm the card payment with Stripe
            if (!clientSecret) {
                 clientSecret = $('#client_secret').val();
            }

            const { paymentIntent, error } = await stripe.confirmCardPayment(clientSecret, {
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
                if (card) card.update({ 'disabled': false });
                submitButton.attr('disabled', false);

            } else if (paymentIntent.status === 'succeeded') {
                paymentIntentIdInput.val(paymentIntent.id);
                paymentForm.off('submit').submit();

            } else if (paymentIntent.status === 'requires_action') {
                // Handle 3D Secure or other actions
                const { error: actionError, paymentIntent: actionPaymentIntent } = await stripe.handleCardAction(paymentIntent.client_secret);

                if (actionError) {
                    cardErrors.text(actionError.message);
                    $('#payment-form').fadeToggle(100);
                    $('#loading-overlay').fadeToggle(100);
                    if (card) card.update({ 'disabled': false });
                    submitButton.attr('disabled', false);
                } else if (actionPaymentIntent.status === 'succeeded') {
                    paymentIntentIdInput.val(actionPaymentIntent.id);
                    paymentForm.off('submit').submit();
                } else {
                    console.warn("Payment still not succeeded after action. Status:", actionPaymentIntent.status); // Debugging
                    cardErrors.text("Payment not successful after action. Status: " + actionPaymentIntent.status);
                    $('#payment-form').fadeToggle(100);
                    $('#loading-overlay').fadeToggle(100);
                    if (card) card.update({ 'disabled': false });
                    submitButton.attr('disabled', false);
                }
            } else {
                console.warn("Payment not succeeded. Status:", paymentIntent.status);
                cardErrors.text("Payment not successful. Status: " + paymentIntent.status + ". Please check details or try another method.");
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                if (card) card.update({ 'disabled': false });
                submitButton.attr('disabled', false);
            }
        } else {
            paymentForm.off('submit').submit();
        }
    });
});