from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home' ),
    path('nav/',nav,name='nav'),
    path('create/',create,name='create' ),
    path('finalise/<uuid:id>',finalise,name='finalise'),
    path('edit/<uuid:id>',edit,name='edit'),
    path('pdf/<uuid:id>',generate_pdf,name='generate_pdf'),
    path('view-all/',view_all_quotes,name='view_all'),
    path('quote/details/<uuid:quote_id>/', view_single_quote, name='view_single'),

]
