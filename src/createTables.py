from riotwatcher import LolWatcher, ApiError
import pandas as pd
from datetime import datetime
import os

# macros
API_KEY = 'RGAPI-22d19514-3d78-48af-aabc-9cedd7ecce0e' # API key da Riot Games
SUMMONER_NAME = 'xLegenderx' # Nome do jogador cujo histórico de partidas será analisado
SEASON_ATUAL = True # Variável que indica se a partida é da season atual (True) ou não (False)

# Lista de nomes que serão analisados caso estejam na partida do jogador (SUMMONER_NAME)
interested_names = ["lucjam", "xLegenderx", "Living Paradox", "mikasa 7", "NeoLight", "Kuroda el Bruto", "Tom Platz", "dudinha", "EU COMO DUDINHA", "Kolaltia", "mikasa ツ", "tsidkenu963", "Taylor Swiftness"]

watcher = LolWatcher(API_KEY)
my_region = 'br1'

# Verifica se a chave da API é valida
try:
    me = watcher.summoner.by_name(my_region, SUMMONER_NAME)
except ApiError as err:
    if err.response.status_code == 403:
        print("The API key is not valid.")
    else:
        raise

# Pega o histórico de partidas do jogador
my_matches = watcher.match.matchlist_by_puuid(my_region, me['puuid'])

# Cria os dataFrames que serão utilizados
df = pd.DataFrame(columns=["MatchNumber", "SummonerName", "Role", "Champion", "Kills", "Deaths", "Assists","KDA", "CS","CS/min", "Date"])
df_provisorio = pd.DataFrame(columns=["MatchNumber", "SummonerName", "Role", "Champion", "Kills", "Deaths", "Assists","KDA", "CS","CS/min", "Date"])
match_index = 0
num_participantes = 0
aram_count = 0

# Verifica cada partida do histórico do jogador (últimas 20 partidas)
for match in my_matches:
    print("Analysing match " + str(match_index) + "\n******************\n")
    match_detail = watcher.match.by_id(my_region, match)
    timestamp_ms = match_detail['info']['gameEndTimestamp']
    timestamp_s = timestamp_ms / 1000.0  # Convert from ms to s
    date = datetime.fromtimestamp(timestamp_s)  
    print("DATA " + str(date))
    
    # Verifica se o jogo é da season atual (depois de 08/01/2023)
    compare_date = datetime.strptime('08/01/2023', '%m/%d/%Y')

    if date > compare_date:
        SEASON_ATUAL = True
    else:
        print("MATCH BEFORE 08/01/2023")
        SEASON_ATUAL = False
    
    # Verifica se a partida é uma partida clássica
    if(match_detail['info']['gameMode'] != 'CLASSIC'):
        print("Match " + str(match_index) + " is not a classic match. Skipping...")
        if match_detail['info']['gameMode'] == 'ARAM':
            print("Match " + str(match_index) + " is an ARAM match. Skipping...")
            aram_count += 1
        match_index += 1
        continue
    for participant in match_detail['info']['participants']:
        summoner_name = participant['summonerName']
        # print("****participants summoner name: " + participant['summonerName'])
        if summoner_name in interested_names:
            print("Summoner " + summoner_name + " is in the list of interested names. Adding to the table...")
            
            role = participant['individualPosition']
            total_minions_killed = participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
            cs_per_min = total_minions_killed / (match_detail['info']['gameDuration'] / 60)
            kda = (participant['kills'] + participant['assists']) / participant['deaths'] if participant['deaths'] != 0 else participant['kills'] + participant['assists']
            
            if (role == 'UTILITY'):
                role = 'SUPPORT'
            elif (role == 'BOTTOM'):
                role = 'ADC'
                
            participant_row = {
                'MatchNumber': "match " + str(match_index),
                'SummonerName': summoner_name,
                'Role': role,
                'Champion': participant['championName'],
                'Kills': participant['kills'],
                'Deaths': participant['deaths'],
                'Assists': participant['assists'],
                'KDA': kda,
                'CS': total_minions_killed,
                'CS/min' : cs_per_min,
                'Date': date
            }
            num_participantes += 1
            df_new_row = pd.DataFrame(participant_row, index=[match_index])
            
            # Exclude empty or all-NA columns before the concat operation
            df_provisorio = df_provisorio.dropna(how ='all', axis=1)
            df = df.dropna(how = 'all', axis = 1)
            
            df_provisorio = pd.concat([df_provisorio, df_new_row])
    
    # Somente adiciona na tabela se a partida possuir 3 ou mais participantes da lista de nomes interessados
    if num_participantes >= 3 and SEASON_ATUAL: 
        print("A partida " + str(match_index) + " tem " + str(num_participantes) + " participantes. Adicionando a tabela final...")
        df = pd.concat([df, df_provisorio])
    num_participantes = 0
    match_index += 1


# Remove linhas duplicadas
df = df.drop_duplicates()

# Agrupa a tabela de partidas por role para cada jogador, somando os valores
sum_df = df.groupby(['SummonerName', 'Role'])[['Kills', 'Deaths', 'Assists', 'KDA', 'CS', 'CS/min']].sum().reset_index()
# print(sum_df)

# Conta o número de partidas por role para cada jogador
matches_per_role = df.groupby(['SummonerName', 'Role']).size().reset_index(name='Matches')

# Calcula a média de cada jogador por role
average_df = df.groupby(['SummonerName', 'Role'])[['Kills', 'Deaths', 'Assists','KDA', 'CS', 'CS/min']].mean().astype(float).round(1).reset_index()

# Calcula o KDA de cada jogador pela média de kills, deaths e assists (KDA = (Kills + Assists) / Deaths)
average_df['KDA'] = average_df.apply(lambda row: (row['Kills'] + row['Assists']) / row['Deaths'] if row['Deaths'] != 0 else 0, axis=1).round(1)
print(average_df)

# Adiciona a coluna de número de partidas na tabela de médias
average_df = pd.merge(average_df, matches_per_role, on=['SummonerName', 'Role'])
# print(average_df)

# Converte as tabelas para csv
sum_df.to_csv('tabelas/grouped.csv', index=False)
average_df.to_csv('tabelas/average.csv', index=False)
df.to_csv('tabelas/matches.csv', index=False)

print("******\nARAM count: " + str(aram_count))