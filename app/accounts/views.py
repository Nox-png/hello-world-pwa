from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.forms import LoginForm

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