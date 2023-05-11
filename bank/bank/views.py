from django.http import JsonResponse
from django.views import View
from django.utils import timezone

from bank.models import Account, Currency, Transaction
import json
import random


# Currency.objects.create(code='GBP', symbol='£', exchange_rate=1.00)

# Currency.objects.create(code='USD', symbol='$', exchange_rate=1.38) 
# Currency.objects.create(code='EUR', symbol='€', exchange_rate=1.17) 
# Currency.objects.create(code='JPY', symbol='¥', exchange_rate=152.24)  
# Currency.objects.create(code='AUD', symbol='$', exchange_rate=1.80) 
# Currency.objects.create(code='CAD', symbol='$', exchange_rate=1.72)
# Currency.objects.create(code='CHF', symbol='CHF', exchange_rate=1.27)
# Currency.objects.create(code='CNY', symbol='¥', exchange_rate=8.78)
# Currency.objects.create(code='SEK', symbol='kr', exchange_rate=11.92)
# Currency.objects.create(code='NZD', symbol='$', exchange_rate=1.97)

# gbp = Currency.objects.get(code='GBP')

# Account.objects.create(company_name='Company A', balance=10000.00, currency_id=gbp)
# Account.objects.create(company_name='Company B', balance=20000.00, currency_id=gbp)
# Account.objects.create(company_name='Company C', balance=30000.00, currency_id=gbp)

# account_a = Account.objects.get(account_id=1)
# account_b = Account.objects.get(account_id=2)
# account_c = Account.objects.get(account_id=3)

# Transaction.objects.create(account_id=account_a, transaction_date=timezone.now(), transaction_amount=random.uniform(100, 1000), transaction_currency=gbp)
# Transaction.objects.create(account_id=account_b, transaction_date=timezone.now(), transaction_amount=random.uniform(100, 1000), transaction_currency=gbp)
# Transaction.objects.create(account_id=account_c, transaction_date=timezone.now(), transaction_amount=random.uniform(100, 1000), transaction_currency=gbp)


class PayView(View):
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Parse the incoming JSON data
        data = json.loads(request.body)

        # Extract the transaction details
        amount = data['transaction']['amount']
        currency_code = data['transaction']['currency']
        recipient_account_name = data['transaction']['recipient account']

        try:
            currency = Currency.objects.get(code=currency_code)
            recipient_account = Account.objects.get(company_name=recipient_account_name)
        except (Currency.DoesNotExist, Account.DoesNotExist):
            return JsonResponse({'status': 'failed', 'message': 'Invalid currency or recipient account'}, status=400)

        transaction = Transaction.objects.create(
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
        transaction_id = data['transactionId']
        
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)
        except (Transaction.DoesNotExist):
            return JsonResponse({'status': 'failed', 'message': 'Invalid transaction ID'}, status=400)

        amount = transaction.transaction_amount
        recipient_account = Account.objects.get(account_id=transaction.account_id)

        exchanged_amount = exchange_currency(transaction.transaction_amount, recipient_account.currency_id, transaction.transaction_currency)

        recipient_account.balance -= exchanged_amount
        recipient_account.save()

        return JsonResponse({'status': 'success', 'transaction_id': transaction_id})
    

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
    exchanged_amount = amount * from_currency.exchange_rate / to_currency.exchange_rate

    return exchanged_amount


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
        exchanged_amount = amount * from_currency.exchange_rate / to_currency.exchange_rate

        # Return the result
        return JsonResponse({
            'original_amount': amount,
            'original_currency': from_currency.code,
            'exchanged_amount': exchanged_amount,
            'exchanged_currency': to_currency.code,
        })
    