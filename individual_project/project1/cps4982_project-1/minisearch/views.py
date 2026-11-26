from django.shortcuts import render
from .search_call import search, read_file


def search_index(request):

    results=[]
    search_term=""
    context={'results':{},'count':0,'search_term':'empty'}
    if request.GET.get('keyword'):
        search_term=request.GET['keyword']
        results=search(query=search_term,topN=20)
        print(results)
        context={'results':results[1],'count':results[0],'search_term':search_term}
    return render(request,'index.html',context)


# Create your views here.
def index(request):
    results=[]
    search_term=""
    context={'results':{},'count':0,'search_term':'empty'}
    if request.GET.get('keyword'):
        search_term=request.GET['keyword']
        results=search(query=search_term,topN=20)
        print(results)
        context={'results':results[1],'count':results[0],'search_term':search_term}
    return render(request,'index.html',context)

def read(request, filename):

    data = read_file(filename)
    file = "http://localhost:8000/static/gutenberg/" + filename
    return render(request,"index_read.html",{"filename":file, "results":data})