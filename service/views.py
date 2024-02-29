from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import datetime
from .models import Quote, Product
from decimal import Decimal
import json
# Create your views here.
current_date = datetime.datetime.now()
fortnight = current_date + datetime.timedelta(days=15)


def create(request):
    if request.method == 'POST':
        # Extract and save the Quote information
        quote = Quote(
            company_name=request.POST.get('company-name'),
            client_name=request.POST.get('client-name'),
            client_email=request.POST.get('client-email'),
            quotation_number=request.POST.get('quote-no'),
            vat=request.POST.get('vat'),
            inco_terms=request.POST.get('inco-terms'),
            shipment_weight=request.POST.get('ship-weight'),
        )
        quote.save()

        # Process and save each Product
        # Assuming you're sending Products data as a list of JSON strings for each row
        products_data = json.loads(request.POST.get('products_data'))  # Make sure to include a hidden input in your form that contains this JSON data

        
        for product_info in products_data:
            Product.objects.create(
                quote=quote,
                all_info=product_info,
            )
        print(products_data)
  

        # return JsonResponse({"message":"Good!"})  # Redirect to a new URL on success

    # If not POST, or for the first page load
    return render(request, 'create.html')

def view_quotation(request):
    quotations = Quote.objects.all()
    return render(request, "edit.html", {"quotations": quotations})

def nav(request):
    return render(request, "nav.html")


def home(request):
    get_quotations = Quote.objects.all()
    print(get_quotations)
    return render(request, "home.html")


# def hello_world_pdf(request):

#     # Create the PDF object directly.
#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = 'attachment; filename="hello_world.pdf"'
#     pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/Arial.ttf'))
#     pdfmetrics.registerFont(TTFont('Arial-Bold', 'Arialbd.ttf'))

#     # Create the PDF object and draw "Hello, world!" on it.
#     p = canvas.Canvas(response)
#      # Set the font size
#     font_size = 10
#     p.setFont("Arial", font_size)
#     p.drawString(60, 800, "https://bakustock.com")
#     p.drawString(60, 788, "Tel: 050 406 30 77")

#     font_size = 14
#     p.setFont("Arial-Bold", font_size)
#     p.drawString(250, 800, "AVISTA LLC")

#     font_size = 10
#     p.setFont("Arial", font_size)
#     p.drawString(400, 800, "E-mail: avista@bakustock.com")
#     p.drawString(400, 788, "E-mail: avista.mmc@gmail.com")

#     p.setFont("Arial-Bold", 11)
#     p.drawString(60, 720,"QİYMƏT TƏKLİFİ | QUOTATION | КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ")

#     p.setFont("Arial", 9)
#     p.drawString(60, 680, "Müştəri | Customer | Клиент: ")
#     p.drawString(60, 668, "Company XYZ")
#     p.drawString(60, 656, "Concerned Person")
#     p.drawString(60, 644, "Mail")

#     p.drawString(330, 680,     "Təklifin № | Quotation № | № КП:")
#     p.drawString(490, 680,     "A24-061.1")
#     p.drawString(330, 668, "                       Tarix | Date | Дата:")
#     p.drawString(490, 668, current_date.strftime("%d-%m-%Y"))
#     p.drawString(305, 656, "Etibarlıdır | Valid till | Действителен до:")
#     p.drawString(490, 656, fortnight.strftime("%d-%m-%Y"))
#     p.drawString(332, 644, "Sorğu № | RFQ № | № Запроса:")
#     p.drawString(490, 644, "email")

#     p.showPage()
#     p.save()

#     return response


def hello_world_pdf(request):
    # Create the PDF object directly.
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="hello_world.pdf"'
    pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "Arialbd.ttf"))

    # Create the PDF object and draw "Hello, world!" on it.
    p = canvas.Canvas(response)

    # Set the font size
    font_size = 10
    p.setFont("Arial", font_size)
    p.drawString(60, 800, "https://bakustock.com")
    p.drawString(60, 788, "Tel: 050 406 30 77")

    font_size = 14
    p.setFont("Arial-Bold", font_size)
    p.drawString(250, 800, "AVISTA LLC")

    font_size = 10
    p.setFont("Arial", font_size)
    p.drawString(400, 800, "E-mail: avista@bakustock.com")
    p.drawString(400, 788, "E-mail: avista.mmc@gmail.com")

    p.setFont("Arial-Bold", 11)
    p.drawString(60, 720, "QİYMƏT TƏKLİFİ | QUOTATION | КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ")

    p.setFont("Arial", 9)
    p.drawString(60, 680, "Müştəri | Customer | Клиент: ")
    p.drawString(60, 668, "Company XYZ")
    p.drawString(60, 656, "Concerned Person")
    p.drawString(60, 644, "Mail")

    current_date = datetime.datetime.now()
    fortnight = current_date + datetime.timedelta(days=15)

    font_size = 9
    p.setFont("Arial", font_size)

    p.drawString(330, 680, "Təklifin № | Quotation № | № КП:")
    p.drawString(490, 680, "A24-061.1")
    p.drawString(330, 668, "Tarix | Date | Дата:")
    p.drawString(490, 668, current_date.strftime("%d/%m/%Y"))
    p.drawString(330, 656, "Etibarlıdır | Valid till | Действitelen do:")
    p.drawString(490, 656, fortnight.strftime("%d/%m/%Y"))
    p.drawString(330, 644, "Sorğu № | RFQ № | № Зaproca:")
    p.drawString(490, 644, "email")

    p.line(50, 610, 540, 610)  # Draws a line from (250, 790) to (400, 790)
    p.drawString(70, 585, "№")
    p.drawString(100, 595, "Malların-Xidmətlərin təsviri")
    p.drawString(310, 595, "Çatdırılma")
    p.drawString(370, 595, "Say")
    p.drawString(410, 595, "Ölcü vahidi")
    p.drawString(460, 595, "Qiymət")
    p.drawString(500, 595, "Toplam")

    p.drawString(100, 585, "Description of Goods-Services")
    p.drawString(310, 585, "Delivery")
    p.drawString(370, 585, "QTY")
    p.drawString(410, 585, "UOM")
    p.drawString(460, 585, "Price")
    p.drawString(500, 585, "Total")

    p.drawString(100, 575, "Наименование Товаров-Услуг")
    p.drawString(310, 575, "Cроки")
    p.drawString(370, 575, "Кол-во")
    p.drawString(410, 575, "Единица")
    p.drawString(460, 575, "Цена")
    p.drawString(500, 575, "Сумма")
    p.line(50, 565, 540, 565)  # Draws a line from (250, 790) to (400, 790)

    # Products
    p.drawString(70, 530, "1")
    p.drawString(100, 530, "Product 1")
    p.drawString(310, 530, "15 days")
    p.drawString(370, 530, "100")
    p.drawString(410, 530, "kg")
    p.drawString(460, 530, "100.00")
    p.drawString(500, 530, "10000.00")

    p.drawString(70, 510, "2")
    p.drawString(100, 510, "Product 2")
    p.drawString(310, 510, "15 days")
    p.drawString(370, 510, "100")
    p.drawString(410, 510, "kg")
    p.drawString(460, 510, "100.00")
    p.drawString(500, 510, "10000.00")

    # NOTES
    p.setFillColor(colors.red)
    font_size = 7.5
    p.setFont("Arial", font_size)
    p.drawString(
        100,
        480,
        "NOTE: Although AVISTA LLC is an authorized distributor of Ingersol Rand, ",
    )
    p.drawString(
        100,
        470,
        "it is not responsible for delays in delivery cause by Ingersoll Rand.",
    )

    #
    p.setFillColor(colors.black)
    font_size = 8
    p.line(240, 450, 540, 450)  # Draws a line
    p.drawString(
        260, 438, "Ümumi məbləğ ƏDV-siz | Total net value excl TAX | Всего без НДС:"
    )
    p.drawString(500, 438, "1000.00")
    p.drawString(426, 426, "ƏDV | VAT | НДС:")
    p.drawString(500, 426, "18%")
    p.drawString(398, 414, "ÜMUMİ | TOTAL | ВСЕГО:")
    p.drawString(500, 414, "1180.00")
    p.line(240, 408, 540, 408)  # Draws a line

    # INCOTERMS
    # INCOTERMS
    font_size = 9
    p.setFont("Arial", font_size)
    p.drawString(70, 380, "INCOTERMS şərtləri | INCOTERMS | Условия INCOTERMS:")

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, 370, "DDP Baku Price")
    p.drawString(100, 360, "Certificate of Origin will be provided if applicable:")
    p.drawString(
        100,
        350,
        "Certificate of Conformity on AVISTA's letterhead will be provided upon request",
    )

    # WEIGHT & DIMENSIONS
    font_size = 9
    p.setFont("Arial", font_size)
    p.drawString(70, 320, "Çəki və ölçülər | Weight and dimensions | Вес и размеры:")

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, 310, "Shipment Net Weight [approximate] :")
    p.drawString(100, 300, "Shipment dimensions [approximate] :")

    # PAYMENT TERMS
    font_size = 9
    p.setFont("Arial", font_size)
    p.drawString(70, 260, "Ödəniş şərtləri | Payment terms | Условия оплаты:")

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, 250, "100% payment in advance")
    p.drawString(
        100,
        240,
        "In case of exceptional market price increases AVISTA will be entitled to change offered prices within the validity period",
    )
    p.drawString(
        100,
        230,
        "In case of submitting VAT Exemption Certificates 18% VAT will not be charged. In all other cases 18% VAT will be added upon invoicing",
    )
    p.drawString(
        100, 220, "AVISTA is not charging with VAT for the exported goods and services."
    )

    # OTHER TERMS
    font_size = 9
    p.setFont("Arial", font_size)
    p.drawString(70, 180, "Digər şərtlər | Other terms | Иные условия:")

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(
        100,
        170,
        "Availability in stock at the time of issuing PO must be checked with AVISTA",
    )
    p.drawString(
        100,
        160,
        "Days/Weeks means business days/weeks. Holidays and weekends exclusive.",
    )
    p.drawString(
        100,
        150,
        "AVISTA is not responsible If the buyer selects and orders wrong part number(s) without consulting with AVISTA",
    )

    p.showPage()
    p.save()

    return response
