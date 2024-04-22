from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import *
from django.db.models import F
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import logging
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.db.models import Avg, Q
import stripe

logger = logging.getLogger(__name__)

newprice = 0
counter = 0
totalPrice = 0
check = 0

stripe.api_key = 'sk_test_51OSI7sFPjlUSYagTXnxTdFRqyOda6ZmfcOF5SOSvJmOQfPdINr2yGXIVsuCZfCfqWUme5U7N3aexQklFYNw2VXry00nREQV5oi'

def paySite(request):
    stripe_public_key = 'pk_test_51OSI7sFPjlUSYagTUUDX7n384Ham8qfjl2yrzHcUDNS7y5AQgCiElVxAMkYUbL5QRlq4guWRe52yIynAo9zA1mBF00UI2cgNV9'

    if request.method == 'POST':           
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        street = request.POST.get('street')
        number = request.POST.get('number')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        delivery_method = request.POST.get('delivery')
        price = request.POST.get('newPriceSave')
        priceSend = request.POST.get('price')
        
        price = "{:.2f}".format(float(price)).replace('.', ',')

        try:
            validate_email(email)
        except ValidationError as e:
            deliveryMethod = DeliveryMethod.objects.all()
            messages.error(request, "Niepoprawny adres email!")
            if request.user.is_authenticated:
                user = request.user
                try:
                    user_address = get_object_or_404(UserAddress, user=user)
                except:
                    user_address = None
                return render(request, 'order.html', {'message': 'message', 'deliveryMethod': deliveryMethod, 'total': priceSend, 'user_address': user_address})
            else:
                return render(request, 'order.html', {'message': 'message', 'deliveryMethod': deliveryMethod, 'total': priceSend})
            
        if request.user.is_authenticated:
            user = request.user
            user_address, created = UserAddress.objects.get_or_create(
                user=user,
                defaults={
                    'name': name,
                    'surname': surname,
                    'email': email,
                    'telephone': telephone,
                    'street': street,
                    'number': number,
                    'city': city,
                    'postcode': postcode,
                }
            )

            if not created:
                user_address.name = name
                user_address.surname = surname
                user_address.email = email
                user_address.telephone = telephone
                user_address.street = street
                user_address.number = number
                user_address.city = city
                user_address.postcode = postcode

            user_address.save()

        context = {'name':name, 'surname':surname, 'email':email, 'telephone':telephone,
                   'street':street, 'number':number, 'city':city, 'postcode':postcode, 'price':totalPrice, 'delivery':delivery_method}
                   
    return render(request, 'paySite.html', {'stripe_public_key':stripe_public_key, 'name':name, 'surname':surname, 'email':email, 'telephone':telephone,
                   'street':street, 'number':number, 'city':city, 'postcode':postcode, 'price':price, 'delivery':delivery_method})

def pay_submit(request):
    global newprice
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        street = request.POST.get('street')
        number = request.POST.get('number')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        delivery_method = request.POST.get('delivery')
        price = request.POST.get('price')

        delivery = get_object_or_404(DeliveryMethod, method=delivery_method)
        session_key = request.session.session_key

        if request.user.is_authenticated:
            user = request.user
            products = UserItem.objects.filter(user=user)
            item = Order(user=user, name=name, surname=surname, email=email, telephone=telephone,
                        street=street, number=number, city=city, postcode=postcode, delivery_method=delivery)
            item.save()

            user_items = UserItem.objects.filter(user=user)
            order = Order.objects.filter(user=user).order_by('-date').first()
            priceToOrder = price.replace(',', '.')
            for user_item in user_items:
                order_history = OrderHistory(
                    order=order,
                    product=user_item.product.name,
                    user=user_item.user,
                    option=user_item.option,
                    quantity=user_item.quantity,
                    price=user_item.price,
                    priceOrder=priceToOrder
                )
                order_history.save()     
        else:
            item = Order(key_session=session_key, name=name, surname=surname, email=email, telephone=telephone,
                        street=street, number=number, city=city, postcode=postcode, delivery_method=delivery)
            item.save()
            cart = request.session.get('cart', [])
            order = Order.objects.filter(key_session=session_key).order_by('-date').first()
            priceToOrder = price.replace(',', '.')
            
            for user_item in cart:
                order_history = OrderUserSession(
                    order=order,
                    product=user_item['name'],
                    key_session=session_key,
                    option=user_item['option'],
                    quantity=user_item['quantity'],
                    price=float(user_item['price'].replace(',', '.')),
                    priceOrder=priceToOrder
                )
                order_history.save()  

        code = Code.objects.filter(key=session_key).first()
        if code is not None:
            code.delete()

        current_month = datetime.now().replace(day=1).strftime('%B')
        monthly_summary, created = MonthlyOrderSummary.objects.get_or_create(month=current_month)
        newprice = str(price)
        delivery_price = Decimal(delivery.price)
        newprice = Decimal(newprice.replace(",", ".")) - delivery_price
        monthly_summary.total_value += newprice 
        monthly_summary.save()

        if request.user.is_authenticated:
            subject = 'ZAMÓWIENIE'
            message = render_to_string("orderEmail.html", {
                'user': user.username,
                'products': UserItem.objects.filter(user=user),
                'total': sum(product.total_price for product in products),
                'order': Order.objects.filter(user=user).order_by('-id').first(),
                'totalPrice': price
                })

            from_email = 'greenvibeteam@gmail.com'
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            cart = UserItem.objects.filter(user=user)

            for user_item in cart:
                product = user_item.product
                product.sold += user_item.quantity
                product.save()
                productStorage = get_object_or_404(ProductStorage, option=user_item.option, product__name=user_item.product.name)
                current_storage = float(productStorage.storage)
                updated_storage = current_storage - float(user_item.quantity)
                productStorage.storage = updated_storage
                productStorage.save()
            if UserItem.objects.filter(user=user).exists():
                UserItem.objects.filter(user=user).delete()
        else:
            cart = request.session.get('cart', [])
            subject = 'ZAMÓWIENIE'
            message = render_to_string("orderEmail.html", {
                'products': request.session.get('cart', []),
                'total': sum(product['total_price'] for product in cart),
                'order': Order.objects.filter(key_session=session_key).order_by('-id').first(),
                'totalPrice': price
                })

            from_email = 'greenvibeteam@gmail.com'
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            for user_item in cart:
                product = Product.objects.get(id=user_item['id'])
                product.sold += user_item['quantity']
                product.save()
                productStorage = get_object_or_404(ProductStorage, option=user_item['option'], product__name=user_item['name'])
                current_storage = float(productStorage.storage)
                updated_storage = current_storage - float(user_item['quantity'])
                productStorage.storage = updated_storage
                productStorage.save()
            if 'cart' in request.session:
                del request.session['cart']
    return render(request, 'pay_submit.html')

def products(request, category):
    filter_flavour = "-- wybierz --"
    filter_query = "-- wybierz --"
    search_query = ""
    price1 = 0
    price2 = 1000

    all_categories = Category.objects.all()
    category_obj = get_object_or_404(Category, name=category)
    category_id = category_obj.id
    products_list = Product.objects.filter(category=category_id, is_active=True)

    flavours = Product.objects.filter(category__name='ODŻYWKI BIAŁKOWE').values_list('flavour', flat=True)
    unique_flavours = set(flavours)
    list_unique_flavours = list(unique_flavours)
    
    sorting = request.GET.get('sorting', '-- wybierz --')
    price1str = request.GET.get('price1')
    price2str = request.GET.get('price2')
    flavourProducts = request.GET.get('flavourProducts')

    if price1str and price2str:
        price1 = float(price1str)
        price2 = float(price2str)
        products_list = products_list.filter(price__gte=price1) 
        products_list = products_list.filter(price__lte=price2)
    
    if flavourProducts:
        if flavourProducts != "-- wybierz --":
            products_list = products_list.filter(flavour=flavourProducts)
        filter_flavour = flavourProducts

    if sorting == '-- wybierz --':
        products_list = products_list
    elif sorting == 'najniższa cena':
        products_list = products_list.order_by('price')
        filter_query = "najniższa cena"
    elif sorting == 'najwyższa cena':
        products_list = products_list.order_by('-price')
        filter_query = "najwyższa cena"
    elif sorting == 'najlepsze opinie':
        products_list = products_list.annotate(avg_rate=Avg('productreview__rate')).order_by('-avg_rate')
        filter_query = "najlepsze opinie"

    if request.method == 'POST':
        if 'filter_button' in request.POST:
            price1str = request.POST.get('price1')
            price2str = request.POST.get('price2')
            flavourProducts = request.POST.get('flavourProducts')
            sorting_from_post = request.POST.get('sortingFilter')
            
        if 'sort_button' in request.POST:
            price1str = request.POST.get('priceSort1')
            price2str = request.POST.get('priceSort2')
            flavourProducts = request.POST.get('flavour')
            sorting_from_post = request.POST.get('sorting')

        if price1str and price2str:
            price1 = float(price1str)
            price2 = float(price2str)
            products_list = products_list.filter(price__gte=price1) 
            products_list = products_list.filter(price__lte=price2)
            
        if flavourProducts:
            if flavourProducts != "-- wybierz --":
                products_list = products_list.filter(flavour=flavourProducts)
            filter_flavour = flavourProducts
        
        if sorting_from_post:
            sorting = sorting_from_post
            if sorting == 'najniższa cena':
                products_list = products_list.order_by('price')
                filter_query = "najniższa cena"
            elif sorting == 'najwyższa cena':
                products_list = products_list.order_by('-price')
                filter_query = "najwyższa cena"
            elif sorting == 'najlepsze opinie':
                products_list = products_list.annotate(avg_rate=Avg('productreview__rate')).order_by('-avg_rate')
                filter_query = "najlepsze opinie"

    if request.method == 'GET':
        if 'search_button' in request.GET:
            search_query = request.GET.get('search_query')
        if search_query:
            products_list = products_list.filter(Q(name__icontains=search_query))

    if request.method == 'GET':
        filter_flavour = "-- wybierz --"
        filter_query = sorting
    
    paginator = Paginator(products_list, 9)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'category': category_id,
        'list_unique_flavours': list_unique_flavours,
        'filter_query': filter_query,
        'filter_flavour': filter_flavour,
        'price1': int(price1),
        'price2': int(price2),
        'sorting': sorting,
        'search_query': search_query,
        'all_categories': all_categories,
    }

    return render(request, 'products.html', context)

def cartSummary(request):
    global newprice
    global totalPrice
    global counter
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            code = request.POST.get('code')
            price = request.POST.get('price')
            try:
                discount_code = get_object_or_404(Code, code=code)
                if discount_code:
                    session_key = request.session.session_key
                    discount_code.key = session_key
                    discount_code.save()
                    codeValue = float(discount_code.value / 100)
                    price_with_dot = float(price.replace(',', '.'))
                    priceValue = float(codeValue) * float(price_with_dot)
                    totalPrice = float(price_with_dot) - float(priceValue)  
                    response_data = {'success': True, 'total': totalPrice}
                    return JsonResponse(response_data)
            except Code.DoesNotExist:
                return JsonResponse({'success': False})

        
        check = 0
        user = request.user
        if UserItem.objects.filter(user=user).exists():
            products = UserItem.objects.filter(user=user)
            if counter == 0:
                total = sum(
                    product.total_price for product in products
                )
            else:
                total = totalPrice
            context = {'products':products, 'total':total}
        
    else:
        if request.method == 'POST':
            code = request.POST.get('code')
            price = request.POST.get('price')
        
            try:
                discount_code = get_object_or_404(Code, code=code, is_used=False)
                if discount_code:
                    session_key = request.session.session_key
                    discount_code.key = session_key
                    discount_code.save()
                    codeValue = float(discount_code.value / 100)
                    price_with_dot = float(price.replace(',', '.'))
                    priceValue = float(codeValue) * float(price_with_dot)
                    totalPrice = float(price_with_dot) - float(priceValue)  
                    response_data = {'success': True, 'total': totalPrice}
                    return JsonResponse(response_data)
            except Code.DoesNotExist:
                return JsonResponse({'success': False})
              
        check = 0
        cart = request.session.get('cart', [])
  
        total = "{:.2f}".format(sum(float(product['total_price']) for product in cart)).replace('.', ',')
        context = {'products':cart, 'total':total}
        
    return render(request, 'cartSummary.html', context)

def moreP(request, product_id):
    if request.method == 'POST':
        option = request.POST.get('option')
        price = request.POST.get('priceSend')
        quantity = request.POST.get('quantitySend')

        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            option = request.POST.get('option')
            price = request.POST.get('priceSend')
            quantity = request.POST.get('quantitySend')

            price = float(price.replace(',', '.'))

            try:
                product = get_object_or_404(Product, id=product_id)
                product_id = product.pk
            except Product.DoesNotExist:
                product_id = None

            user = request.user
            
            counterStorage = get_object_or_404(ProductStorage, product__id=product_id, option=option)
            quantityStorage = float(counterStorage.storage)

            item, created = UserItem.objects.get_or_create(
                        product=product, user=user, option=option, price=price
                    )
            if not created:
                quantitySum = float(quantity) + float(item.quantity)
                if quantitySum > quantityStorage:
                    quantity = quantityStorage
                    item.quantity = quantity
                else:
                    item.quantity = F('quantity') + quantity
                item.save()
            if created:
                item.quantity = quantity
                item.save()

            messages.success(request, ("Produkt został dodany do koszyka."))
            url = f'/moreP/{product_id}/'
            return redirect(url)
        else:
            cart = request.session.get('cart', [])
            existing_item = None
            for item in cart:
                if item['id'] == product.id and item['name'] == product.name and item['option'] == option:
                    existing_item = item
                    counterStorage = get_object_or_404(ProductStorage, product__id=item['id'], option=item['option'])
                    quantityStorage = float(counterStorage.storage) 
                    break

            if existing_item:
                quantitySum = float(quantity) + float(item['quantity'])
                if quantitySum > quantityStorage:
                    quantity = quantityStorage
                    item['quantity'] = int(quantity)
                else:
                    new_quantity = int(existing_item['quantity']) + int(quantity)
                    existing_item['quantity'] = int(existing_item['quantity']) + int(quantity)
                    existing_item['total_price'] = float(new_quantity) * float(existing_item['price'].replace(',', '.'))
            else:
                new_price = "{:.2f}".format(float(price)).replace('.', ',')
                cart_item = {
                    'id': product.id,
                    'name': product.name,
                    'option': option,
                    'quantity': quantity,
                    'price': new_price,
                    'photo': product.photo.url,
                    'total_price': "{:.2f}".format(float(quantity) * float(price)),
                }
                cart.append(cart_item)

            request.session['cart'] = cart
            
            messages.success(request, ("Produkt został dodany do koszyka."))
            url = f'/moreP/{product_id}/'
            return redirect(url)

    product = get_object_or_404(Product, id=product_id)
    average_rating = productReview.objects.filter(product=product).aggregate(Avg('rate'))
    average = average_rating['rate__avg']
    if average:
        average = round(average, 1)

    if request.user.is_authenticated:
        user = request.user
        username = request.user.username
        all_reviews = productReview.objects.filter(product=product)
        other_reviews = all_reviews.exclude(user=request.user)
        sorted_user_reviews = productReview.objects.filter(product=product,user=username).order_by('date')
        sorted_other_reviews = other_reviews.order_by('date')
        reviews = list(sorted_user_reviews) + list(sorted_other_reviews)
    else:
        reviews = productReview.objects.filter(product=product).order_by('date')

    productStorage = ProductStorage.objects.filter(product__id=product_id)

    first_product = ProductStorage.objects.filter(product__id=product_id).first()
    first_product_storage = first_product.storage

    username = request.user.username
    if username:
        context = {'product': product, 'reviews': reviews, 'average': average, 'productStorage': productStorage, 'username':username, 'first_product_storage':first_product_storage}
    else:
        context = {'product': product, 'reviews': reviews, 'average': average, 'productStorage': productStorage, 'username':username, 'first_product_storage':first_product_storage}
    return render(request, 'moreP.html', context)

def view_cart(request):
    cart = 0
    products = 0
    cartCheck = request.session.get('cart', [])
    if request.user.is_authenticated and cartCheck:
        user = request.user
        for item in cartCheck:
            product_id = item['id']
            product = get_object_or_404(Product, id=product_id)
            option = item['option']
            quantity = item['quantity']
            price = float(item['price'].replace(',', '.'))

            counterStorage = get_object_or_404(ProductStorage, product__id=product_id, option=option)
            quantityStorage = float(counterStorage.storage)                    

            item, created = UserItem.objects.get_or_create(
                        product=product, user=user, option=option, price=price
                    )
            if not created:
                quantitySum = float(quantity) + float(item.quantity)
                if quantitySum > quantityStorage:
                    quantity = quantityStorage
                    item.quantity = quantity
                else:
                    item.quantity = F('quantity') + quantity
                item.save()
            if created:
                item.quantity = quantity
                item.save()
            request.session.pop('cart', None)

    if request.user.is_authenticated:
        user = request.user
        if UserItem.objects.filter(user=user).exists():
            products = UserItem.objects.filter(user=user)

            product_names = [product.product.name for product in products]

            productStorage = ProductStorage.objects.filter(product__name__in=product_names)

            total = sum(
                product.total_price for product in products
            )
            
            context = {'products':products, 'total':total, 'productStorage':productStorage}

            if request.method == 'POST':
                product_pk = request.POST.get('delete_product')
                quantities = request.POST.getlist('quantitySend')
                
                if product_pk is None:
                    for index, product in enumerate(products):
                        product_id = product.id
                        item = UserItem.objects.get(pk=product_id)
                        item.quantity = quantities[index]
                        item.save()
                        total = sum(
                            product.total_price for product in products
                        )
                        
                        context = {'products':products, 'total':total}
                    return redirect('/cartSummary/')
                else:
                    item = UserItem.objects.filter(pk=product_pk)
                    item.delete()
                    return redirect('/cart/')
    else:
        cart = request.session.get('cart', [])
            
        product_names = [item.get('name', 'Unknown') for item in cart]

        productStorage = ProductStorage.objects.filter(product__name__in=product_names)

        total = "{:.2f}".format(sum(float(product['total_price']) for product in cart)).replace('.', ',')
            
        if request.method == 'POST':
            product_id = request.POST.get('delete_product')
            quantities = request.POST.getlist('quantitySend')
  
            if product_id is None:
                for item in cart:
                    item['quantity'] = int(quantities[cart.index(item)])
                    item['total_price'] = float(item['price'].replace(',', '.'))*float(quantities[cart.index(item)])
                    total = "{:.2f}".format(sum(float(product['total_price']) for product in cart)).replace('.', ',')
                context = {'cart':cart, 'total':total}
                return redirect('/choice/')
            else:
                cart = request.session.get('cart', [])
                index_to_remove = None
                for index, item in enumerate(cart):
                    if str(item.get('id')) == str(product_id):
                        index_to_remove = index
                        break

                if index_to_remove is not None:
                    del cart[index_to_remove]
                    request.session['cart'] = cart

                return redirect('/cart/')
        
    context = {'cart':cart}
    if products !=0:
        context = {'products':products, 'productStorage':productStorage, 'total': total}
    if cart !=0:
        context = {'products':products, 'productStorage':productStorage, 'cart': cart, 'total': total}

    return render(request, 'cart.html', context)

def order_choice(request):
    if request.user.is_authenticated or request.method == 'POST':
        if request.user.is_authenticated:
            user = request.user
            products = UserItem.objects.filter(user=user)
            total = sum(
                    product.total_price for product in products
                )
            newpricesave = total
            return render(request, 'cartSummary.html', {'total':newpricesave, 'products':products}) 
        else:
            cart = request.session.get('cart', [])
            if newprice:
                newpricesave = newprice
            else:
                total = "{:.2f}".format(sum(float(product['total_price']) for product in cart)).replace('.', ',')
                newpricesave = total
            return render(request, 'cartSummary.html', {'total':newpricesave, 'products':cart}) 
    return render(request, 'choice.html')

def order(request):
    stripe_public_key = 'pk_test_51OSI7sFPjlUSYagTUUDX7n384Ham8qfjl2yrzHcUDNS7y5AQgCiElVxAMkYUbL5QRlq4guWRe52yIynAo9zA1mBF00UI2cgNV9'

    newprice = request.GET.get('newPriceSave')
    if request.user.is_authenticated:
        user = request.user
        products = UserItem.objects.filter(user=user)
        total = sum(
                product.total_price for product in products
            )
        try:
            user_address = get_object_or_404(UserAddress, user=user)
        except:
            user_address = None
    
    else:
        cart = request.session.get('cart', [])
        total = "{:.2f}".format(sum(float(product['total_price']) for product in cart)).replace('.', ',')
        products = cart
        user_address = ''
    
    if newprice:
        newpricesave = newprice
    else:
        newpricesave = total
        newprice = total
    
    deliveryMethod = DeliveryMethod.objects.all()
    context = {'user_address':user_address, 'products':products, 'total':total, 'newpricesave': newpricesave, 'stripe_public_key':stripe_public_key, 'deliveryMethod':deliveryMethod}

    return render(request, 'order.html', context)

@login_required
def deleteReview(request, review_id):
    user = request.user
    username = request.user.username
    productCheck = get_object_or_404(productReview, id=review_id)
    product_id = productCheck.product.id
    product = get_object_or_404(Product, id=product_id)
    OrderHistory.objects.filter(user=user, product=product, review=True).update(review=False)

    if productCheck.user == username:
        productCheck.delete()

    url = f'/moreP/{product_id}/'
    return redirect(url)
