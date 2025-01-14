from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    credit_score = models.IntegerField(default=0)

class Loan(models.Model):
    LOAN_TYPES = (
        ('Personal', 'Personal'),
        ('Business', 'Business'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=50, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    emi_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()



class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2)


class CreditScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField()


class InterestRate(models.Model):
    loan_type = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=4, decimal_places=2)


class LoanApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_type = models.CharField(max_length=50)
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)
    repayment_terms = models.IntegerField()


class LoanApproval(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_type = models.CharField(max_length=50)
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)
    repayment_terms = models.IntegerField()


class Repayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan = models.ForeignKey('LoanApproval', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


class PaymentSchedule(models.Model):
    loan = models.ForeignKey('LoanApproval', on_delete=models.CASCADE)
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)


class Collateral(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan = models.ForeignKey('LoanApplication', on_delete=models.CASCADE)
    description = models.TextField()


class Default(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan = models.ForeignKey('LoanApproval', on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
