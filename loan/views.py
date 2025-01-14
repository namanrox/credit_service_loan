# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import *
from .models import *
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer
from .models import User
from .tasks import calculate_credit_score

@api_view(['POST'])
@csrf_exempt
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        calculate_credit_score.delay(user.id) # Trigger Celery task to calculate credit score asynchronously
        response_data = {
            'id': user.id,
            'message': 'User registered successfully'
        }
        return Response(response_data, status=201)
    else:
        error_message = serializer.errors
        return Response({'error': error_message}, status=400)


@api_view(['POST'])
@csrf_exempt
def apply_loan(request):
    # Get user ID from request
    user_id = request.data.get('user_id')
    
    # Get loan details from request
    loan_type_id = request.data.get('loan_type_id')
    loan_amount = request.data.get('loan_amount')
    loan_term = request.data.get('loan_term')

    # Get user and loan type objects
    try:
        user = User.objects.get(id=user_id)
        loan_type = LoanType.objects.get(id=loan_type_id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    except LoanType.DoesNotExist:
        return Response({'error': 'Loan type does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check user's credit score against loan type
    if user.credit_score < loan_type.minimum_credit_score:
        return Response({'error': 'User does not meet minimum credit score requirements for this loan type'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check user's income against loan amount
    if user.income < loan_amount:
        return Response({'error': 'User income is not sufficient to qualify for this loan amount'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate EMI amount
    interest_rate = loan_type.interest_rate
    monthly_interest_rate = (interest_rate / 100) / 12
    total_payments = loan_term * 12
    emi = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** total_payments) / (((1 + monthly_interest_rate) ** total_payments) - 1)
    emi = Decimal(str(round(emi, 2)))
    
    # Calculate due dates and amounts for each EMI
    emi_due_dates = []
    emi_due_amounts = []
    remaining_balance = loan_amount
    for i in range(total_payments):
        emi_due_dates.append(date.today() + timedelta(days=(i+1)*30))
        emi_due_amounts.append(emi)
        remaining_balance -= emi
        if remaining_balance < 0:
            break
    emi_due_amounts[-1] += remaining_balance
    
    # Create new loan object in database
    loan = Loan(user=user, loan_type=loan_type, loan_amount=loan_amount, loan_term=loan_term, emi_amount=emi, emi_due_dates=emi_due_dates, emi_due_amounts=emi_due_amounts)
    loan.save()
    
    # Serialize loan object and return HTTP response with loan ID and EMI details
    serializer = LoanSerializer(loan)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def make_payment(request):
    loan_id = request.data.get('loan_id')
    payment_amount = request.data.get('payment_amount')

    # Check if loan_id and payment_amount are present in the request
    if not loan_id or not payment_amount:
        return Response({'error': 'Loan ID and payment amount are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if loan exists
    loan = get_object_or_404(Loan, id=loan_id)

    # Check if payment amount is valid
    if payment_amount < loan.emi_amount or payment_amount > loan.total_amount_due:
        return Response({'error': 'Invalid payment amount.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if loan is overdue
    if loan.next_due_date < date.today():
        return Response({'error': 'Loan is overdue.'}, status=status.HTTP_400_BAD_REQUEST)

    # Recalculate EMI amounts if payment amount is less than EMI amount
    if payment_amount < loan.emi_amount:
        loan.emi_amount = loan.total_amount_due - payment_amount
        loan.remaining_emis = loan.remaining_emis - 1

    # Update loan object in the database
    loan.total_amount_paid = loan.total_amount_paid + payment_amount
    loan.last_payment_date = date.today()
    loan.next_due_date = loan.next_due_date.replace(day=loan.next_due_date.day + 30)
    loan.save()

    # Serialize loan object and return as response
    serializer = LoanSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def statement(request):
    user = request.user
    loan_applications = user.loanapplication_set.all()
    statements = []
    for loan_application in loan_applications:
        statement = {}
        statement['loan_type'] = loan_application.loan_type
        statement['loan_amount'] = loan_application.loan_amount
        statement['repayment_terms'] = loan_application.repayment_terms
        payment_schedule = loan_application.payment_schedule
        statement['amount_due'] = payment_schedule.amount_due
        statement['due_date'] = payment_schedule.due_date
        statements.append(statement)
    return Response(statements)
