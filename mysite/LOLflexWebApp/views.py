from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse
import os

# Create your views here.

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent of the parent directory
grandparent_dir = os.path.dirname(os.path.dirname(current_dir))

# Construct the path to the CSV file
csv_file_path = os.path.join(grandparent_dir, 'tabelas', 'average.csv')

def home(request):
    tabela_medias = pd.read_csv(csv_file_path)
    dicionario_tabela_medias = tabela_medias.to_dict("records")

    sort_by = request.GET.get('sort_by')
    order = request.GET.get('order', 'asc')
    if sort_by:
        dicionario_tabela_medias.sort(key=lambda row: row[sort_by], reverse=(order == 'desc'))

    return render(request, 'home.html', {'data': dicionario_tabela_medias})




def table_view(request):
    tabela_medias = pd.read_csv(csv_file_path)
    dicionario_tabela_medias = tabela_medias.to_dict("records")
    return render(request, 'table.html', {'data': dicionario_tabela_medias})

