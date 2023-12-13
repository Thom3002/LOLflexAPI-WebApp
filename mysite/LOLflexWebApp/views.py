from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse

# Create your views here.

def home(request):
    tabela_medias = pd.read_csv('C:/Users/Thomas/Desktop/ProjetosPessoais/RiotAPI/src/tabelas/average.csv') # trocar para path relativo no futuro 
    
    dicionario_tabela_medias = tabela_medias.to_dict("records") # records = lista de dicionários
    return render(request, 'home.html', {'data': dicionario_tabela_medias})

