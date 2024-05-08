from service.models import InvoiceModel, Quote, Product
from django.shortcuts import render, redirect
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.http import HttpResponse

