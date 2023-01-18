from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes),
    path('rooms/<str:pk>/', views.getRoom),
    path('rooms/', views.getRooms),
]