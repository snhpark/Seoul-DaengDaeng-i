from django.shortcuts import render
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *

from rest_framework.decorators import api_view
from rest_framework import viewsets

import logging
import base64
from PIL import Image
import os
import numpy as np
import torch
from torch.utils.data import DataLoader
import torchvision
import torch.nn as nn
from torch.autograd import Variable
import torchvision.transforms as transforms
from numpy.linalg import norm
from numpy import dot
from math import radians, cos, sin, asin, sqrt

class PostViewSet(viewsets.ModelViewSet):
    queryset = Owner_post.objects.all()
    serializer_class = Owner_postSerializer


# Create your views here.
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            try: # 맞는 key를 가진 User가 있느냐
                user = User.objects.get(key = serializer.data['key'])
            except User.DoesNotExist:
                return Response(0, status = status.HTTP_201_CREATED)
            return Response(1, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def Dog_shelter_list(request):
    if request.method == 'GET':
        queryset = Dog_shelter.objects.all()
        serializer = Dog_shelterSerializer(queryset, many = True)
        logging.error(serializer.data[0]['shelter_name'])
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = Dog_shelterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

def haversine(currentLat, currentLng, shelterLat, shelterLng):
    # convert decimal degrees to radians
    currentLat, currentLng, shelterLat, shelterLng = map(radians, [currentLat, currentLng, shelterLat, shelterLng])
    # haversine formula
    dlon = shelterLat - currentLat
    dlat = shelterLng - currentLng
    a = sin(dlat/2)**2 + cos(currentLat) * cos(shelterLat) * sin(dlon/2)**2
    c = 2*asin(sqrt(a))
    km = 6367 * c
    return km

@api_view(['POST'])
def FindNearShelter(request):
    currentLocation = NearSerializer(data = request.data)
    if currentLocation.is_valid():
        queryset = Dog_shelter.objects.all()
        shelterList = Dog_shelterSerializer(queryset, many = True)
        logging.error(currentLocation.data)
        for i in currentLocation.data:
            logging.error(i)
        logging.error(len(currentLocation.data))
        logging.error(currentLocation.data['lat'])
        logging.error(currentLocation.data['lng'])
        logging.error(shelterList.data[0])
        logging.error(shelterList.data[0]['lat'])
        logging.error(type(currentLocation.data['lat']))
        logging.error(type(shelterList.data[0]['lat']))
#        logging.error(haversine(currentLocation.data['lat'],currentLocation.data['lng'], shelterList.data['lat'],shelterList.data['lng']))
        return Response(currentLocation.data, status = status.HTTP_201_CREATED)
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def owner_post_list(request):
    owner_posts = Owner_post.objects.all()
    serializer = Owner_postSerializer(owner_posts, many = True)
    return Response(serializer.data)
@api_view(['GET'])
def finder_post_list(request):
    finder_posts = Finder_post.objects.all()
    serializer = Finder_postSerializer(finder_posts, many = True)
    return Response(serializer.data)


@api_view(['POST'])
def owner_post_create(request):
    serializer = Owner_postSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()

        if serializer.data['image'] != "":
            os.makedirs('./media/owner/'+str(serializer.data['id']))
            output = open('media/owner/'+str(serializer.data['id'])+'/profile.jpg', 'wb+')
            output.write(base64.b64decode(serializer.data['image']))
            output.close()

            post = Owner_post.objects.get(id=serializer.data['id'])
            post.image = ""
            post.imageurl = 'http://210.107.198.174:8000/' + 'media/owner/' + str(serializer.data['id']) + '/profile.jpg'
            post.save()
        else:
            pass
        return Response(serializer.data, status = status.HTTP_201_CREATED)
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def finder_post_create(request):
    serializer = Finder_postSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()

        if serializer.data['image'] != "":
            os.makedirs('./media/finder/' + str(serializer.data['id']))
            output = open('media/finder/' + str(serializer.data['id']) + '/profile.jpg', 'wb+')
            output.write(base64.b64decode(serializer.data['image']))
            output.close()

            post = Finder_post.objects.get(id = serializer.data['id'])
            post.image = ""
            post.imageurl = 'http://210.107.198.174:8000/' + 'media/finder/' + str(serializer.data['id']) + '/profile.jpg'
            post.save()
        else:
            pass
        return Response(serializer.data, status = status.HTTP_201_CREATED)
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def post_filter(request):
    currentLocation = NearSerializer(data = request.data)
    if currentLocation.is_valid():  
        owner_posts = Owner_post.objects.filter(
                lat__gte = currentLocation.data['lat'] - 0.003,
                lat__lte = currentLocation.data['lat'] + 0.003,
                lng__gte = currentLocation.data['lng'] - 0.003,
                lng__lte = currentLocation.data['lng'] + 0.003
                )
        finder_posts = Finder_post.objects.filter(
                lat__gte = currentLocation.data['lat'] - 0.003,
                lat__lte = currentLocation.data['lat'] + 0.003,
                lng__gte = currentLocation.data['lng'] - 0.003,
                lng__lte = currentLocation.data['lng'] + 0.003
                )
        serializerOwner = Owner_postSerializer(owner_posts, many = True)
        serializerFinder = Finder_postSerializer(finder_posts, many = True)
        return Response(serializerOwner.data + serializerFinder.data, status = status.HTTP_201_CREATED)
    return Response(currentLocation.errors, status = status.HTTP_400_BAD_REQUEST)



dirnames=['치와와','골든리트리버','보스턴불독','포메라니안','말티즈','도베르만','비글','시베리안허스키','셰퍼드','시츄','푸들','코카스패니얼','콜리','요크셔테리어','퍼그']

loader = transforms.Compose([transforms.Scale(224), transforms.ToTensor()])

def image_loader(image_name):
    """load image, returns cuda tensor"""
    image = Image.open(image_name).convert('RGB')
    image = loader(image).float()
    image = Variable(image, requires_grad=True)
    image = image.unsqueeze(0)  #this is for VGG, may not be needed for ResNet
    return image

def cos_sim(A, B):
       return dot(A, B)/(norm(A)*norm(B))

@api_view(['POST'])
def classificationImage(request):
    getImage = GetImageSerializer(data = request.data)
    if getImage.is_valid():
        if getImage.data['image'] != "":
            output = open('media/classification.jpg', 'wb+')
            output.write(base64.b64decode(getImage.data['image']))
            output.close()

            # Classification
            model = torch.load('media/modeldir/flower_70.pth', map_location='cpu')
            image = image_loader('media/classification.jpg')
            outputs = model(image)
            
            sm = nn.Softmax()
            
            k = 3
            one,labelarr = torch.topk(outputs,k)
            problarr,two = torch.topk(sm(outputs),k)
            candi = []

            for i in range(k):
                x = problarr[0][i].__float__()
                candi.append([labelarr[0][i].__int__(),float("{0:.2f}".format(x)),dirnames[labelarr[0][i].__int__()]])

	    #print(candi[0][2])


            dogType = "abc";
            dogType = candi[0][2]

            return Response(dogType, status = status.HTTP_201_CREATED)
        else :
            logging.error("getImage.data['image'] is empty!!!!!")
    return Response(getImage.errors, status = status.HTTP_400_BAD_REQUEST)








