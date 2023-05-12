from django.http import JsonResponse
from django.views import View
from django.utils import timezone

from bank.models import Account, Currency, Transaction
import json
import requests
import random

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


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


@csrf_exempt
@require_http_methods(["POST"])
def pay(request):
    try:
        # Parse the incoming JSON data
        data = json.loads(request.body)
        # Extract the transaction details
        amount = data['amount']
        company_name = data['companyName']
        bookingID = data['bookingID']
    except:
        return JsonResponse({'status': 'failed', 'error': 'Parsing JSON'}, status=400)

    try:
        # Confirm booking by confirming booking ID and amount
        url = 'https://' + companyToLink(company_name) + '.pythonanywhere.com/airline/confirm_booking' # Has to be changed for when we have actual links
        payload = {
            'bookingID': str(bookingID), 
            'amount': amount,  
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            return JsonResponse({'status': 'failed', 'error': 'Amount not confirmed'}, status=400)
    except:
        return JsonResponse({'status': 'failed', 'error': 'confirming booking'}, status=400)

    try:
        currency = Currency.objects.get(code='GBP')
        recipient_account = Account.objects.get(company_name=company_name)
    except (Currency.DoesNotExist, Account.DoesNotExist):
        return JsonResponse({'status': 'failed', 'error': 'Invalid currency or recipient account'}, status=400)
    try:
        transaction = Transaction.objects.create(
            booking_id=bookingID,
            account_id=recipient_account,
            transaction_amount=amount,
            transaction_currency=currency,
            transaction_date = timezone.now(),
        )

        recipient_account.balance += transaction.transaction_amount
        recipient_account.save()
    except:
        return JsonResponse({'status': 'failed', 'error': 'Unable to alter database'}, status=400)

    return JsonResponse({'status': 'success', 'transactionID': transaction.transaction_id})
    

@csrf_exempt
@require_http_methods(["POST"])
def refund(request):
    try:
        # Parse the incoming JSON data
        data = json.loads(request.body)
        # Extract the booking ID
        bookingID = data['bookingID']
    except:
        return JsonResponse({'status': 'failed', 'error': 'Parsing JSON'}, status=400)

    # Cancel booking by confirming bookingID
    try:
        transaction = Transaction.objects.get(booking_id=bookingID)
    except (Transaction.DoesNotExist):
        return JsonResponse({'status': 'failed', 'error': 'Invalid booking ID'}, status=400)

    company_name = transaction.account_id.company_name
    url = 'https://' + companyToLink(company_name) + '.pythonanywhere.com/airline/cancel_booking' # Has to be changed for when we have actual link
    payload = {'bookingID': str(bookingID)}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        return JsonResponse({'status': 'failed', 'error': 'Booking ID not confirmed'}, status=400)

    recipient_account = transaction.account_id

    try:
        recipient_account.balance -= transaction.transaction_amount
        recipient_account.save()
    except:
        return JsonResponse({'status': 'failed', 'error': 'Unable to alter database'}, status=400)

    return JsonResponse({'status': 'success'})


@csrf_exempt
@require_http_methods(["GET"])   
def exchange(request, from_currency, amount):

    # BANK_URL = 'http://127.0.0.1:8000'

    # amount = 25.00
    # recipient_account = 'KevAir'
    # booking_id = '00129'

    # payload = {'amount':amount, 'companyName':recipient_account, 'bookingID':booking_id}
    # response = requests.post(f'{BANK_URL}/bank/pay', json=payload)
    # print(response)


    # booking_id = '00129'

    # payload = {'bookingID':booking_id}
    # response = requests.post(f'{BANK_URL}/bank/refund', json=payload)
    # print(response)


    # Populate database if not already done so
    if not Account.objects.exists():
        populateDatabase()
        
    try:
        amount = float(amount)
    except ValueError:
        return JsonResponse({'status': 'failed', 'message': 'Invalid amount'}, status=400)
    
    try:
        from_currency = Currency.objects.get(code=from_currency)
    except Currency.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'Invalid currency code'}, status=400)

    # Perform the currency exchange
    exchanged_amount = amount / from_currency.exchange_rate

    return JsonResponse({'convertedAmount': format(exchanged_amount, '.2f')})
