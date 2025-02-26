from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.db.models import Q
from django.shortcuts import (
    render, 
    redirect
)

User = get_user_model()

def signin(request):
    next = request.GET.get('next')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_deleted:
                user.display_name = user.username
                user.save()
            login(request, user)
            return redirect(next or 'chat:room')

        messages.error(request, 'Incorrect username or password!')

    context = {'next': next}
    return render(request, 'chat/login.html', context)

def signup(request):
    next = request.GET.get('next')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            messages.error(request, 'Username/Email ID already taken.')
        
        else:
            user = User(username=username, email=email, display_name=username)
            user.set_password(password)
            user.save()

            login(request, user)
            return redirect(next or 'chat:room')  
             
    context = {'next': next}
    return render(request, 'chat/signup.html', context)

def signout(request):
    logout(request)
    return redirect('chat:index')
