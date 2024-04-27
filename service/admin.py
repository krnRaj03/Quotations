from django.contrib import admin
from .models import (CustomUser,Product,Quote,InvoiceModel)
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Quote)
admin.site.register(InvoiceModel)