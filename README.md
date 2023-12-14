# League Flex Ranking

*Personal project for ranking flex players in League of Legends using RiotAPI.* 

***The objective of this project is to monitor the match history of a specified player, cross-referencing it with a list of selected names. If it detects a flex match involving three or more players from the provided list, the match information is added to a database. This data is then used to rank the players on a leaderboard, which will be viewable on an upcoming website named ‘League Flex Ranking’. The website is currently under development and has not yet been launched.***


## Install requirements
```bash
pip install -r requirements.txt
```

## Run the code

Navigate into the src folder and run 'createTables.py' to create the tables based on the specified player and a list of selected names.
```bash
cd src && python createTables.py
```

## Run the WebApp server

Open a new terminal session to start the server, then navigate to 'mysite' folder and run 
```bash
python manage.py runserver
```

Now you can acess the web app at http://127.0.0.1:8000/
