from django.http import HttpResponse

from bank.models import Account, Currency, Transaction
from django.utils import timezone
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


def hello(request): 
    return HttpResponse("Hello, Will!")