from django.shortcuts import render

def public_page(request):
    return render(request, "p.html")

def admin_page(request):
    return render(request, "admin.html")
