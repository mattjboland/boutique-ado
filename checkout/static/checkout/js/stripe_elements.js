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

// Handle form submit

// The last step to getting this working is to add a listener to the payment forms submit event.
// I'll copy this from the stripe documentation and make a couple changes.
// After getting the form element the first thing the listener does is prevent its
// default action which in our case is to post.
// Instead, we'll execute this code.
// It uses the stripe.confirm card payment method to send the card information
// securely to stripe.
// Here before we call out to stripe. We'll want to disable both
// the card element and the submit button to prevent multiple submissions.
// I'll delete the billing details for now and we'll fill those out in a bit.
// And while I'm at it this client secret variable reminds me that
// I'm actually using Python variable syntax in this file. But we're writing in JavaScript.
// So to stick with the best practices and also to make our code match this variable name.
// Let's change all these variables to camel case.
// So we call the confirm card payment method.
// Provide the card to stripe and then execute this function on the result.
// If there's an error let's do the same thing we're doing above which is to put
// the error right into the card error div.
// And otherwise.
// If the status of the payment intent comes back is succeeded we'll submit the form.
// Of course, if there's an error.
// We'll also want to re-enable the card element and the submit button to allow the user to fix it.
var form = document.getElementById('payment-form');

// The payment system for our e-commerce store is nearly finished. We just need to
// write the code to create any necessary database objects in the webhook handler.
// In this video, we'll get that started.
// Before we get to the webhook code though we need to make
// a small addition to the stripe elements javascript.
// Basically since the payment intent .succeeded webhook will be coming from stripe
// and not from our own code into the webhook handler, we need to somehow stuff the
// form data into the payment intent object so we can retrieve it once we receive the webhook.
// Most of this we can do by simply adding the form data to the
// confirmed card payment method. For example if you were to look at the
// stripe documentation and see the structure of a payment intent object.
// You'd see it has a spot for a billing details object we can add right here under the card.
// It can take a name, email, phone number, and an address with mostly
// the same fields we've got in our form. I'll add all this in getting the data
// from our form and using the trim method to strip off any excess whitespace.
// We can also add some shipping information with all the same fields
// except for email.
// You might be thinking this is a bit redundant since there's
// only one form on the page and you're right, but in reality
// customers might have different delivery and billing information so I'm adding both.
// By the way, you'll notice I've also only added postcode to the shipping
// information since the billing postal code will come from the card element and
// stripe will override it if we try to add it anyway.

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    // Then go back to the JavaScript and create a few variables.
    // We can get the boolean value of the saved info box by just looking at its checked attribute
    // We'll also need the CSRF token which we can get from the input that Django generates on our form.
    // Which will have a name of csrfmiddlewaretoken
    // Then let's create a small object to pass this information to the new view.
    // And also pass the client secret for the payment intent.
    // I'll create a variable for the new URL.
    // And last but most importantly will actually post this data to the view.
    // To do this we'll use our trusty post method built into jQuery
    // Telling it we're posting to the URL and that we want to post the post data above.
    // We'll want to wait for a response that
    // the payment intent was updated before calling the confirmed payment method
    // and this is really easy to do by just tacking on the .done method and
    // executing the callback function.
    // In the callback function, in other words, the one
    // that will be executed if our view returns a 200 response, all we have to do
    // is all the stripe stuff we're already doing, so we can just paste the whole
    // stripe function inside here and we're done.

    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    var url = '/checkout/cache_checkout_data/';

    $.post(url, postData).done(function () {
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                        name: $.trim(form.full_name.value),
                        phone: $.trim(form.phone_number.value),
                        email: $.trim(form.email.value),
                        address:{
                            line1: $.trim(form.street_address1.value),
                            line2: $.trim(form.street_address2.value),
                            city: $.trim(form.town_or_city.value),
                            country: $.trim(form.country.value),
                            state: $.trim(form.county.value),
                        }
                    }
                },
                shipping: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    address: {
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        postal_code: $.trim(form.postcode.value),
                        state: $.trim(form.county.value),
                }
            },
        }).then(function(result) {
            if (result.error) {
                var errorDiv = document.getElementById('card-errors');
                var html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        }); 
        // Conveniently we can also attach a failure function, which will be triggered
        // if our view sends a 400 bad request response. And in that case, we'll just
        // reload the page to show the user the error message from the view.
    }).fail(function () {
        // just reload the page, the error will be in django messages
        location.reload();
    })
});

    // When the user clicks the submit button the event listener 134 prevents the form from submitting
    // and instead disables the card element and triggers the loading overlay.
    // Then we create a few variables to capture the form data we can't put in
    // the payment intent here, and instead post it to the cache_checkout_data view
    // The view updates the payment intent and returns a 200 response, at which point we
    // call the confirm card payment method from stripe and if everything is ok
    // submit the form.
    // If there's an error in the form then the loading overlay will
    // be hidden the card element re-enabled and the error displayed for the user.
    // If anything goes wrong posting the data to our view. We'll reload the page and
    // display the error without ever charging the user.

    // This may seem like a lot but review this and make sure you understand it.
    // Passing data back and forth between the front end and the back end is the essence of full-stack development.
    // So it's very important to understand it well, and don't worry if it
    // doesn't make complete sense at first because this is pretty involved and
    // it'll take some time to get used to.