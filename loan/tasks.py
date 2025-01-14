from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from .models import User, Transaction

@shared_task
def calculate_credit_score(user_id):
    try:
        user = User.objects.get(id=user_id)
        transactions = Transaction.objects.filter(aadhar_id=user.aadhar_id)

        # calculate total account balance for the user
        account_balance = sum([t.amount if t.transaction_type == 'CREDIT' else -t.amount for t in transactions])

        # calculate credit score based on account balance
        if account_balance >= 1000000:
            credit_score = 900
        elif account_balance <= 100000:
            credit_score = 300
        else:
            credit_score = 300 + (account_balance - 100000) // 15000 * 10

        # update user's credit score
        user.credit_score = credit_score
        user.save()
    except ObjectDoesNotExist:
        pass
