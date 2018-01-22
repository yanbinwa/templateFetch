# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from .service import TemplateFetchServiceSingleton
import json
# 
templateFetchService = TemplateFetchServiceSingleton();
templateFetchService.uploadTrainModel();

def fetch(request):
    sentence = request.GET.get('sentence');
    ret = templateFetchService.fetchTemplate(sentence);
    return HttpResponse(json.dumps(ret));

def upload(request):
    return HttpResponse("Hello world ! ");