from django.shortcuts import render
import pandas as pd
from interactive import Retrival_Interface
from BM25 import Retrieval_base
import pickle
from django.conf import settings
import os
from django.http import HttpResponse

#file_ = open(os.path.join(settings.BASE_DIR, 'filename'))

# Create your views here.
def index(request):
    return render(request, 'games/form.html')

def search(request):
    template_name = "games/game_list.html"
    if request.method == 'GET':
        if request.GET.get("textfield"):
            query = request.GET.get('textfield', None)
            try:
                with open('Retrieval_base.pickle', 'rb') as handle:
                    Rb = pickle.load(handle)
            except:
                Rb = Retrieval_base()
                with open('Retrieval_base.pickle', 'wb') as handle:
                    pickle.dump(Rb, handle, protocol=pickle.HIGHEST_PROTOCOL)
            

            Ri = Retrival_Interface(Rb, query, 1000)
            Ri.Base_Retrieve_List()
            with open('Ri.pickle', 'wb') as handle:
                pickle.dump(Ri, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Add suggenstion list
            suggestion_list = Ri.query_suggestion(5)

            result_dict = Ri.retrieve_detail_info(50).to_dict()
            results = {}
            for appid in result_dict['name']:
                results[appid] = []
                for key in result_dict:
                    results[appid].append(result_dict[key][appid])
            #do something with user
            return render(request, template_name, {'results':results, 'suggestion_list': suggestion_list,
                                                    'query':Ri.query, 'final_query':Ri.final_query,
                                                    'if_corrected':Ri.query_correction_flag})
    elif request.method == 'POST':
        if request.POST.get("update"):
            with open('Ri.pickle', 'rb') as handle:
                Ri = pickle.load(handle)
            appid = request.POST.get("parameter")
            Ri.Panalize_Retrieve_List(int(appid))
            suggestion_list = Ri.query_suggestion(5)

            with open('Ri.pickle', 'wb') as handle:
                pickle.dump(Ri, handle, protocol=pickle.HIGHEST_PROTOCOL)
            result_dict = Ri.retrieve_detail_info(50).to_dict()
            results = {}
            for appid in result_dict['name']:
                results[appid] = []
                for key in result_dict:
                    results[appid].append(result_dict[key][appid])
            #do something with user
            return render(request, template_name, {'results':results, 'suggestion_list':suggestion_list, 
                                                    'query':Ri.query,'final_query':Ri.final_query,
                                                    'if_corrected':Ri.query_correction_flag})
            #html = "<html><body>It is appid %s.}</body></html>" % rank
            #return HttpResponse(html)
    else:
        return render(request, 'games/form.html')
