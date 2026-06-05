from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from accounts.forms import LoginForm, UserProfileForm, UserUpdateForm

from accounts.models import UserProfile


PROFILE_IMAGE_PLACEHOLDER = b"""<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160" role="img" aria-label="Profilbild">
<rect width="160" height="160" rx="80" fill="#e9ecef"/>
<circle cx="80" cy="62" r="32" fill="#adb5bd"/>
<path d="M28 148c7-32 27-50 52-50s45 18 52 50" fill="#adb5bd"/>
</svg>"""

# Create your views here.
def loginView(request, template="accounts/login.html"):
    if request.user.is_authenticated:
        return redirect("/")
    
    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, "Ungültige Anmeldedaten.")
        else:
            messages.error(request, "Es ist ein Fehler bei der Validierung des Formulars aufgetreten.")
    
    
    context = {
        "form": form,
    }

    return render(request, template, context)

def logoutView(request):
    logout(request)
    return redirect("/")

@login_required
def profileView(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    statusMessage = None
    statusType = None

    if request.method == "POST":
        if request.POST.get("saveProfile") == "1":
            userForm = UserUpdateForm(request.POST, instance=user)
            profileForm = UserProfileForm()
            if userForm.is_valid():
                userForm.save()
                statusMessage = "Profil gespeichert."
                statusType = "success"
            else:
                statusMessage = "Profil konnte nicht gespeichert werden."
                statusType = "danger"
        elif request.POST.get("saveImage") == "1":
            userForm = UserUpdateForm(instance=user)
            profileForm = UserProfileForm(request.POST, request.FILES)
            if profileForm.is_valid():
                profileImage = profileForm.cleaned_data.get("profileImage")
                if profileImage:
                    profile.profileImage = profileImage.read()
                    profile.profileImageContentType = profileImage.content_type
                    profile.save()
                    statusMessage = "Profilbild gespeichert."
                    statusType = "success"
                    profileForm = UserProfileForm()
                else:
                    statusMessage = "Bitte ein Bild auswählen."
                    statusType = "warning"
            else:
                statusMessage = "Profilbild konnte nicht gespeichert werden."
                statusType = "danger"
    else:
        userForm = UserUpdateForm(instance=user)
        profileForm = UserProfileForm()

    context = {
        "userForm": userForm,
        "profileForm": profileForm,
        "statusMessage": statusMessage,
        "statusType": statusType,

    }
    return render(request, "accounts/profile.html", context)

@login_required
def profileImageView(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if profile is None or not profile.profileImage:
        return HttpResponse(PROFILE_IMAGE_PLACEHOLDER, content_type="image/svg+xml")
    contentType = profile.profileImageContentType or "image/png"
    return HttpResponse(profile.profileImage, content_type=contentType)