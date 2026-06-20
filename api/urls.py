from django.urls import path
from .views import RegisterView, LogoutView, PredictionView, HistoryView, ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/login/refresh/', TokenRefreshView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('predict/', PredictionView.as_view()),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('history/', HistoryView.as_view(), name='history'),
]