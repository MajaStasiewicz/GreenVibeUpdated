from django.shortcuts import render
from .models import *

def training(request):
    woman = Video.objects.filter(caption="woman")
    womanAbs = Video.objects.filter(caption="womanAbs")
    womanChest = Video.objects.filter(caption="womanChest")
    womanBack = Video.objects.filter(caption="womanBack")
    womanHips = Video.objects.filter(caption="womanHips")
    womanLegs = Video.objects.filter(caption="womanLegs")

    man = Video.objects.filter(caption="man")
    manAbs = Video.objects.filter(caption="manAbs")
    manChest = Video.objects.filter(caption="manChest")
    manBack = Video.objects.filter(caption="manBack")
    manHips = Video.objects.filter(caption="manHips")
    manLegs = Video.objects.filter(caption="manLegs")

    videos = Video.objects.all()

    return render(request, 'training.html',{"videos":videos})