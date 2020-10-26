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