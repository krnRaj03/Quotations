from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home' ),
    path('nav/',nav,name='nav'),
    path('create/',create_quote,name='create' ),
    
    #Quote URLs
    path('finalise-quote/<uuid:id>',finalise_quotation,name='finalise_quotation'),
    path('edit_quote/<uuid:id>',edit_quotation,name='edit_quote'),
    path('create-quotation/<uuid:id>',create_quotation,name='create_quotation'),
    path('quote/delete/<uuid:id>/', delete_quote, name='delete_quote'),
    path('view-all-quotes/',view_all_quotes,name='view_all'),
    path('quote/details/<uuid:quote_id>/', view_single_quote, name='view_single'),


    #Invoice URLs
    path('finalise-invoice/<uuid:id>/', finalise_invoice, name='finalise_invoice'),
    path('create-invoice/<uuid:id>',create_invoice,name='create_invoice'),
    path('invoice-pdf/<uuid:id>',invoice_pdf,name='invoice_pdf'),
    path('view-all-invoices/',view_all_invoices,name='view_all_invoices'),
]
