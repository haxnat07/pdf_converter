from django.urls import path
from .views import *

urlpatterns = [
    #path('', upload_pdf, name='upload_pdf'),
    path('', upload_pdf, name='upload_pdf'),
]
