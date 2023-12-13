from riotwatcher import LolWatcher, ApiError
import pandas as pd
from datetime import datetime

API_KEY = 'RGAPI-9bcfbf80-3881-4a06-81e0-b12703c43d3f'
SUMMONER_NAME = 'mikasa 7'
SEASON_ATUAL = True
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

my_matches = watcher.match.matchlist_by_puuid(my_region, me['puuid'])
df = pd.DataFrame(columns=["MatchNumber", "SummonerName", "Role", "Champion", "Kills", "Deaths", "Assists","KDA", "TotalMinionsKilled", "Date"])
df_provisorio = pd.DataFrame(columns=["MatchNumber", "SummonerName", "Role", "Champion", "Kills", "Deaths", "Assists","KDA", "TotalMinionsKilled", "Date"])
match_index = 0
num_participantes = 0
aram_count = 0
for match in my_matches:
    print("Analysing match " + str(match_index) + "\n******************\n")
    match_detail = watcher.match.by_id(my_region, match)
    timestamp_ms = match_detail['info']['gameEndTimestamp']
    timestamp_s = timestamp_ms / 1000.0  # Convert from ms to s
    date = datetime.fromtimestamp(timestamp_s)  
    # print("DATA " + str(date))
    # Create a datetime object for 08/01/2023
    compare_date = datetime.strptime('08/01/2023', '%m/%d/%Y')

    # Check if date is after 08/01/2023
    if date > compare_date:
        # print("Date is after 08/01/2023")
        # print(date)
        SEASON_ATUAL = True
    else:
        print("Date is not after 08/01/2023")
        # print(date)
        SEASON_ATUAL = False
    # print(match_detail)
    if(match_detail['info']['gameMode'] != 'CLASSIC'):
        print("Match " + str(match_index) + " is not a classic match. Skipping...")
        if match_detail['info']['gameMode'] == 'ARAM':
            print("Match " + str(match_index) + " is an ARAM match. Skipping...")
            aram_count += 1
        match_index += 1
        continue
    for participant in match_detail['info']['participants']:
        summoner_name = participant['summonerName']
        print("****particpants summoner name: " + participant['summonerName'])
        if summoner_name in interested_names:
            print("Summoner " + summoner_name + " is in the list of interested names. Adding to the table...")
            role = participant['individualPosition']
            if (role == 'UTILITY'):
                role = 'SUPPORT'
            participant_row = {
                'MatchNumber': "match " + str(match_index),
                'SummonerName': summoner_name,
                'Role': role,
                'Champion': participant['championName'],
                'Kills': participant['kills'],
                'Deaths': participant['deaths'],
                'Assists': participant['assists'],
                'KDA': (participant['kills'] + participant['assists']) / participant['deaths'] if participant['deaths'] != 0 else participant['kills'] + participant['assists'],
                'TotalMinionsKilled': participant['totalMinionsKilled'],
                'Date': date
            }
            num_participantes += 1
            if participant_row['Role'] == 'Invalid':
                print("Invalid role for " + participant_row['SummonerName'] + " in match " + str(match_index))
            df_new_row = pd.DataFrame(participant_row, index=[match_index])
            df_provisorio = pd.concat([df_provisorio, df_new_row])
            
    if num_participantes >= 3 and SEASON_ATUAL: # Verifica se possui 3 ou mais participantes
        print("A partida " + str(match_index) + " tem " + str(num_participantes) + " participantes. Adicionando a tabela final...")
        df = pd.concat([df, df_provisorio])
    num_participantes = 0
    match_index += 1


# Limita a quantidade de casas decimais para 2
# pd.set_option('display.float_format', '{:.2f}'.format) 

# Remove linhas duplicadas
df = df.drop_duplicates()

# Agrupa a tabela de partidas por role para cada jogador, somando os valores
sum_df = df.groupby(['SummonerName', 'Role'])[['Kills', 'Deaths', 'Assists', 'KDA', 'TotalMinionsKilled']].sum().reset_index()
# print(sum_df)

# Count the number of matches per role for each player
matches_per_role = df.groupby(['SummonerName', 'Role']).size().reset_index(name='Matches')

# Calcula a média de cada jogador por role
average_df = df.groupby(['SummonerName', 'Role'])[['Kills', 'Deaths', 'Assists','KDA', 'TotalMinionsKilled']].mean().astype(float).round(2).reset_index()
print(average_df)

average_df = pd.merge(average_df, matches_per_role, on=['SummonerName', 'Role'])
# print(average_df)

sum_df.to_csv('tabelas/grouped.csv', index=False)
average_df.to_csv('tabelas/average.csv', index=False)
df.to_csv('tabelas/matches.csv', index=False)

print("******\nARAM count: " + str(aram_count))