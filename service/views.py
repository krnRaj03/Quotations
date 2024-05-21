from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from .models import Quote, Product, InvoiceModel
from decimal import Decimal
import json,datetime
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.
current_date = datetime.datetime.now()
fortnight = current_date + datetime.timedelta(days=15)


# NAV & HOME
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
    profit_per_month = (
        Quote.objects
        .annotate(month=TruncMonth('date_created'))
        .values('month')
        .annotate(total_profit=Sum('profit'))
        .order_by('month')
    )

    invoices_per_month = (
        InvoiceModel.objects
        .annotate(month=TruncMonth('date_created'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    month_labels = [quote['month'].strftime('%B') for quote in quotes_per_month]
    quotes_data = [quote['total'] for quote in quotes_per_month]
    invoices_data = [invoice['total'] for invoice in invoices_per_month]
    profit_data = [profit['total_profit'] for profit in profit_per_month]

    context = {
        'month_labels': json.dumps(month_labels, cls=DjangoJSONEncoder),
        'quotes_data': json.dumps(quotes_data, cls=DjangoJSONEncoder),
        'invoices_data': json.dumps(invoices_data, cls=DjangoJSONEncoder),
        'profit_data': json.dumps(profit_data, cls=DjangoJSONEncoder),
    }
    return render(request, "home.html", context)

#############################

#Quotes
def create_quote(request):
    total_sum = 0
    total_profit=0  
    if request.method == 'POST':
        generate_quote = Quote(
            company_name=request.POST.get('company-name'),
            client_name=request.POST.get('client-name'),
            client_email=request.POST.get('client-email'),
            quotation_number=request.POST.get('quote-no'),
            vat=request.POST.get('vat'),
            inco_terms=request.POST.get('inco-terms'),
            shipment_weight=request.POST.get('ship-weight'),
            shipment_dimensions=request.POST.get('ship-dimensions'),
        )
        if Quote.objects.filter(quotation_number=generate_quote.quotation_number):
            return HttpResponse ("Quotation number already exists")
        
        generate_quote.save()

        # Products data as a list of JSON  for each row
        products_data = json.loads(request.POST.get('products_data'))  # Make sure to include a hidden input in your form that contains this JSON data

        for product_info in products_data:
            total = product_info.get('total')
            total1=product_info.get('profit')

            total_profit += float(total1)
            total_sum += float(total)
            Product.objects.create(
                quote=generate_quote,
                all_info=product_info,
            )  
        pre_tax_total = total_sum

        generate_quote.pre_tax_total = pre_tax_total
        generate_quote.profit=total_profit
        generate_quote.save()

        # Calculate VAT 
        vat_rate = request.POST.get('vat', 0)
        if vat_rate:  
            vat_rate = float(vat_rate)
            if vat_rate > 0: 
                vat_amount = total_sum * (vat_rate / 100)
                total_sum += vat_amount  

        # Update total price
        generate_quote.total_price = total_sum
        generate_quote.save()

        return redirect('finalise_quotation', id=generate_quote.id)

    return render(request, 'quotes/create_quote.html')


def finalise_quotation(request,id):
    quote = Quote.objects.get(id=id)
    product=Product.objects.filter(quote=quote)
    
    context = {"quote":quote,"product":product}
    return render(request, "quotes/finalise_quote.html", context)


def create_quotation(request,id):
    quote=Quote.objects.get(id=id)
    total_price=format(quote.total_price, '.2f')
    pre_tax_total=format(quote.pre_tax_total, '.2f')
    vat=quote.vat
    quote_no=quote.quotation_number
    products=Product.objects.filter(quote=quote)
    for product in products:
        coo=product.all_info.get('coo')
        hs_code=product.all_info.get('hsCode')
    
    
    #PDF object 
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename=f"{quote_no}.pdf"'
    pdfmetrics.registerFont(TTFont("Arial", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", "Arial.ttf"))

    p = canvas.Canvas(response)
    def check_page(y, font_name="Arial", font_size=10):
        if y < 100:  # Threshold for adding a new page
            p.showPage()
            p.setFont(font_name, font_size)
            return 800  # Reset y to the top 
        return y

  
    font_size = 10
    p.setFont("Arial", font_size)
    p.drawString(60, 800, "www.bakustock.com")
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

    p.line(50, 610, 540, 610)  
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
    p.line(50, 565, 540, 565)  # Horizontal line


    # Products
    y = 540
    font_size = 8
    p.setFont("Arial", font_size)  # Initial y-coordinate for products
    for i, prod in enumerate(products):
        p.drawString(70, y, str(i + 1))
        p.drawString(100, y, prod.all_info['productName'])
        LINE_HEIGHT = 9  
        delivery_date = prod.all_info['deliveryDate']
        if hs_code and coo:
            p.drawString(100, y- LINE_HEIGHT,f"COO: {prod.all_info['coo']}    HS Code: {prod.all_info['hsCode']}")
        if len(delivery_date) > 10:
            first_line = delivery_date[:13]
            second_line = delivery_date[13:26]  
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
        y -= 35  

    y -= 10  

    # NOTES Section
    p.setFillColor(colors.red)
    font_size = 7.5
    p.setFont("Arial", font_size)
    p.drawString(100, y, "NOTE: Although AVISTA LLC is an authorized distributor of Ingersol Rand, ")
    y -= 10
    p.drawString(100, y, "it is not responsible for delays in delivery cause by Ingersoll Rand.")
    y -= 20  

    # Other Sections
    p.setFillColor(colors.black)
    font_size = 8
   
    p.line(240, y, 540, y) 
    y -= 12  
    p.drawString(260, y, "Ümumi məbləğ ƏDV-siz | Total net value excl TAX | Всего без НДС:")
    p.drawString(500, y, pre_tax_total)
    y -= 12  
    p.drawString(426, y, "ƏDV | VAT | НДС:")
    p.drawString(500, y, f'{vat}%')
    y -= 12 
    p.drawString(398, y, "ÜMUMİ | TOTAL | ВСЕГО:")
    p.drawString(500, y, total_price)
    y -= 6  
    p.line(240, y, 540, y) 
    y = check_page(y, "Arial", 9)
    y -= 20  
    y = check_page(y, "Arial", 9)
    y-=20

    # INCOTERMS Section
    font_size = 9
    p.setFont("Arial-Bold", font_size)
    p.drawString(70, y, "INCOTERMS şərtləri | INCOTERMS | Условия INCOTERMS:")
    y -= 10  

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, y - 2, quote.inco_terms)
    p.drawString(100, y - 12, "Certificate of Origin will be provided if applicable:")
    p.drawString(100, y - 22, "Certificate of Conformity on AVISTA's letterhead will be provided upon request")
    y -= 40  

    # WEIGHT & DIMENSIONS Section
    font_size = 9
    p.setFont("Arial-Bold", font_size)
    p.drawString(70, y, "Çəki və ölçülər | Weight and dimensions | Вес и размеры:")
    y -= 10 

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, y - 2, f"Shipment Net Weight [approximate]: {quote.shipment_weight}")
    p.drawString(100, y - 12, f"Shipment dimensions [approximate]: {quote.shipment_dimensions}")
    y -= 30  

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
    y -= 50  

    # OTHER TERMS Section
    font_size = 9
    p.setFont("Arial-Bold", font_size)
    p.drawString(70, y, "Digər şərtlər | Other terms | Иные условия:")
    y -= 10 

    font_size = 8
    p.setFont("Arial", font_size)
    p.drawString(100, y - 2, "Availability in stock at the time of issuing PO must be checked with AVISTA")
    p.drawString(100, y - 12, "Days/Weeks means business days/weeks. Holidays and weekends exclusive.")
    p.drawString(100, y - 22, "AVISTA is not responsible If the buyer selects and orders wrong part number(s) without consulting with AVISTA")

    p.showPage()
    p.save()

    return response


def edit_quotation(request, id):
    quote = Quote.objects.get(id=id)
    products=Product.objects.filter(quote=quote)

    if request.method == 'POST':
        # Update Quote
        quote.company_name = request.POST.get('company_name')
        quote.client_name = request.POST.get('client_name')
        quote.client_email = request.POST.get('client_email')
        quote.total_price = request.POST.get('total_price', 0.0)
        quote.profit = request.POST.get('profit', 0.0)
        quote.vat = request.POST.get('vat')
        quote.inco_terms = request.POST.get('inco_terms')
        quote.shipment_weight = request.POST.get('shipment_weight')
        quote.save()

        # Update Product 
    products_json = request.POST.get('products_json')
    
    if products_json:
        products_data = json.loads(products_json)
        print(type(products_data))
        for product_info in products_data:
            product_id = product_info.get('id')
            product_quantity = int(product_info.get('quantity'))
            product_price = int(product_info.get('price'))
            total = product_quantity * product_price
            print(total)
            if product_id:
                product = Product.objects.get(id=product_id)
                product.all_info = {
                    'productName': product_info.get('productName'),
                    'deliveryDate': product_info.get('deliveryDate'),
                    'quantity': product_info.get('quantity'),
                    'uom': product_info.get('uom'),
                    'price': product_info.get('price'),
                    'total': total,
                }
                product.save()
        return redirect('view_all')  # Redirect after POST

    return render(request, 'quotes/edit_quote.html', {'quote': quote, 'products': products})


def view_all_quotes(request):
    get_quotations = Quote.objects.all()
   
    context = {"quotes":get_quotations}
    return render(request, "quotes/view_all_quotes.html", context)


def view_single_quote(request, quote_id):
    quote = Quote.objects.get(id=quote_id)
    products = quote.product_set.all()  
    
    return render(request, 'quotes/view_single_quote.html', {'quote': quote, 'products': products})


def delete_quote(request, id):
    quote = Quote.objects.get(id=id)
    quote.delete()
    return redirect('view_all')


#################################

#Invoices
def view_all_invoices(request):
    invoices = InvoiceModel.objects.all()
    context = {"invoices":invoices}
    return render(request, "invoices/view_all_invoices.html", context)


def view_single_invoice(request,invoice_id):
    invoice=InvoiceModel.objects.get(id=invoice_id)
    products=Product.objects.filter(quote=invoice.quote)
    context={"invoice":invoice,"products":products}
    return render(request, "invoices/view_single_invoice.html", context)


def finalise_invoice(request,id):
    quote = Quote.objects.get(id=id)
    product=Product.objects.filter(quote=quote)
    
    try:
        invoice=InvoiceModel.objects.get(quote=quote)
        if invoice.quote is not None:
            return HttpResponse("The invoice already exists!")

    except:
        # Account details
        account_options = [
                {
                    'value': 'AZ77PAHA40060AZNHC0100067812 - AVISTA MMC',
                    'label': 'AZN',
                    'details': """AZN Account number: AZ77PAHA40060AZNHC0100067812
                                    Account name: AVISTA MMC
                                    VÖEN: 1803853771 		
                                    Beneficiary’s Bank: PASHA Bank JSC, Baku, Azerbaijan			
                                    Correspondent account: AZ82NABZ01350100000000071944 
                                    Bank S.W.I.F.T BIK: PAHAAZ22
                                    Bank VÖEN: 1700767721
                                    Bank code: 505141"""
                },
                {
                    'value': 'AZ68PAHA40160USDHC0100067812 - AVISTA MMC',
                    'label': 'USD',
                    'details': """USD Account of the Beneficiary: AZ68PAHA40160USDHC0100067812		
                                    Beneficiary’s Bank: PASHA Bank JSC, Baku, Azerbaijan		
                                    S.W.I.F.T BIK: PAHAAZ22 		

                                    Correspondent account				
                                    Account with Institution: Raiffeisen Bank International AG 
                                    Address: Am Stadtpark 9, 1030 Vienna		
                                    SWIFT BIC: RZBAATWW		
                                    Correspondent account: 70-55.081.095		
                                    Identification number: 00067812"""
                },
                {
                    'value': 'AZ02PAHA40160EURHC0100067812 - AVISTA MMC',
                    'label': 'EUR',
                    'details': """EUR Account of the Beneficiary: AZ02PAHA40160EURHC0100067812		
                                    Beneficiary’s Bank: PASHA Bank JSC, Baku, Azerbaijan		
                                    S.W.I.F.T BIK: PAHAAZ22 		

                                    Correspondent account				
                                    Account with Institution: Raiffeisen Bank International AG 
                                    Address: Am Stadtpark 9, 1030 Vienna		
                                    SWIFT BIC: RZBAATWW		
                                    Correspondent account: 1-55.081.095		
                                    Identification number: 00067812"""
                }
            ]

        if request.method == 'POST':
            bank_details = request.POST['bank_details']
            selected_details = next((item['details'] for item in account_options if item['value'] == bank_details), "No details found.")
            invoice_number = request.POST['invoice_number']
            invoice_date = request.POST['date']
            seller_name = request.POST['seller']
            buyer_name = request.POST['buyer']
            purchase_order = request.POST['purchase_order']
            director_name = request.POST['director']
        
            invoice=InvoiceModel.objects.create(invoice_number=invoice_number,quote=quote,
                                            purchase_order=purchase_order,invoice_date=invoice_date,
                                            bank_details=selected_details,seller_name=seller_name,
                                            buyer_name=buyer_name,director_name=director_name)
            invoice.save()
            return redirect('create_invoice', id=quote.id)
            

    context = {"quote":quote,"product":product,"account_options": account_options}
    return render(request, "invoices/finalise_invoice.html", context)


def create_invoice(request, id):
    quote = Quote.objects.get(id=id)
    product=Product.objects.filter(quote=quote)
    invoice = InvoiceModel.objects.get(quote=quote)
   
    bank_details_str = invoice.bank_details
    context = {"quote":quote,"product":product,"invoice":invoice,"bank_details_str":bank_details_str}
    return render(request, "invoices/create_invoice.html",context)


def invoice_pdf(request, id):
    quote = Quote.objects.get(id=id)
    product=Product.objects.filter(quote=quote)
    invoice = InvoiceModel.objects.get(quote=quote)
    bank_details_str = invoice.bank_details
    

    for p in product:
        name=p.all_info.get('productName')
        quantity=p.all_info.get('quantity')
        uom=p.all_info.get('uom')
        price=p.all_info.get('price')

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{quote.quotation_number}.pdf"'
    pdfmetrics.registerFont(TTFont("Arial", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial_Bold", "/usr/share/fonts/truetype/msttcorefonts/arialbd.ttf"))

    # Create PDF object
    p = canvas.Canvas(response)
    p.setFont("Arial", 10)

    details = [
        (80, 710, f"Fakturanın Nömrəsi | Invoice Number | Номер фактуры: {invoice.invoice_number}           Tarix | Date | Дата: {invoice.invoice_date}"),
        (80, 685, "Satıcı | Seller | Продавец:"+"        "+invoice.seller_name+"                      "+ "Alıcı | Buyer | Покупатель:"+ "        "+invoice.buyer_name),
        (80, 660, "Alış Sifarişi | Purchase Order | Заказ №:"+"         "+ invoice.purchase_order),
    ]

    padding = 5  # Padding around text for rectangle
    line_width=1.5
    for x, y, text in details:
        text_width = p.stringWidth(text, "Arial", 10)
        p.drawString(x, y, text)
        p.setLineWidth(line_width)
        p.rect(x - padding, y - 6, text_width + 2 * padding, 18, stroke=1, fill=0)
    
    texts = [
    ("№", 2),
    ("Sayı\nQTY\nКол-во", 25),  # x offset from the start of the rectangle
    ("Ölcü vahidi\nUOM\nЕдиница", 62),
    ("Malların təsviri | Description of goods | Наименование товара", 125),
    ("Qiymət\nPrice\nЦена", 380),
    ("Toplam\nTotal\nСумма", 430)
         ]
    x_start = 80  # Start rectangle
    y_start = 632 
    font_name = "Arial"
    font_size = 9
    line_height = 12  

    p.setFont(font_name, font_size)

    # Calculate dimensions for rectangle
    max_height = max(text.count('\n') + 1 for text, _ in texts) * line_height
    max_width = 0

    column_widths = []
    for text, offset in texts:
        width = max(p.stringWidth(line, font_name, font_size) for line in text.split('\n'))
        column_widths.append(offset + width)  # Store the full width of each column
        max_width = max(max_width, offset + width)  # Update max width considering the offset

    # Calculate the starting x-coordinates for centered text
    center_positions = []
    for text, offset in texts:
        width = max(p.stringWidth(line, font_name, font_size) for line in text.split('\n'))
        center_positions.append(x_start + offset + (width / 2))

    # Draw each block of text centered
    for (text, offset), center_x in zip(texts, center_positions):
        lines = text.split('\n')
        current_y = y_start
        for line in lines:
            text_width = p.stringWidth(line, font_name, font_size)
            p.drawString(center_x - (text_width /1.9), current_y, line)
            current_y -= line_height  # Decrement y to move to the next line

    # Draw rectangle around the content
    p.rect(x_start - 5, y_start - max_height, max_width + 10, max_height + 12, stroke=1, fill=0)

    # Draw vertical separators
    for i, width in enumerate(column_widths[:-1]):  # Exclude the last column since we don't need a separator after it
        separator_x = x_start + width + 1  # +2 for some padding
        p.line(separator_x, y_start - max_height, separator_x, y_start + 12)

    # Products
    y = 570
    font_size = 8.5
    p.setFont("Arial", font_size)  
    for i, prod in enumerate(product):
        p.drawString(85, y, str(i + 1)+".")
        p.drawString(110, y, prod.all_info['quantity'])
        p.drawString(150, y, prod.all_info['uom'])
        p.drawString(198, y, prod.all_info['productName'])
        p.drawString(460, y, prod.all_info['price'])
        p.drawString(507, y, prod.all_info['total'])
        y -= 18  # Move to the next line
    y -= 5 

    font_size =10
    p.setFont("Arial_Bold", font_size)
    p.drawString(80, y, "Şərtlər | Terms | Условие:"+"                 "+"Rate: 1.00€ = ")
    y -= 15

    p.setFont("Arial", 9)
    p.drawString(250, y, "Terms:"+ "        "+ quote.inco_terms)
    y -= 15

    p.drawString(298,y,"50% in advance, 50% before shipping")
    y -= 6

    #Horizontal line
    x_start = 80  
    x_end = 550   
    y_position = y  
    p.line(x_start, y_position, x_end, y_position)
    y -= 12

    p.drawString(150, y, "Ümumi məbləğ ƏDV-siz | Total net value excl TAX | Всего без НДС:"+"        "+ str(quote.pre_tax_total))
    y -= 12
    p.drawString(350, y, "ƏDV | VAT | НДС:" + "        "+ str(quote.vat)+"%")
    y -= 12
    p.setFont("Arial_Bold", 9)
    p.drawString(314, y, "ÜMUMİ | TOTAL | ВСЕГО:"+"        "+ str(quote.total_price))
    y -= 8

    #horizontal line
    x_start = 80  
    x_end = 550   
    y_position = y  
    p.line(x_start, y_position, x_end, y_position)
    y -= 20

    p.setFont("Arial_Bold", 10)
    p.drawString(80, y, "BANK REKVIZITLƏRİ | BANK DETAILS | РЕКВИЗИТЫ СЧЁТА:")
    y -= 5

    details_list = bank_details_str.split('                          ')
    y -= 10  
    
    p.setFont("Arial", 9)
    for detail in details_list:
        detail = detail.strip()
        if detail: 
            p.drawString(80, y, detail)
            y -= 12  
            

    y -=20

    p.setFont("Arial_Bold", 10)
    p.drawString(80, y, "AVISTA LLC")
    y-= 10
    p.setFont("Arial", 10)
    p.drawString(80, y, "Direktor | Director | Директор")
    y -= 10
    p.drawString(80, y, invoice.director_name)


    # Main Header
    p.setFont("Arial", 10)
    p.drawString(60, 800, "www.bakustock.com")
    p.drawString(60, 788, "Tel: 050 406 30 77")

    p.setFont("Arial_Bold", 14)
    p.drawString(250, 800, "AVISTA LLC")

    p.setFont("Arial", 10)
    p.drawString(400, 800, "E-mail: avista@bakustock.com")
    p.drawString(400, 788, "E-mail: avista.mmc@gmail.com")

    p.setFont("Arial_Bold", 12)
    p.drawString(74, 740, "HESAB FAKTURA | INVOICE | СЧЁТ ФАКТУРА")

    p.showPage()
    p.save()
    
    return response


def delete_invoice(request, id):
    invoice = InvoiceModel.objects.get(id=id)
    invoice.delete()
    return redirect('view_all_invoices')
    
    
def edit_invoice(request, id):
    invoice = InvoiceModel.objects.get(id=id)
    products = Product.objects.filter(quote=invoice.quote)

    if request.method == 'POST':
        # Update Invoice
        invoice.invoice_number = request.POST.get('invoice_number')
        invoice.purchase_order = request.POST.get('purchase_order')
        invoice.invoice_date = request.POST.get('invoice_date')
        invoice.seller_name = request.POST.get('seller_name')
        invoice.buyer_name = request.POST.get('buyer_name')
        invoice.director_name = request.POST.get('director_name')
        invoice.bank_details = request.POST.get('bank_details')
        invoice.save()

        # Update Product 
        products_json = request.POST.get('products_json')
        print(type(products_json))
        if products_json:
            products_data = json.loads(products_json)
            print(type(products_data))
            for product_info in products_data:
                product_id = product_info.get('id')
                product_quantity = int(product_info.get('quantity'))
                product_price = int(product_info.get('price'))
                total = product_quantity * product_price
                if product_id:
                    product = Product.objects.get(id=product_id)
                    product.all_info = {
                        'productName': product_info.get('productName'),
                        'deliveryDate': product_info.get('deliveryDate'),
                        'quantity': product_info.get('quantity'),
                        'uom': product_info.get('uom'),
                        'price': product_info.get('price'),
                        'total': total,
                    }
                    product.save()
            return redirect('view_all_invoices')

    return render(request, 'invoices/edit_invoice.html', {'invoice': invoice, 'products': products})