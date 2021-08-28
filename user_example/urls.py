from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('see_request/',views.see_request, name="see_request"),
    path('staff_place/', views.staff_place, name="staff_place"),
    path('testhome/', views.testhome, name = 'testhome'),
]
