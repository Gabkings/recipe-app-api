from django.urls import path 
from . import views

app_name = 'users'
urlpatterns = [
    path('users/create', views.CreateUserView.as_view(), name='create'),
    path('users/token', views.CreateTokenView.as_view(), name='token'),
    path('users/me', views.ManageUserView.as_view(), name='me'),
]
