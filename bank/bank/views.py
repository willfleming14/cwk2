from django.http import JsonResponse
from django.views import View
from django.utils import timezone

from bank.models import Account, Currency, Transaction
import json
import requests
import random

def populateDatabase():
    Currency.objects.create(code='GBP', symbol='£', exchange_rate=1.00)

    Currency.objects.create(code='USD', symbol='$', exchange_rate=1.38) 
    Currency.objects.create(code='EUR', symbol='€', exchange_rate=1.17) 
    Currency.objects.create(code='JPY', symbol='¥', exchange_rate=152.24)  
    Currency.objects.create(code='AUD', symbol='$', exchange_rate=1.80) 
    Currency.objects.create(code='CAD', symbol='$', exchange_rate=1.72)
    Currency.objects.create(code='CHF', symbol='CHF', exchange_rate=1.27)
    Currency.objects.create(code='CNY', symbol='¥', exchange_rate=8.78)
    Currency.objects.create(code='SEK', symbol='kr', exchange_rate=11.92)
    Currency.objects.create(code='NZD', symbol='$', exchange_rate=1.97)

    gbp = Currency.objects.get(code='GBP')

    Account.objects.create(company_name='KevAir', balance=10000.00, currency_id=gbp)
    Account.objects.create(company_name='Cathay Pacific', balance=20000.00, currency_id=gbp)
    Account.objects.create(company_name='FlyLo', balance=30000.00, currency_id=gbp)
    Account.objects.create(company_name='Emirates', balance=30000.00, currency_id=gbp)


    account_a = Account.objects.get(account_id=1)
    account_b = Account.objects.get(account_id=2)
    account_c = Account.objects.get(account_id=3)
    account_d = Account.objects.get(account_id=4)

    Transaction.objects.create(account_id=account_a, booking_id='9123', transaction_date=timezone.now(), transaction_amount=format(random.uniform(100, 1000), '.2f'), transaction_currency=gbp)
    Transaction.objects.create(account_id=account_b, booking_id='9124', transaction_date=timezone.now(), transaction_amount=format(random.uniform(100, 1000), '.2f'), transaction_currency=gbp)
    Transaction.objects.create(account_id=account_c, booking_id='9125', transaction_date=timezone.now(), transaction_amount=format(random.uniform(100, 1000), '.2f'), transaction_currency=gbp)
    Transaction.objects.create(account_id=account_d, booking_id='9126', transaction_date=timezone.now(), transaction_amount=format(random.uniform(100, 1000), '.2f'), transaction_currency=gbp)

def companyToLink(company_name):
    if company_name == 'KevAir':
        return 'ed19km2b'
    elif company_name == 'Cathay Pacific':
        return 'mavericklow'
    elif company_name == 'FlyLo':
        return 'krzsztfkml'
    else:
        return 'safwanchowdhury'

class PayView(View):
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Populate database if not already done so
        if not Account.objects.exists():
            populateDatabase()

        # Parse the incoming JSON data
        data = json.loads(request.body)

        # Extract the transaction details
        amount = data['transaction']['amount']
        company_name = data['transaction']['companyName']
        bookingID = data['transaction']['bookingID']

        # Confirm booking by confirming amount and reservation ID
        url = companyToLink(company_name) + '.pythonanywhere.com/airline/cancel_reservation' # Has to be changed for when we have actual links
        data = {
            'bookingID': bookingID, 
            'amount': amount,  
        }
        response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            return JsonResponse({'status': 'failed', 'message': 'Amount not confirmed'}, status=400)

        try:
            currency = Currency.objects.get(code='GBP')
            recipient_account = Account.objects.get(company_name=company_name)
        except (Currency.DoesNotExist, Account.DoesNotExist):
            return JsonResponse({'status': 'failed', 'message': 'Invalid currency or recipient account'}, status=400)

        transaction = Transaction.objects.create(
            booking_id=bookingID,
            account_id=recipient_account,
            transaction_amount=amount,
            transaction_currency_id=currency,
            transaction_date = timezone.now(),
        )

        exchanged_amount = exchange_currency(transaction.transaction_amount, transaction.transaction_currency, recipient_account.currency_id)

        recipient_account.balance += exchanged_amount
        recipient_account.save()

        return JsonResponse({'status': 'success', 'TransactionID': transaction.transaction_id})
    

class RefundView(View):
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Parse the incoming JSON data
        data = json.loads(request.body)

        # Extract the transaction ID
        bookingID = data['bookingID']

        # Cancel booking by confirming bookingID
        try:
            transaction = Transaction.objects.get(booking_id=bookingID)
        except (Transaction.DoesNotExist):
            return JsonResponse({'status': 'failed', 'message': 'Invalid transaction ID'}, status=400)
    
        company_name = transaction.account_id.company_name
        url = companyToLink(company_name) + '.pythonanywhere.com/airline/cancel_reservation' # Has to be changed for when we have actual links
        data = {
            'bookingID': bookingID,  
        }
        response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            return JsonResponse({'status': 'failed', 'message': 'Booking ID not confirmed'}, status=400)

        recipient_account = Account.objects.get(account_id=transaction.account_id)

        exchanged_amount = exchange_currency(transaction.transaction_amount, recipient_account.currency_id, transaction.transaction_currency)

        recipient_account.balance -= exchanged_amount
        recipient_account.save()

        return JsonResponse({'status': 'success', 'transaction_id': bookingID})
    

def exchange_currency(amount, from_currency_id, to_currency_id):
    # Convert the amount to a float
    try:
        amount = float(amount)
    except ValueError:
        raise ValueError('Invalid amount parameter')

    # Get the currencies
    try:
        from_currency = Currency.objects.get(id=from_currency_id)
        to_currency = Currency.objects.get(id=to_currency_id)
    except Currency.DoesNotExist:
        raise ValueError('Invalid currency code')

    # Perform the currency exchange
    exchanged_amount = amount / from_currency.exchange_rate * to_currency.exchange_rate

    return format(exchanged_amount, '.2f')


class CurrencyExchangeView(View):
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Parse the incoming JSON data
        data = json.loads(request.body)

        # Extract the parameters from the request
        amount = data.get('amount')
        from_currency_code = data.get('from_currency')
        to_currency_code = data.get('to_currency')

        # Validate the parameters
        if not all([amount, from_currency_code, to_currency_code]):
            return JsonResponse({'status': 'failed', 'message': 'Missing required parameters'}, status=400)
        
        # Convert the amount to a float
        try:
            amount = float(amount)
        except ValueError:
            return JsonResponse({'status': 'failed', 'message': 'Invalid amount parameter'}, status=400)

        # Get the currencies
        try:
            from_currency = Currency.objects.get(code=from_currency_code)
            to_currency = Currency.objects.get(code=to_currency_code)
        except Currency.DoesNotExist:
            return JsonResponse({'status': 'failed', 'message': 'Invalid currency code'}, status=400)

        # Perform the currency exchange
        exchanged_amount = amount / from_currency.exchange_rate * to_currency.exchange_rate

        # Return the result
        return JsonResponse({
            'original_amount': format(amount, '.2f'),
            'original_currency': from_currency.code,
            'exchanged_amount': format(exchanged_amount, '.2f'),
            'exchanged_currency': to_currency.code,
        })
    
class GetCurrencyExchangeView(View):
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, from_currency, amount, *args, **kwargs):
        # Populate database if not already done so
        if not Account.objects.exists():
            populateDatabase()
            
        try:
            amount = float(amount)
        except ValueError:
            return JsonResponse({'status': 'failed', 'message': 'Invalid amount'}, status=400)
        
        try:
            from_currency = Currency.objects.get(code=from_currency)
            to_currency = Currency.objects.get(code='GBP')
        except Currency.DoesNotExist:
            return JsonResponse({'status': 'failed', 'message': 'Invalid currency code'}, status=400)

        # Perform the currency exchange
        exchanged_amount = amount / from_currency.exchange_rate * to_currency.exchange_rate

        return JsonResponse({'convertedAmount': format(exchanged_amount, '.2f')})

    