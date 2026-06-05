from django.shortcuts import render, redirect

# Create your views here.
def index(request, template='web/base.html'):
    if not request.user.is_authenticated:
         return redirect("/accounts/login")
    return render(request, template)