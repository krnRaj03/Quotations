from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser
from .manager import UserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import check_password, make_password
# Create your models here.
class CustomUser(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    password_reset_token = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    work_place = models.CharField(max_length=200, blank=True)
    is_user = models.BooleanField(_("user status"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_superuser = models.BooleanField(default=False)

    
    date_created = models.DateTimeField(auto_now_add=True)
 

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def get_full_name(self):
        """
        Returns the user's full name.
        """
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        """
        Returns the user's short name.
        """
        return self.first_name

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the given permission.
        """
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has permissions to view the app with the given label.
        """
        return True

    def set_password(self, raw_password):
        """
        Sets the user's password to the given raw password.
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Checks if the given raw password matches the user's stored password hash.
        """
        return check_password(raw_password, self.password)

class Quote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=100)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    quotation_number = models.CharField(max_length=50)
    vat = models.CharField(max_length=50)
    inco_terms = models.CharField(max_length=100)
    shipment_weight = models.CharField(max_length=50)
    shipment_dimensions = models.CharField(max_length=50)
    pre_tax_total = models.FloatField(default=0.0)
    total_price = models.FloatField(default=0.0)
    profit = models.FloatField(default=0.0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.quotation_number+" - "+self.client_name

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    all_info=models.JSONField()
    total_price = models.FloatField(default=0.0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.quote.quotation_number+" - "+str(self.id)

class InvoiceModel (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50,null=True)
    purchase_order = models.CharField(max_length=50,null=True)
    invoice_date = models.CharField(max_length=50, null=True)
    bank_details = models.CharField(max_length=2000)
    seller_name = models.CharField(max_length=200)
    buyer_name = models.CharField(max_length=200)
    director_name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.invoice_number) +"-"+ str(self.quote.quotation_number) 

