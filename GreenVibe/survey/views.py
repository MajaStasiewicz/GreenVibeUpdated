from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product, ProductStorage, UserItem
from .models import *
import logging
from django.db.models import F
from django.contrib import messages

question_number = 0
save_number = 0

logger = logging.getLogger(__name__)

def surveyHomePage(request):
    global question_number
    question_number = 0

    if request.method=="POST":
        request.session['answers'] = {}
        return redirect('/data/')

    return render(request, 'survey_home_page.html')

def data(request):
    if request.method=="POST":
        request.session['imie'] = request.POST['imie']
        request.session['weight'] = request.POST['waga']
        request.session['height'] = request.POST['wzrost']
        request.session['wiek'] = request.POST['wiek']
        return redirect('/question/')
    return render(request, 'data.html')
  
def questionBeggining(request):
    global question_number
    global save_number

    heading = Heading.objects.get(heading="PYTANIA WSTĘPNE")
    counter_base = Question.objects.filter(heading=heading)

    if question_number == 0:
        request.session['visits'] = 0

    request.session['visits'] = int(request.session.get('visits', 0)) + 1
    check = request.session['visits']

    if request.method == 'POST':
        question_number+=1
        answer = request.POST.get('odp')
        data = "PYTANIAWSTĘPNE" + str(question_number) + str(answer)
        request.session['answers'][f'answer_{save_number}'] = data
        save_number+=1
    if question_number != 0:
        if check > question_number:
            return redirect('/survey/')

    if question_number == counter_base.count(): 
        question_number = 0
        return redirect('/heading/')
    else:
        iterations = 0
        for question in counter_base:
            if iterations == question_number:
                questions = question
            iterations += 1
    return render(request, 'questions.html', {'Question': questions})

def heading(request):
    headings = Heading.objects.exclude(heading="PYTANIA WSTĘPNE")
    customer = str(request.session['imie'])
    return render(request, 'heading.html', {'klient': customer, 'headings':headings})

def checkboxes(request):
    if request.method=='POST':
        options=request.POST.getlist('option')      
        request.session['options'] = options
        if options==[]:
            return redirect('/heading/')
        else:
            url = f'/{str(options[0]).replace(" ", "")}/'
            return redirect(url)
    return render(request, 'heading.html')

def next(request):
    global question_number
    global save_number

    options = request.session.get('options', [])
    heading = Heading.objects.get(heading=options[0])
    counter_base = Question.objects.filter(heading=heading)

    if question_number == 0:
        request.session['visits'] = 0

    request.session['visits'] = int(request.session.get('visits', 0)) + 1
    check = request.session['visits']

    if request.method == 'POST':
        question_number+=1
        answer = request.POST.get('odp')
        data = str(str(options[0]).replace(" ", "")) + str(question_number) + str(answer)
        request.session['answers'][f'answer_{save_number}'] = data
        save_number+=1

    if question_number != 0:
        if check > question_number:
            return redirect('/survey/')

    if question_number == counter_base.count(): 
        options.pop(0)
        if options:
            url = f'/{str(options[0]).replace(" ", "")}/'
            question_number = 0
            return redirect(url)
        else:
            question_number = 0
            request.session['visits'] = 0
            return redirect('/saving/')
    else:
        iterations = 0
        for question in counter_base:
            if iterations == question_number:
                questions = question
            iterations += 1
    return render(request, 'questions.html', {'Question': questions})

def saving(request):
    check1 = 0
    counterMg = 0
    counterD3 = 0
    counterFe = 0
    counterC = 0
    counterHair = 0
    counterB12 = 0
    counterMobile = 0
    counterCa = 0

    request.session['visits'] = int(request.session.get('visits', 0)) + 1
    #check = request.session['visits']

    if request.method == 'POST': 
        request.session['visits'] = 0
        if request.user.is_authenticated:
            product_name = request.POST.get('product_name')
            product = Product.objects.get(name=product_name)
            product_price = product.price
            option = '60 tabletek'
            quantity = 1
            product_storage = ProductStorage.objects.get(product=product,option=option)

            if product_storage.storage != 0:
                user = request.user
                item, created = UserItem.objects.get_or_create(
                            product=product, user=user, option=option, price=product_price
                        )
                if not created:
                    item.quantity = F('quantity') + quantity
                    item.save()
                if created:
                    item.quantity = quantity
                    item.save()
                messages.success(request, ("Produkt został dodany do koszyka."))
                return redirect('/saving/')
            else:
                messages.success(request, ("Aktualnie brak na magazynie."))
                return redirect('/saving/')
        else:
            product_name = request.POST.get('product_name')
            product = Product.objects.get(name=product_name)
            product_price = product.price
            option = '60 tabletek'
            quantity = 1
            product_storage = ProductStorage.objects.get(product=product,option=option)
            
            if product_storage.storage != 0:
                product_price = "{:.2f}".format(float(product_price))
                cart = request.session.get('cart', [])
                existing_item = None
                for item in cart:
                    if item['id'] == product.id and item['name'] == product.name:
                        existing_item = item
                        break

                if existing_item:
                    item['quantity'] = item['quantity'] + int(quantity)
                else:
                    cart_item = {
                        'id': product.id,
                        'name': product.name,
                        'option': option,
                        'quantity': quantity,
                        'price': str(product_price).replace('.', ','),
                        'photo': product.photo.url,
                        'total_price': "{:.2f}".format(float(quantity) * float(product_price)),
                    }
                    cart.append(cart_item)

                request.session['cart'] = cart
                messages.success(request, ("Produkt został dodany do koszyka."))
                return redirect('/saving/')
            else:
                messages.success(request, ("Aktualnie brak na magazynie."))
                return redirect('/saving/')
        
    #if check > 1:
        #return redirect('/survey/')

    all = []
   
    weight = float(request.session['weight'])
    height = float(request.session['height'])
    heightM = float(height / 100)
    heightK = float(heightM ** 2)
    BMI = float(weight / heightK)
    BMIs = str(round(BMI, 1))
    BMIr = float(BMIs)
    all.append("Twoje BMI: " + BMIs)

    if BMIr < 18.5:
        all.append("Masz niedowagę. Warto zwrócić na to uwagę przy komponowaniu diety.")
    elif 18.5 <= BMIr <= 24.9:
        all.append("Twoja waga jest w normie.")
    elif 25 <= BMIr <= 29.9:
        all.append("Masz nadwagę w niewielkim stopniu. Warto zwrócić na to uwagę przy komponowaniu diety.")
    elif 30 <= BMIr <= 34.9:
        all.append("Masz nadwagę. Warto skonsultować się z dietetykiem i wprowadzić mniej kaloryczne produkty.")
    elif BMIr >= 35:
        all.append("Twoja waga wskazuje na otyłość. W pewnym momencie wysoka waga może prowadzić do różnych poważnych chorób. Warto wziąć to pod uwagę.")
    
    session_data = request.session.get('answers', {})

    for key, value in session_data.items():
        if "PYTANIAWSTĘPNE41" in value:
            all.append("WARTO ROZWAŻYĆ WPROWADZENIE WIĘKSZEJ ILOŚCI WARZYW DO DIETY.")

        if "PYTANIAWSTĘPNE31" in value:
            all.append("WARTO ROZWAŻYĆ WPROWADZENIE WIĘKSZEJ ILOŚCI PRODUKTÓW ZAWIERAJĄCYCH WAPŃ LUB ZAKUPIĆ PONIŻSZY SUPLEMENT.")

        if "PYTANIAWSTĘPNE21" in value:
            all.append("ZDROWIE ORGANIZMU TO NIE TYLKO ODPOWIEDNIA DIETA, ALE RÓWNIEŻ NIE KORZYSTANIE Z UŻYWEK TAKICH JAK PAPIEROSY. JEŚLI NIE JEST MOŻLIWE DLA CIEBIE RZUCENIE PALENIA, WARTO ROZWAŻYĆ OGRANICZENIE WYPALANYCH DZIENNIE PAPIEROSÓW.")

        if "PYTANIAWSTĘPNE11" in value:
            all.append("ZDROWIE ORGANIZMU TO NIE TYLKO ODPOWIEDNIA DIETA, ALE RÓWNIEŻ NIE KORZYSTANIE Z UŻYWEK TAKICH JAK ALKOHOL. OGRANICZENIE SPOŻYWANIA ALKOHOLU MOŻE ZNACZNIE POPRAWIĆ STAN ORGANIZMU.")
        
        if "ENERGIAISEN21" in value or "ENERGIAISEN22" in value:
            if counterFe != 1:
                all.append("Żelazo")
            check1 = 1
            counterFe = 1

        if "ENERGIAISEN11" in value or "ENERGIAISEN12" in value:
            if counterMg != 1:
                all.append("Magnez")
            check1 = 1
            counterMg = 1

        if "WŁOSYIPAZNOKCIE31" in value or "WŁOSYIPAZNOKCIE32" in value or "WŁOSYIPAZNOKCIE21" in value or "WŁOSYIPAZNOKCIE22" in value or "WŁOSYIPAZNOKCIE12" in value:
            if counterHair != 1:
                all.append("Kompleks włosy i paznokcie")
            check1 = 1
            counterHair = 1

        if "WŁOSYIPAZNOKCIE11" in value:
            all.append("SUGEROWANA JEST WIZYTA U DERMATOLOGA W CELU SPRAWDZENIA STANU SKÓRY GŁOWY.")

        if "PAMIĘĆISKUPIENIE31" in value or "ENERGIAISEN31" in value or "ENERGIAISEN32" in value or "ENERGIAISEN33" in value or "PYTANIAWSTĘPNE51" in value or "PYTANIAWSTĘPNE52" in value:
            if counterB12 != 1:
                all.append("B12")
            counterB12 = 1

        if "PAMIĘĆIKONCENTRACJA21" in value or "PAMIĘĆIKONCENTRACJA22" in value or "PAMIĘĆIKONCENTRACJA11" in value or "PAMIĘĆIKONCENTRACJA12" in value:
            if counterMobile != 1:
                all.append("ZBYT DUŻY CZAS KORZYSTANIA Z URZĄDZEŃ TAKICH JAK KOMPUTER CZY TELEFON MOŻE PRZYCZYNIAĆ SIĘ DO PROBLEMÓW Z KONCENTRACJĄ. STARAJ SIĘ OGRANICZAĆ TO DO MINIMUM.")
            counterMobile = 1

        if "KOŚCIISTAWY31" in value or "KOŚCIISTAWY11" in value or "KOŚCIISTAWY12" in value or "PYTANIAWSTĘPNE31" in value:
            if counterCa != 1:
                all.append("Wapń")
            check1 = 1
            counterCa = 1

        if "KOŚCIISTAWY21" in value or "OGÓLNEZDROWIE33" in value or "ODPORNOŚĆ31" in value or "ODPORNOŚĆ32" in value or "ODPORNOŚĆ21" in value or "ODPORNOŚĆ22" in value:
            if counterD3 != 1:
                all.append("D3")
            check1 = 1
            counterD3 = 1

        if "ODPORNOŚĆ31" in value or "OGÓLNEZDROWIE11" in value or "ODPORNOŚĆ32" in value or "ODPORNOŚĆ21" in value or "ODPORNOŚĆ22" in value:
            if counterC != 1:
                all.append("C")
            check1 = 1
            counterC = 1

        if "STRES31" in value:
            all.append("STARAJ SIĘ UNIKAĆ SYTUACJI STRESOWYCH. ZBYT DUŻA ILOŚĆ STRESU MOŻE PROWADZIĆ DO WIELU RÓŻNYCH, NIERAZ POWAŻNYCH CHORÓB.")

        if "STRES11" in value:
            all.append("POSTARAJ SIĘ WPROWADZIĆ WYKONYWANIE ĆWICZEŃ RELAKSACYJNYCH.")

        if "OGÓLNEZDROWIE23" in value:
            all.append("POSTARAJ SIĘ LEPIEJ ZADBAĆ O SWOJĄ DIETĘ. TO W JAKI SPOSÓB ODŻYWIAMY SWOJE CIAŁO JEST KLUCZOWĄ KWESTIĄ UTRZYMANIA ZDROWIA.")

    if check1 == 0:
        all.append("Multiwitamina")
    
    products = []
    sorted_all = []
    for product in all:
        try:
            suplement = get_object_or_404(Product, name=product)
            if suplement is not None:
                products.append(suplement)
        except:
            sorted_all.append(product)
    return render(request, 'saving.html', {'all':sorted_all, 'products':products})

