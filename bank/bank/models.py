from django.db import models

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255, unique=True)
    balance = models.FloatField()
    currency_id = models.ForeignKey('Currency', on_delete=models.CASCADE)

    def __str__(self):
        return self.company_name

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    account_id = models.ForeignKey(Account, related_name='transactions', on_delete=models.CASCADE)
    booking_id = models.CharField(max_length=255)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_amount = models.FloatField()
    transaction_currency = models.ForeignKey('Currency', on_delete=models.CASCADE)

    def __str__(self):
        return f'Transaction {self.transaction_id} for {self.account_id.company_name}'

class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=3)
    symbol = models.CharField(max_length=1)
    exchange_rate = models.FloatField()

    def __str__(self):
        return self.code