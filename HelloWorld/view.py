# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from .service import TemplateFetchServiceSingleton
# 
def fetch(request):
    sentence = request.GET.get('sentence');
    templateFetchService = TemplateFetchServiceSingleton();
    ret = templateFetchService.fetchTemplate(sentence);
    return HttpResponse(ret);

def upload(request):
    return HttpResponse("Hello world ! ");