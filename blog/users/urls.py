from django.urls import path
from .views import UserRegisterView, UserLoginView, UserLogoutView, ProfileView, ProfileUpdateView, CustomPasswordChangeView, MyProfileView
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/<slug:username>/', ProfileView.as_view(), name='profile'),
    path('my-profile/', MyProfileView.as_view(), name='my_profile'),
    path('profile/<slug:username>/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='password_change'),
    # path('profile/<slug:username>/', PublicProfileView.as_view(), name='user_profile')
]
