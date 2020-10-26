/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js

    Inside it the first thing I'm going to do is get the stripe public key.
    And client secret from the template using a little jQuery.
    Remember those little script elements contain the values we need as their text.
    So we can get them just by getting their ids and using the .text function.
    I'll also slice off the first and last character on each
    since they'll have quotation marks which we don't want.
    Finally, made possible by the stripe js included in the base template.
    All we need to do to set up stripe is create a variable using our stripe public key.
    Now we can use it to create an instance of stripe elements.
    Use that to create a card element.
    And finally, mount the card element to the div we created in the last video.
    The card element can also accept a style argument.

    So I'm going to get some basic styles from the stripe js Docs.
    And the only thing I'll update is the default colour of the element to black.
    And I'll change the invalid colour to match bootstraps text danger class.
*/

var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
var client_secret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripe_public_key);
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
// First let's add a listener on the card element for the change event.
// And every time it changes we'll check to see if there are any errors.
// If so we'll display them in the card errors div we created near the card element on the checkout page.
// Looking at the site now it's more clear what the issue is if the user experience is an error.

// As we've rendered the error from stripe with a nice little icon next to it.
// Before we dive into the code let's briefly discuss how this is going to work.
// Stripe works with what are called payment intents.
// The process will be that when a user hits the checkout page
// the checkout view will call out to stripe and create a payment intent
// for the current amount of the shopping bag.
// When stripe creates it. it'll also have a secret that identifies it.
// Which will be returned to us and we'll send it to the template as the client secret variable.
// Then in the JavaScript on the client side.
// We'll call the confirm card payment method from stripe js.
// Using the client secret which will verify the card number.
// The first thing needed to accomplish that is a function to calculate
// the current bag total in the view.
// Even though we wrote it for a different purpose we've actually already got the
// code we need right in the context processor in the bag app.

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