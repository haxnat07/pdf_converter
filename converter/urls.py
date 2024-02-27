from django.urls import path
from .views import *

urlpatterns = [
    #path('', upload_pdf, name='upload_pdf'),
    path('upload/', upload_pdf, name='upload_pdf'),
    path('', homepage, name='homepage'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('mail_send/', mail_send, name='mail_send'),
]
