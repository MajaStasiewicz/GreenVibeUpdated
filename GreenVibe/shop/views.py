from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from shop.forms import RegisterUserForm
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
import logging
from shop.models import *
from products.models import *
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views import View
from .utils import generate_discount_code

logger = logging.getLogger(__name__)

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

def handler403(request, exception):
    return render(request, '403.html', status=403)

def handler400(request, exception):
    return render(request, '400.html', status=400)

def handler401(request, exception):
    return render(request, '401.html', status=401)

def handler503(request, exception):
    return render(request, '503.html', status=503)

def handler429(request, exception):
    return render(request, '429.html', status=429)

def handler502(request, exception):
    return render(request, '502.html', status=502)

def handler504(request, exception):
    return render(request, '504.html', status=504)

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_success')

class PasswordsResetView(PasswordResetView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('registration/reset.html')
    
def password_success(request):
    return render(request, 'changeSuccess.html', {})

def index(request):
    active_banners = Banner.objects.filter(is_active=True)

    all_categories = Category.objects.all()
    bestsellers_by_category = {}

    for category in all_categories:
        bestsellers = Product.objects.filter(category=category).order_by('-sold')[:3]
        bestsellers_by_category[category.name] = bestsellers

    return render(request, 'home.html', {'bestsellers_by_category': bestsellers_by_category, 'active_banners': active_banners})

def home(request):
    active_banners = Banner.objects.filter(is_active=True)

    all_categories = Category.objects.all()
    bestsellers_by_category = {}

    for category in all_categories:
        bestsellers = Product.objects.filter(category=category).order_by('-sold')[:3]
        bestsellers_by_category[category.name] = bestsellers

    return render(request, 'home_copy.html', {'bestsellers_by_category': bestsellers_by_category, 'active_banners': active_banners})

def aboutUs(request):
    return render(request, 'aboutUs.html')

def contact(request):
    if request.method == 'POST':
        message = request.POST.get('body')
        email = request.POST.get('email')
        try:
            validate_email(email)
        except ValidationError as e:
            messages.success(request, ("Niepoprawny adres email!"))
            return render(request, 'contact.html', {'message': 'message'})
        
        subject = 'Prośba o kontakt'
        message = 'Wiadomość wysłana z maila: ' + email + ' Zapytanie: ' + message
        from_email = email
        recipient_list = ['greenvibeteam@gmail.com']
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        messages.success(request, ("Wiadomość została wysłana!"))
        return redirect('/contact/')
    return render(request, 'contact.html')

def rules(request):
    return render(request, 'rules.html')

def pay(request):
    return render(request, 'pay.html')

def returns(request):
    return render(request, 'returns.html')

def saveBlank(request):
    return render(request, 'saveBlank.html')

def change(request):
    return render(request, 'change.html')

def accountShop(request):
    user = request.user
    username = request.user.username
    orders = OrderHistory.objects.filter(user=user)
    orders_by_date = orders.order_by('-order__date')
    reviews = productReview.objects.filter(user=username)
    try:
        user_address = get_object_or_404(UserAddress, user=user)
    except:
        user_address = None

    if request.method == 'POST':
        user = request.user
        username = request.user.username
        user_data = request.POST.get('user_data')
        if user_data == "save":
            name = request.POST.get('name')
            surname = request.POST.get('surname')
            email = request.POST.get('email')
            telephone = request.POST.get('telephone')
            street = request.POST.get('street')
            number = request.POST.get('number')
            city = request.POST.get('city')
            postcode = request.POST.get('postcode')

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
        else:
            orders = OrderHistory.objects.filter(user=user)
            orders_by_date = orders.order_by('-order__date')
            reviews = productReview.objects.filter(user=username)

            rate = request.POST.get('rate')
            comment = request.POST.get('comment')
            productId = request.POST.get('productId')
            product = get_object_or_404(Product, name=productId)
            item, created = productReview.objects.get_or_create(
                            product=product, user=username, comment=comment, rate=rate
                        )
            item.save()
            
            OrderHistory.objects.filter(user=user, product=product, review=False).update(review=True)
            messages.success(request, ("Dziękujemy za dodanie opinii do produktu!"))
            return render(request, 'accountShop.html', {'username':username, 'orders_by_date': orders_by_date, 'reviews': reviews, 'user': user, 'message': 'message'})

    return render(request, 'accountShop.html', {'user_address': user_address, 'username': username, 'orders_by_date': orders_by_date, 'reviews': reviews, 'user': user})

def delete_account(request):
    if request.user.is_authenticated:
        user = request.user
        logout(request)  
        user.delete()  
        messages.success(request, ("Konto zostało usunięte!"))
        return redirect('/login/')
    return render(request, 'accountShop.html')
        
def reward(request, parametr):
    if request.method == 'POST': 
        email = request.POST.get('email')

        try:
            validate_email(email)
        except ValidationError as e:
            messages.success(request, ("Niepoprawny adres email!"))
            return render(request, 'reward.html', {'message': 'message', 'parametr': parametr})
        
        emailCheck = ZapisNewsletter.objects.filter(email=email)
        if not emailCheck:
            newsletterSave = ZapisNewsletter(email=email)
            newsletterSave.save()

            discount_code = generate_discount_code()
            subject = 'KOD RABATOWY'
            message = 'TWÓJ KOD RABATOWY NA: ' + str(parametr) + '% TO: ' + str(discount_code)
            from_email = 'greenvibeteam@gmail.com'
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            logger.info("tuuuuuuuuuuuuuuuu")
            logger.info(discount_code)
            logger.info(parametr)
            code = Code(code=discount_code, value=parametr, is_used=False)
            code.save()
            messages.success(request, ("Kod został wysłany na podany email!"))
            return redirect('/homeCopy/')
        else:
            messages.success(request, ("Ten email jest już zapisany do newslettera!"))
            url = f'/reward/{parametr}/'
            return redirect(url)
    return render(request, 'reward.html', {'parametr':parametr})

def newsletter(request):
    parametr = request.GET.get('parametr')
    if parametr != 'niestety':
        url = f'/reward/{parametr}/'
        return redirect(url)

def loginSite(request):
    if request.method == 'POST':  
        login_choice = request.POST.get('loginChoice')
        if login_choice == "login_register":
            pass
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
        
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                parametr = 'ODŻYWKI BIAŁKOWE'
                url = f'/products/{parametr}/'
                return redirect(url)
            else:
                messages.success(request, ("Niepoprawna nazwa użytkownika lub hasło!"))
                return redirect('/login/')
    return render(request, 'login.html')

def loginSiteCart(request):
    if request.method == 'POST':  
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
            
        if user is not None:
            login(request, user)
            return redirect('/cart/')
        else:
            logger.info("tutta")
            messages.success(request, ("Niepoprawna nazwa użytkownika lub hasło!"))
            return redirect('/loginSiteCart/')
    return render(request, 'login.html')

def logoutSite(request):
    logout(request)
    messages.success(request, ("Zostałeś wylogowany!"))
    return redirect('/login/')

def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        emailCheck = request.POST.get('email')
        nameCheck = request.POST.get('username')
        try:
            validate_email(emailCheck)
        except ValidationError as e:
            messages.success(request, ("Niepoprawny adres email!"))
            form = RegisterUserForm()
            return render(request, 'register.html', {'message': 'message','form':form})
        
        if User.objects.filter(email=emailCheck).exists():
            messages.success(request, ("Email istnieje!"))
            return redirect('/register/')
        elif User.objects.filter(username=nameCheck).exists(): 
            messages.success(request, ("Nazwa użytkownika istnieje!"))
            return redirect('/register/')
        else:
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False
                user.save()
                activateEmail(request, user, form.cleaned_data.get('email'))
                return redirect('/login/')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
                        return redirect('/register/')
    else:
        form = RegisterUserForm()
    return render(request, 'register.html', {
       'form':form,
    })

def activateEmail(request, user, to_email):
    subject = 'Potwierdzenie założenia konta'
    message = render_to_string("activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
        })

    from_email = 'greenvibeteam@gmail.com'
    recipient_list = [to_email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
   
    messages.success(request, "Sprawdz maila i potwierdź, aby sie zalogować!")

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Dziękujemy za potwierdzenie emaila!")
        return redirect('/login/')
    else:
        messages.error(request, "Link jest niepoprawny lub wygasł!")

    return redirect('/home/')


