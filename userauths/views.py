
from django.shortcuts import redirect, render
from django.contrib import messages
from core.models import FriendRequest, Post
from userauths.forms import UserRegisterForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout

from userauths.models import Profile, User
from django.contrib.auth.decorators import login_required





def RegisterView(request, *args, **kwargs):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey {request.user.username}, you are already logged in")
        return redirect('core:feed')   

    form = UserRegisterForm(request.POST or None)
    
    if form.is_valid():
        form.save()
        full_name = form.cleaned_data.get('full_name')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')

        user = authenticate(email=email, password=password)
        login(request, user)

        messages.success(request, f"Hi {request.user.username}, your account have been created successfully.")

        profile = Profile.objects.get(user=request.user)
        profile.full_name = full_name
        profile.phone = phone
        profile.save()

        return redirect('core:feed')
    
    context = {
        'form':form
    }
    
    return render(request, 'userauths/sign-up.html', context)



def LoginView(request):
    if request.user.is_authenticated:
        return redirect('core:feed')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You are Logged In")
                return redirect('core:feed')
            else:
                messages.error(request, 'Username or password does not exit.')
                return redirect('userauths:sign-up')

        except:
            messages.error(request, 'User does not exist')
            return redirect('userauths:sign-up')
            
    return HttpResponseRedirect("/")
    


def LogoutView(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect("userauths:sign-up")



@login_required
def my_profile(request):
    profile = request.user.profile
    posts = Post.objects.filter(active=True, user=request.user)

    context = {
        "posts":posts,
        "profile":profile,
    }
    return render(request, "userauths/my-profile.html", context)



@login_required
def friend_profile(request, username):
    profile = Profile.objects.get(user__username=username)
    posts = Post.objects.filter(active=True, user=profile.user)

    # Send Friend Request Feature
    bool = False
    bool_friend = False

    sender = request.user
    receiver = profile.user
    bool_friend = False
    print("========================  Add or cancel")
    try:
        friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver)
        if friend_request:
            bool = True
        else:
            bool = False
    except:
        bool = False
    

    # End Send Friend Request Feature
    print("Bool =======================", bool)
    

    context = {
        "posts":posts,
        "profile":profile,
        "bool_friend":bool_friend,
        "bool":bool,
    }
    return render(request, "userauths/friend-profile.html", context)
