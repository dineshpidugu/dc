from django.shortcuts import render

# Create your views here.
def chat(r):
    return render(r,"index.html")