from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home' ),
    path('create/',create,name='create' ),
    path('nav/',nav,name='nav'),
    path('pdf/',hello_world_pdf,name='hello_world_pdf'),
    path('edit/',view_quotation,name='view_quotation'),
]
