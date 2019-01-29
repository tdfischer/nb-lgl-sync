#!/usr/bin/env python
import requests
import json
import random
import stripe
import dotenv
import os
import time
from datetime import datetime, timedelta

dotenv.load_dotenv()

stripe.api_key = os.environ.get('STRIPE_KEY')

LGL_URL = os.environ.get('LGL_INTEGRATION_URL')

sinceTwoDaysAgo = int(time.mktime((datetime.utcnow() - timedelta(days=2)).timetuple()))

charges = stripe.Charge.list(created={'gte': sinceTwoDaysAgo})

chargeCount = 0
while len(charges) > 0:
    lastID = None
    for charge in charges:
        chargeCount += 1
        appeal = charge['statement_descriptor']
        invoice = charge['invoice']

        if invoice is not None:
            invoice_obj = stripe.Invoice.retrieve(invoice)
            for line in invoice_obj['lines']['data']:
                plan_obj = line['plan']
                if plan_obj is not None:
                    appeal = 'Stripe Plan: $%s/%s'%(plan_obj['amount'] / 100, plan_obj['interval'])

        data = {
            'full_name': charge['source']['name'],
            'amount': charge['amount'] / 100,
            'email': charge['receipt_email'],
            'txn_id': charge['id'],
            'date': datetime.utcfromtimestamp(charge['created']).strftime('%Y-%m-%d'),
            'method': 'Stripe',
            'appeal_name': appeal
        }
        requests.post(LGL_URL, data=data)
        lastID = charge['id']
    print 'Processed', chargeCount
    charges = stripe.Charge.list(starting_after=lastID, created={'gte': sinceTwoDaysAgo})
