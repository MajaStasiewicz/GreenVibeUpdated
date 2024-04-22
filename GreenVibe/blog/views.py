from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from blog.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from django.db.models import Count, Avg
import logging

logger = logging.getLogger(__name__)

roomSend = 0
plannerPopup = ' '

def blog(request):
    latestPost = Post.objects.latest('created_at')

    all_posts = Post.objects.order_by('-created_at')
    
    for post in all_posts:
        reviews = Review.objects.filter(post=post).order_by('created_at')
        sum = 0
        for review in reviews:
            sum += review.rate

        counter = len(reviews)
        if sum != 0:
            rate = sum/counter
        else:
            rate = 0
        round_rate = round(rate, 1)
        post.average = round_rate
        post.save()

    posts = all_posts[1:4]
    context = {'latestPost':latestPost, 'posts':posts}
    return render(request, 'bposts.html', context)

def more(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user.is_authenticated:
        user = request.user
        all_reviews = Review.objects.filter(post=post)
        other_reviews = all_reviews.exclude(user=request.user)
        sorted_user_reviews = Review.objects.filter(post=post,user=user).order_by('created_at')
        sorted_other_reviews = other_reviews.order_by('created_at')
        reviews = list(sorted_user_reviews) + list(sorted_other_reviews)
    else:
        reviews = Review.objects.filter(post=post).order_by('created_at')
        user=1

    sum = 0
    for review in reviews:
        sum += review.rate

    counter = len(reviews)
    if sum != 0:
        rate = sum/counter
    else:
        rate = 0
    round_rate = round(rate, 1)

    return render(request, 'more.html', {'post':post, 'reviews':reviews, 'round_rate':round_rate, 'user':user})

def ranking(request):
    top_posts = Post.objects.annotate(avg_rate=Avg('review__rate')).order_by('-avg_rate')[:3]

    top_users_by_posts = User.objects.annotate(total_posts=Count('post')).order_by('-total_posts')[:3]

    top_users_by_avg_rate = User.objects.annotate(avg_rate=Avg('post__review__rate')).order_by('-avg_rate')[:3]

    context = {
        'top_posts': top_posts,
        'top_users_by_posts': top_users_by_posts,
        'top_users_by_avg_rate': top_users_by_avg_rate,
    }

    return render(request, 'ranking.html', context)

def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            post = get_object_or_404(Post, id=post_id)
            user = request.user
            comment = request.POST.get('comment')
            rate = request.POST.get('rate')

            comment = Review(post=post,user=user,comment=comment,rate=rate)
            comment.save()
            messages.success(request, ("Dziękujemy za dodanie komentarza!"))
            url = f'/more/{post_id}/'
            return redirect(url)
    else:
        messages.success(request, ("Musisz być zalogowany!"))
        url = f'/more/{post_id}/'
        return redirect(url)
    return render(request, 'comment.html')

def account(request):
    if request.user.is_authenticated:
        user = request.user

        checkF = 'F1'
        checkM = 'M1'
        plannerF = Planner.objects.filter(button=checkF,user=user).exists()
        plannerM = Planner.objects.filter(button=checkM,user=user).exists()

        if plannerF:
            pass
        else:
            textbox = 'PROMOCJA'
            textarea = 'Zapraszamy na zakupy!'
            button = 'F1'
            planner = Planner(user=user,title=textbox,value=textarea,button=button)
            planner.save()

        if plannerM:
            pass
        else:
            textbox = 'NOWOŚCI'
            textarea = 'Zapraszamy na zakupy! Nowe produkty!'
            button = 'M1'
            planner = Planner(user=user,title=textbox,value=textarea,button=button)
            planner.save()

        post = Post.objects.filter(user=user).order_by('-created_at').first()

        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        if created:
            user_profile.delete()
            person = UserProfile(user=user)
            person.save()
            user_profile = UserProfile.objects.get(user=user)
        
    else:
        return redirect('/noaccount/')
    return render(request, 'account.html', {'post':post, 'user_profile':user_profile})

@login_required
def postCreate(request):
    if request.user.is_authenticated:
        user = request.user
        rooms = Room.objects.all()
        if request.method == 'POST':
            title = request.POST.get('title')
            body = request.POST.get('body', '')
            topic = request.POST.get('topic')
            topic = Room.objects.filter(name=topic).first()
            
            postSave = Post(title=title,user=user,topic=topic,body=body)
            
            postSave.save()
            messages.success(request, ("Opublikowałeś post!"))
            return redirect('/blog/')
    return render(request, 'postCreate.html', {'rooms':rooms})

def noaccount(request):
    return render(request, 'noaccount.html')

def allPosts(request):
    posts = Post.objects.all().order_by('-created_at')
    rooms = Room.objects.all()
    if request.method == 'POST':
        topic = request.POST.get('topic')
        topic = Room.objects.filter(name=topic).first()
        #topic = room.id

        if topic=="Wszystkie":
            posts = Post.objects.all().order_by('-created_at')
        else:
            posts = Post.objects.filter(topic=topic).order_by('-created_at')
    return render(request, 'allPosts.html', {'posts':posts, 'rooms':rooms})

@login_required
def myPosts(request):
    if request.user.is_authenticated:
        user = request.user
        posts = Post.objects.filter(user=user).order_by('-created_at')

    return render(request, 'myPosts.html', {'posts':posts})

@login_required
def deletePost(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user == request.user:
        post.delete()

    return redirect('/myPosts/')

@login_required
def deleteReview(request, post_id):
    review = get_object_or_404(Review, id=post_id)
    post = review.post.id

    if review.user == request.user:
        review.delete()
    
    url = f'/more/{post}/'
    return redirect(url)

@login_required
def deleteAnswer(request, post_id):
    answer = get_object_or_404(Answer, id=post_id)
    review = answer.review  
    post = review.post.id 

    if answer.user == request.user:
        answer.delete()
    
    url = f'/more/{post}/'
    return redirect(url)

@login_required
def avatarChange(request, user_id):
    user = User.objects.get(id=user_id)

    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()
            return redirect('/accountBlog/')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'avatarChange.html', {'form': form})

@login_required
def answerReview(request, post_id):
    review = get_object_or_404(Review, id=post_id)
    post = review.post.id
    user = request.user

    if request.method == 'POST':
        comment = request.POST.get('comment')
        commentReview = Answer(review=review,user=user,comment=comment)
        commentReview.save()
    
    url = f'/more/{post}/'
    return redirect(url)

def messenger(request):
    rooms = Room.objects.all()
    return render(request, 'messenger.html', {'rooms':rooms})

def roomShow(request, room_id):
    global roomSend
    roomSend = room_id
    room = get_object_or_404(Room, id=room_id)  
    messages = Message.objects.filter(room=room)
    user = request.user
    username = user.username
    return render(request, 'messages.html', {'messages':messages, 'room':room_id, 'username':username, 'roomN':room})

def send(request):
    global roomSend
    if request.method == 'POST':
        room = get_object_or_404(Room, id=roomSend)
        user = request.user
        message = request.POST['message']
        messageSave = Message(user=user,room=room,value=message)
        messageSave.save()
        success = 'wreszczie'
        return HttpResponse(success)

def getMessages(request, room_id):
    user = request.user.username
    room = get_object_or_404(Room, id=room_id)  
    messages = Message.objects.filter(room=room)
    messages_data = list(messages.values('value', 'date', 'user__username'))

    if messages:
        formatted_messages = []
        for message in messages:
            formatted_message = {
                'value': message.value,
                'date': message.date.strftime("%H:%M"),  
                'user__username': message.user.username,
                'user': user
            }
            formatted_messages.append(formatted_message)

    if not formatted_messages:
        return JsonResponse({"messages": "Brak wiadomości."})
    else:
        user_messages = []
        other_users_messages = []

        if message.user == request.user:
                user_messages.append(formatted_message)
        else:
            other_users_messages.append(formatted_message)

        response_data = {
            "user_messages": user_messages,
            "other_users_messages": other_users_messages
        }

        return JsonResponse({"messages": formatted_messages})

@login_required
def planner(request):
    global plannerPopup
    user = request.user
    
    buttonsM = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10']
    plannersM = {}
    plannersMMandatory = {}
    for button in buttonsM:
        plannersM[button] = Planner.objects.filter(button=button, user=user).exists()
        plannersMMandatory[button] = PlannerMandatory.objects.filter(button=button).exists()
        if plannersM[button]:
            plannersM[button] = get_object_or_404(Planner, button=button, user=user)
        elif plannersMMandatory[button]:
            plannersM[button] = get_object_or_404(PlannerMandatory, button=button)
        else:
            plannersM[button] = '+'

    buttonsTU = ['TU1', 'TU2', 'TU3', 'TU4', 'TU5', 'TU6', 'TU7', 'TU8', 'TU9', 'TU10']
    plannersTU = {}
    plannersTUMandatory = {}
    for button in buttonsTU:
        plannersTU[button] = Planner.objects.filter(button=button, user=user).exists()
        plannersTUMandatory[button] = PlannerMandatory.objects.filter(button=button).exists()
        if plannersTU[button]:
            plannersTU[button] = get_object_or_404(Planner, button=button, user=user)
        elif plannersTUMandatory[button]:
            plannersTU[button] = get_object_or_404(PlannerMandatory, button=button)
        else:
            plannersTU[button] = '+'

    buttonsW = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10']
    plannersW = {}
    plannersWMandatory = {}
    for button in buttonsW:
        plannersW[button] = Planner.objects.filter(button=button, user=user).exists()
        plannersWMandatory[button] = PlannerMandatory.objects.filter(button=button).exists()
        if plannersW[button]:
            plannersW[button] = get_object_or_404(Planner, button=button, user=user)
        elif plannersWMandatory[button]:
            plannersW[button] = get_object_or_404(PlannerMandatory, button=button)
        else:
            plannersW[button] = '+'

    buttonsTH = ['TH1', 'TH2', 'TH3', 'TH4', 'TH5', 'TH6', 'TH7', 'TH8', 'TH9', 'TH10']
    plannersTH = {}
    plannersTHMandatory = {}
    for button in buttonsTH:
        plannersTH[button] = Planner.objects.filter(button=button, user=user).exists()
        plannersTHMandatory[button] = PlannerMandatory.objects.filter(button=button).exists()
        if plannersTH[button]:
            plannersTH[button] = get_object_or_404(Planner, button=button, user=user)
        elif plannersTHMandatory[button]:
            plannersTH[button] = get_object_or_404(PlannerMandatory, button=button)
        else:
            plannersTH[button] = '+'
        
    buttonsF = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10']
    plannersF = {}
    plannersFMandatory = {}
    for button in buttonsF:
        plannersF[button] = Planner.objects.filter(button=button, user=user).exists()
        plannersFMandatory[button] = PlannerMandatory.objects.filter(button=button).exists()
        if plannersF[button]:
            plannersF[button] = get_object_or_404(Planner, button=button, user=user)
        elif plannersFMandatory[button]:
            plannersF[button] = get_object_or_404(PlannerMandatory, button=button)
        else:
            plannersF[button] = '+'

    buttonsSA = ['SA1', 'SA2', 'SA3', 'SA4', 'SA5', 'SA6', 'SA7', 'SA8', 'SA9', 'SA10']
    plannersSA = {}
    plannersSAMandatory = {}
    for button in buttonsSA:
        plannersSA[button] = Planner.objects.filter(button=button, user=user).exists()
        plannersSAMandatory[button] = PlannerMandatory.objects.filter(button=button).exists()
        if plannersSA[button]:
            plannersSA[button] = get_object_or_404(Planner, button=button, user=user)
        elif plannersSAMandatory[button]:
            plannersSA[button] = get_object_or_404(PlannerMandatory, button=button)
        else:
            plannersSA[button] = '+'

    buttonsSU = ['SU1', 'SU2', 'SU3', 'SU4', 'SU5', 'SU6', 'SU7', 'SU8', 'SU9', 'SU10']
    plannersSU = {}
    plannersSUMandatory = {}
    for button in buttonsSU:
        plannersSU[button] = Planner.objects.filter(button=button, user=user).exists()
        plannersSUMandatory[button] = PlannerMandatory.objects.filter(button=button).exists()
        if plannersSU[button]:
            plannersSU[button] = get_object_or_404(Planner, button=button, user=user)
        elif plannersSUMandatory[button]:
            plannersSU[button] = get_object_or_404(PlannerMandatory, button=button)
        else:
            plannersSU[button] = '+'

    context = {'plannersM':plannersM, 'plannersTU':plannersTU, 'plannersW':plannersW, 'plannersTH':plannersTH,
               'plannersF':plannersF, 'plannersSA':plannersSA, 'plannersSU':plannersSU, 'planner':plannerPopup}
    return render(request, 'planner.html', context)

@login_required
def plannerSave(request):
    user = request.user
    textarea = request.GET.get('textarea')
    textbox = request.GET.get('textbox')
    button = request.GET.get('buttonId')
    cleaned_textbox = textbox.strip()
    cleaned_textarea = textarea.strip()
        
    planner = Planner.objects.filter(button=button, user=user).exists()
    plannerMandatory = PlannerMandatory.objects.filter(button=button).exists()
    if plannerMandatory:
        plannerMandatory = PlannerMandatory.objects.filter(button=button)
        plannerMandatoryButton = plannerMandatory.first().button
    else:
        plannerMandatoryButton = 0

    if button != plannerMandatoryButton:     
        if cleaned_textbox == '' and cleaned_textarea == '':
            if cleaned_textbox == '' and planner:
                planner = get_object_or_404(Planner, button=button, user=user)
                planner.delete()
        elif cleaned_textbox == '' and cleaned_textarea != '':
            if planner:
                textbox = 'Brak tytułu...'
                planner = get_object_or_404(Planner, button=button, user=user)
                planner.delete()
                planner = Planner(user=user,title=textbox,value=textarea,button=button)
                planner.save()
            else:
                textbox = 'Brak tytułu...'
                planner = Planner(user=user,title=textbox,value=textarea,button=button)
                planner.save()
        else:
            if planner:
                planner = get_object_or_404(Planner, button=button, user=user)
                planner.delete()
                planner = Planner(user=user,title=textbox,value=textarea,button=button)
                planner.save()
            else:
                planner = Planner(user=user,title=textbox,value=textarea,button=button)
                planner.save()

    return redirect('/planner/')

def deletePlanner(request):
    user = request.user
    user_planners = Planner.objects.filter(user=user)
    user_planners.delete()
    return redirect('/planner/')
