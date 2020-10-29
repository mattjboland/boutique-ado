# Now obviously we need to create that file so the import
# will work. Let's make a new file called webhooks.py. Right
# at the same level as our webhook handler. Inside it, I'll
# create the webhook function which will take a request.
# The code for this will come directly from stripe with a
# couple modifications. First I'll change the name of
# endpoint_secret to wh_secret which we'll create in a moment.
# I'll also add a generic exception line 44 handler to catch any
# exceptions other than the two stripe has provided.

# Before we add that part, at the top we'll need to set up the
# stripe API key. And the webhook secret which will be used to
# verify that the webhook actually came from stripe. And we'll
# need a few imports. We'll need our settings file to get the
# webhook and the stripe API secrets. We need HttpResponse so
# these exception handlers will work. We'll need our webhook
# handler class and of course stripe. And last we need two
# decorators require_post which as the name implies will make
# this view require a post request and will reject get requests.
# And CSRF exempt since stripe won't send a CSRF token like
# we'd normally need.

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # Set up a webhook handler
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get the webhook type from Stripe
    event_type = event['type']

    # If there's a handler for it, get it from the event map
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event
    response = event_handler(event)
    return response
