from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterUserView, ApplyLoanView, MakePaymentView, StatementView

urlpatterns = [
    path('', include(router.urls)),
    path('register-user/', RegisterUserView.as_view(), name='register_user'),
    path('apply-loan/', ApplyLoanView.as_view(), name='apply_loan'),
    path('make-payment/', MakePaymentView.as_view(), name='make_payment'),
    path('statement/', StatementView.as_view(), name='statement'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
