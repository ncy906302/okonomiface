from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from .forms import UploadModelForm

from .models import Photo
from django.shortcuts import redirect

from seetaface.api import *
import os
import json
from cs import *

import urllib.request
from bs4 import BeautifulSoup

data={}

def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def index(request):
    # with open('data.json') as json_file:
    #     data = json.load(json_file)
    global data
    if len(data)==0:
        with open('data.json') as json_file:
            data = json.load(json_file)

    photos = Photo.objects.all()
    form = UploadModelForm()
    template = loader.get_template('faceApp/index.html')
    if request.method == "POST":
        photos.delete()
        form = UploadModelForm(request.POST, request.FILES)
        print(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/faceApp/result/')
    context = {
        'photos': photos,
        'form': form
    }
    
    return render(request, 'faceApp/index.html', context)

# def index(request):
#     template = loader.get_template('faceApp/index.html')
#     context = {}
#     return HttpResponse(template.render(context,request))

def RemoveAllPhoto(request):
    Photo.objects.all().delete()
    return HttpResponse('remove all complete')

def result(request):
    init_mask = FACE_DETECT|FACERECOGNITION|LANDMARKER5
    seetaFace = SeetaFace(init_mask)
    global data
    with open('av_jouyu_name_id.json') as json_file:
        av_id = json.load(json_file)
    image = imread('media/'+str(Photo.objects.all()[0].image))
    # image = imread('mari.jpg')
    detect_result = seetaFace.Detect(image)
    face1 = detect_result.data[0].pos
    points1 = seetaFace.mark5(image,face1)
    feature1 = seetaFace.Extract(image,points1)


    similar_dict = {}
    similar_list = []
    for i in data:
        similar_temp = []
        for j in data[i]:
            similar = CalculateSimilarity(j,feature1[:])
            similar_temp.append(similar)
        similar_avg = sum(similar_temp)/len(similar_temp)
        # print(similar_avg,i)
        similar_dict[str(similar_avg)] = i
        similar_list.append(similar_avg)
    temp_id=''

    top_5_list=[]

    for i in range(8):
        similar_max = str(max(similar_list))
        top_5_list.append([similar_dict[similar_max],av_id[similar_dict[similar_max]]])

        del similar_dict[str(max(similar_list))]
        similar_list.remove(max(similar_list))
    
    photos = Photo.objects.all()
    form = UploadModelForm()
    if request.method == "POST":
        photos.delete()
        form = UploadModelForm(request.POST, request.FILES)
        # print(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/faceApp/result/')
    context = {
        'top_5' : top_5_list,
        'form' : form,
    }

    return render(request, 'faceApp/result.html', context)
    # return HttpResponse(str(Photo.objects.all()[0].image)+'<br>'+temp_id+url)

def ajax(request):
    if request.method == "POST":
        print(request.POST['name'],request.POST['id'])
    name = request.POST['name']
    av_id = request.POST['id']
    # response_data = {'name':name,'av_id':av_id}
    # return HttpResponse(json.dumps(response_data), content_type="application/json")
    
    url = 'https://www.dmm.co.jp/digital/videoa/-/list/narrow/=/article=actress/id='+av_id+'/limit=30/n1=DgRJTglEBQ4GpoD6,YyI,qs_/'
    # print(url)
    html =  urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    src = soup.find_all('p',class_="tmb")
    

    pic_url = []
    for j in src:
        temp = j.find_all('img')[0].get_attribute_list('src')[0]
        pic_url.append(temp)
    
    context = {
        'name' : name,
        'pic_url' : pic_url,
    }
    return HttpResponse(json.dumps(context), content_type="application/json")