from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import datetime
from .models import Quote, Product
from decimal import Decimal
import json
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.
current_date = datetime.datetime.now()
fortnight = current_date + datetime.timedelta(days=15)


def nav(request):
    return render(request, "nav.html")


def home(request):
    quotes_per_month = (
        Quote.objects
        .annotate(month=TruncMonth('date_created'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    month_labels = [quote['month'].strftime('%B') for quote in quotes_per_month]
    quotes_data = [quote['total'] for quote in quotes_per_month]

    context = {
        'month_labels': json.dumps(month_labels, cls=DjangoJSONEncoder),
        'quotes_data': json.dumps(quotes_data, cls=DjangoJSONEncoder),
    }
    return render(request, "home.html", context)


def create(request):
    total_sum = 0
    total_profit=0  
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
            shipment_dimensions=request.POST.get('ship-dimensions'),
        )
        quote.save()

        # Assuming you're sending Products data as a list of JSON strings for each row
        products_data = json.loads(request.POST.get('products_data'))  # Make sure to include a hidden input in your form that contains this JSON data
        
        for product_info in products_data:
            total = product_info.get('total')
            total1=product_info.get('profit')

            total_profit += float(total1)
            total_sum += float(total)
            Product.objects.create(
                quote=quote,
                all_info=product_info,
            )  
        pre_tax_total = total_sum

        quote.pre_tax_total = pre_tax_total
        quote.profit=total_profit
        quote.save()

        # Calculate VAT if applicable
        vat_rate = request.POST.get('vat', 0)
         # Default to 0 if not found
        if vat_rate:  # Check if vat_rate is not None or an empty string
            vat_rate = float(vat_rate)
            if vat_rate > 0:  # Check if VAT is greater than 0
                vat_amount = total_sum * (vat_rate / 100)
                total_sum += vat_amount  # Add VAT to total_sum

        # Update the quote with the total price including VAT if applicable
        quote.total_price = total_sum
        quote.save()

        return redirect('finalise', id=quote.id)

    # If not POST, or for the first page load
    return render(request, 'create_quote.html')


def finalise(request,id):
    quote = Quote.objects.get(id=id)
    product=Product.objects.filter(quote=quote)
    context = {"quote":quote,"product":product}

    return render(request, "finalise_quote.html", context)


def edit(request, id):
    quote = Quote.objects.get(id=id)
    product=Product.objects.filter(quote=quote)
    for p in product:
        print(p.all_info)
    context = {"quote":quote,"product":product}

    print(product)
    return render(request, "edit_quote.html", context)


def view_all_quotes(request):
    get_quotations = Quote.objects.all()
   
    context = {"quotes":get_quotations,}
    return render(request, "view_all_quotes.html", context)


def view_single_quote(request, quote_id):
    # Retrieve the quote object based on the provided quote_id
    quote = Quote.objects.get(id=quote_id)
    products = quote.product_set.all()  # Fetch related products for the quote
    
    return render(request, 'view_single_quote.html', {'quote': quote, 'products': products})

def generate_pdf(request,id):
    quote=Quote.objects.get(id=id)
    total_price=format(quote.total_price, '.2f')
    pre_tax_total=format(quote.pre_tax_total, '.2f')
    vat=quote.vat
    quote_no=quote.quotation_number
    product=Product.objects.filter(quote=quote)
    
    # Create the PDF object directly.
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename=f"{quote_no}.pdf"'
    pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "Arialbd.ttf"))

    # Create the PDF object and draw "Hello, world!" on it.
    p = canvas.Canvas(response)
    def check_page(y, font_name="Arial", font_size=10):
        if y < 100:  # Threshold for adding a new page, adjust as needed
            p.showPage()
            p.setFont(font_name, font_size)
            return 800  # Reset y to the top of the new page
        return y

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
    p.drawString(60, 668, quote.company_name)
    p.drawString(60, 656, quote.client_name)
    p.drawString(60, 644, quote.client_email)

    current_date = datetime.datetime.now()
    fortnight = current_date + datetime.timedelta(days=15)

    font_size = 9
    p.setFont("Arial", font_size)

    p.drawString(330, 680, "Təklifin № | Quotation № | № КП:")
    p.drawString(490, 680, quote.quotation_number)
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
    y = 540
    font_size = 8
    p.setFont("Arial", font_size)  # Initial y-coordinate for products
    for i, prod in enumerate(product):
        p.drawString(70, y, str(i + 1))
        p.drawString(100, y, prod.all_info['productName'])
        LINE_HEIGHT = 9  # Define your line height
        delivery_date = prod.all_info['deliveryDate']
        if len(delivery_date) > 10:
            first_line = delivery_date[:13]
            second_line = delivery_date[13:26]  # Adjust the index to exclude the characters already used in the first line
            third_line = delivery_date[26:]
            p.drawString(310, y, first_line)
            p.drawString(310, y - LINE_HEIGHT, second_line)
            p.drawString(310, y - LINE_HEIGHT * 2, third_line)
        else:
            p.drawString(310, y, delivery_date)
        p.drawString(370, y, prod.all_info['quantity'])
        p.drawString(410, y, prod.all_info['uom'])
        p.drawString(460, y, prod.all_info['price'])
        p.drawString(500, y, prod.all_info['total'])
        y -= 35  # Move to the next line

    y -= 10  # Extra spacing before the notes section

    # NOTES Section
    p.setFillColor(colors.red)
    font_size = 7.5
    p.setFont("Arial", font_size)
    p.drawString(100, y, "NOTE: Although AVISTA LLC is an authorized distributor of Ingersol Rand, ")
    y -= 10
    p.drawString(100, y, "it is not responsible for delays in delivery cause by Ingersoll Rand.")
    y -= 20  # Adjust y as needed for the next piece of content

    # Other Sections
    p.setFillColor(colors.black)
    font_size = 8
    # Here, adjust the fixed y positions to the new dynamic y value as needed
    p.line(240, y, 540, y)  # Adjusts the y position for the line dynamically
    y -= 12  
    p.drawString(260, y, "Ümumi məbləğ ƏDV-siz | Total net value excl TAX | Всего без НДС:")
    p.drawString(500, y, pre_tax_total)
    y -= 12  # Adjusts space for the next line of text
    p.drawString(426, y, "ƏDV | VAT | НДС:")
    p.drawString(500, y, f'{vat}%')
    y -= 12  # Adjusts space for the next line of text
    p.drawString(398, y, "ÜMUMİ | TOTAL | ВСЕГО:")
    p.drawString(500, y, total_price)
    y -= 6  # Adjusts space before drawing the final line
    p.line(240, y, 540, y)  # Adjusts the y position for the final line dynamically
    y = check_page(y, "Arial", 9)
    y -= 20  # Adjust this value as needed to ensure proper spacing from the previous content
    y = check_page(y, "Arial", 9)
    y-=20

    # INCOTERMS Section
    font_size = 9
    p.setFont("Arial-Bold", font_size)
    p.drawString(70, y, "INCOTERMS şərtləri | INCOTERMS | Условия INCOTERMS:")
    y -= 10  # Adjust for space between header and details

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, y - 2, quote.inco_terms)
    p.drawString(100, y - 12, "Certificate of Origin will be provided if applicable:")
    p.drawString(100, y - 22, "Certificate of Conformity on AVISTA's letterhead will be provided upon request")
    y -= 40  # Adjust y after INCOTERMS details

    # WEIGHT & DIMENSIONS Section
    font_size = 9
    p.setFont("Arial-Bold", font_size)
    p.drawString(70, y, "Çəki və ölçülər | Weight and dimensions | Вес и размеры:")
    y -= 10  # Space between header and details

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, y - 2, f"Shipment Net Weight [approximate]: {quote.shipment_weight}")
    p.drawString(100, y - 12, f"Shipment dimensions [approximate]: {quote.shipment_dimensions}")
    y -= 30  # Adjust y after WEIGHT & DIMENSIONS details

    # PAYMENT TERMS Section
    font_size = 9
    p.setFont("Arial-Bold", font_size)
    p.drawString(70, y, "Ödəniş şərtləri | Payment terms | Условия оплаты:")
    y -= 10  # Space between header and details
    y = check_page(y, "Arial", 9)
    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, y - 2, "100% payment in advance")
    p.drawString(100, y - 12, "In case of exceptional market price increases AVISTA will be entitled to change offered prices within the validity period")
    p.drawString(100, y - 22, "In case of submitting VAT Exemption Certificates 18% VAT will not be charged. In all other cases 18% VAT will be added upon invoicing")
    p.drawString(100, y - 32, "AVISTA is not charging with VAT for the exported goods and services.")
    y -= 50  # Adjust y after PAYMENT TERMS details

    # OTHER TERMS Section
    font_size = 9
    p.setFont("Arial-Bold", font_size)
    p.drawString(70, y, "Digər şərtlər | Other terms | Иные условия:")
    y -= 10  # Space between header and details

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, y - 2, "Availability in stock at the time of issuing PO must be checked with AVISTA")
    p.drawString(100, y - 12, "Days/Weeks means business days/weeks. Holidays and weekends exclusive.")
    p.drawString(100, y - 22, "AVISTA is not responsible If the buyer selects and orders wrong part number(s) without consulting with AVISTA")
    # Adjust 'y' if you have more sections to add or if this is the end

    p.showPage()
    p.save()

    return response


