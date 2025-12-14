
import pandas as pd
import glob
import os
from difflib import SequenceMatcher
import ast
import re
from datetime import datetime

# Team name matching function
def match_team_name(target_team, available_teams, threshold=0.6):
    """
    Match team names using multiple strategies
    """
    target_lower = target_team.lower().strip()

    # Strategy 1: Exact match
    for team in available_teams:
        if team.lower().strip() == target_lower:
            return team

    # Strategy 2: Containment match
    for team in available_teams:
        team_lower = team.lower().strip()
        if target_lower in team_lower or team_lower in target_lower:
            return team

    # Strategy 3: Common name variations
    name_mappings = {
        # Premier League
        "wolves": "wolverhampton",
        "spurs": "tottenham",
        "man utd": "manchester united",
        "man united": "manchester united",
        "man city": "manchester city",
        "newcastle": "newcastle united",
        "west ham": "west ham united",
        "brighton": "brighton and hove albion",
        "leeds": "leeds united",
        "leicester": "leicester city",
        "norwich": "norwich city",
        "nottingham": "nottingham forest",
        "nott'ham forest": "nottingham forest",
        "sheffield": "sheffield united",
        "luton": "luton town",
        "bournemouth": "afc bournemouth",
        # La Liga
        "atletico madrid": "atlético madrid",
        "atletico": "atlético",
        "athletic club": "athletic bilbao",
        "athletic": "athletic bilbao",
        "betis": "real betis",
        "celta": "celta vigo",
        "alaves": "alavés",
        "cadiz": "cádiz",
        "almeria": "almería",
        "leganes": "leganés",
        # Bundesliga
        "bayern": "bayern munich",
        "bayern münchen": "bayern munich",
        "dortmund": "borussia dortmund",
        "borussia m'gladbach": "borussia mönchengladbach",
        "monchengladbach": "mönchengladbach",
        "gladbach": "mönchengladbach",
        "mgladbach": "mönchengladbach",
        "leverkusen": "bayer leverkusen",
        "bayer 04 leverkusen": "bayer leverkusen",
        "rb leipzig": "rasenballsport leipzig",
        "leipzig": "rasenballsport leipzig",
        "wolfsburg": "vfl wolfsburg",
        "frankfurt": "eintracht frankfurt",
        "koln": "köln",
        "cologne": "köln",
        "fc koln": "fc köln",
        "1. fc köln": "köln",
        "union berlin": "1. fc union berlin",
        "hertha": "hertha bsc",
        "hertha berlin": "hertha bsc",
        "schalke": "schalke 04",
        "mainz": "mainz 05",
        "freiburg": "sc freiburg",
        "hoffenheim": "tsg hoffenheim",
        "augsburg": "fc augsburg",
        "stuttgart": "vfb stuttgart",
        "bochum": "vfl bochum",
        "werder": "werder bremen",
        "heidenheim": "1. fc heidenheim",
        "darmstadt": "sv darmstadt 98",
        # Ligue 1
        "psg": "paris saint-germain",
        "paris sg": "paris saint-germain",
        "paris": "paris saint-germain",
        "monaco": "as monaco",
        "marseille": "olympique marseille",
        "om": "olympique marseille",
        "olympique de marseille": "olympique marseille",
        "lille": "losc lille",
        "losc": "losc lille",
        "lille osc": "losc lille",
        "lyon": "olympique lyon",
        "ol": "olympique lyon",
        "olympique lyonnais": "olympique lyon",
        "nice": "ogc nice",
        "lens": "rc lens",
        "racing club de lens": "rc lens",
        "rennes": "stade rennais",
        "stade rennais fc": "stade rennais",
        "strasbourg": "rc strasbourg",
        "racing club de strasbourg": "rc strasbourg",
        "rc strasbourg alsace": "rc strasbourg",
        "reims": "stade reims",
        "stade de reims": "stade reims",
        "brest": "stade brestois",
        "stade brestois 29": "stade brestois",
        "nantes": "fc nantes",
        "montpellier": "montpellier hsc",
        "toulouse": "fc toulouse",
        "saint-etienne": "as saint-étienne",
        "saint etienne": "as saint-étienne",
        "st etienne": "as saint-étienne",
        "asse": "as saint-étienne",
        "auxerre": "aj auxerre",
        "angers": "angers sco",
        "le havre": "havre ac",
        "havre": "havre ac",
        "bordeaux": "fc girondins de bordeaux",
        "girondins": "fc girondins de bordeaux",
        # Serie A
        "inter": "inter milan",
        "inter milan": "internazionale",
        "internazionale": "inter",
        "fc internazionale milano": "inter milan",
        "milan": "ac milan",
        "ac milan": "milan",
        "juve": "juventus",
        "juventus fc": "juventus",
        "roma": "as roma",
        "as roma": "roma",
        "lazio": "ss lazio",
        "ss lazio": "lazio",
        "napoli": "ssc napoli",
        "ssc napoli": "napoli",
        "fiorentina": "acf fiorentina",
        "acf fiorentina": "fiorentina",
        "atalanta": "atalanta bc",
        "verona": "hellas verona",
        "hellas verona fc": "hellas verona",
        "bologna": "bologna fc",
        "torino": "torino fc",
        "genoa": "genoa cfc",
        "sampdoria": "uc sampdoria",
        "udinese": "udinese calcio",
        "cagliari": "cagliari calcio",
        "parma": "parma calcio",
        "empoli": "empoli fc",
        "sassuolo": "us sassuolo",
        "spezia": "spezia calcio",
        "venezia": "venezia fc",
        "salernitana": "us salernitana",
        "monza": "ac monza",
        "cremonese": "us cremonese",
        "lecce": "us lecce",
    }

    for short_name, full_name in name_mappings.items():
        if short_name in target_lower or target_lower in short_name:
            for team in available_teams:
                if full_name in team.lower() or short_name in team.lower():
                    return team

    # Strategy 4: Fuzzy string matching
    best_match = None
    best_ratio = 0
    for team in available_teams:
        ratio = SequenceMatcher(None, target_lower, team.lower()).ratio()
        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = team

    return best_match

# Load standings from text files
def load_standings():
    """
    Load all standings files and create a mapping
    Returns: dict[league_season] -> list of teams in order
    """
    standings = {}

    # Mapping from league names to file prefixes
    league_mapping = {
        'ESP-La Liga': 'll_',
        'GER-Bundesliga': 'bl_',
        'ITA-Serie A': 'sa_',
        'ENG-Premier League': 'pl_',
        'FRA-Ligue 1': 'l1_'
    }

    # Find all standings files
    for txt_file in glob.glob('*.txt'):
        # Parse file name to get league and season
        for league, prefix in league_mapping.items():
            if txt_file.startswith(prefix):
                season = txt_file.replace(prefix, '').replace('.txt', '')
                key = f"{league}_{season}"

                # Read teams from file
                with open(txt_file, 'r', encoding='utf-8') as f:
                    teams = [line.strip() for line in f if line.strip()]
                    standings[key] = teams
                break

    return standings

def get_team_ranking(team, league, season, standings):
    """
    Get team's final ranking for a season
    """
    key = f"{league}_{season}"
    if key not in standings:
        return None

    teams_list = standings[key]
    matched_team = match_team_name(team, teams_list)

    if matched_team:
        return teams_list.index(matched_team) + 1  # 1-indexed ranking
    return None

def extract_game_info(outfield_players_str):
    """
    Extract game info from the outfield_players column
    Returns: (home_team, away_team)
    """
    try:
        # Parse the string to get the first dict entry
        data = ast.literal_eval(outfield_players_str)
        if isinstance(data, list) and len(data) > 0:
            first_entry = data[0]
            game_str = first_entry.get(('game', ''), '')
            # Format: "2025-08-15 Liverpool-Bournemouth"
            match = re.search(r'\d{4}-\d{2}-\d{2}\s+(.+)-(.+)', game_str)
            if match:
                return match.group(1).strip(), match.group(2).strip()
    except:
        pass
    return None, None

def calculate_form_score(last_games_str, team, opponent_rankings, team_ranking):
    """
    Calculate recent form score based on results against higher/lower ranked teams
    """
    if not last_games_str or last_games_str == '':
        return 0

    games = last_games_str.split(', ')
    total_score = 0
    num_games = 0

    for game in games:
        # Parse game format: "Team_A goals_a goals_b Team_B"
        parts = game.strip().split()
        if len(parts) < 4:
            continue

        try:
            # Find where the scores are (they should be numeric)
            score_indices = []
            for i, part in enumerate(parts):
                if part.isdigit():
                    score_indices.append(i)

            if len(score_indices) < 2:
                continue

            goals_for = int(parts[score_indices[0]])
            goals_against = int(parts[score_indices[1]])

            # Get opponent name (everything after the second score)
            opponent = ' '.join(parts[score_indices[1]+1:])
            opponent_rank = opponent_rankings.get(opponent)

            if opponent_rank is None or team_ranking is None:
                continue

            num_games += 1

            # Determine result
            if goals_for > goals_against:  # Win
                if opponent_rank < team_ranking:  # Opponent ranked higher (lower number = better)
                    total_score += 2
                else:
                    total_score += 1
            elif goals_for < goals_against:  # Loss
                if opponent_rank < team_ranking:  # Lost to higher ranked team
                    total_score -= 1
                else:  # Lost to lower ranked team
                    total_score -= 2
            else:  # Draw
                if opponent_rank < team_ranking:  # Drew with higher ranked team
                    total_score += 1
                else:  # Drew with lower ranked team
                    total_score -= 1
        except:
            continue

    return total_score / num_games if num_games > 0 else 0

def process_csv_files():
    """
    Main function to process all CSV files
    """
    # Load standings
    print("Loading standings...")
    standings = load_standings()
    print(f"Loaded standings for {len(standings)} league-seasons")

    # Find all CSV files
    csv_files = glob.glob('*.csv')
    print(f"Found {len(csv_files)} CSV files")

    all_data = []

    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        try:
            df = pd.read_csv(csv_file)

            # Sort by date to ensure chronological order
            df["date"] = pd.to_datetime(df["date"].astype(str).str.strip(),
                            format="mixed",
                            errors="raise")
            df = df.sort_values(['league', 'season', 'date', 'match_id'])

            # Add new columns
            df['is_home'] = 0
            df['last_five_games'] = ''
            df['club_ranking'] = None
            df['avg_goals_for_last5'] = 0.0
            df['avg_goals_against_last5'] = 0.0
            df['avg_points_last5'] = 0.0
            df['recent_form_score_last5'] = 0.0

            # Process each row
            for idx in df.index:
                row = df.loc[idx]

                # 1. Determine is_home
                home_team, away_team = extract_game_info(str(row['outfield_players']))
                if home_team and row['team'] == home_team:
                    df.at[idx, 'is_home'] = 1

                # 2. Get club ranking
                ranking = get_team_ranking(row['team'], row['league'], row['season'], standings)
                df.at[idx, 'club_ranking'] = ranking

                # 3. Get last 5 games for this team in this season
                team = row['team']
                league = row['league']
                season = row['season']
                current_date = row['date']

                # Get all previous games for this team in this season
                prev_games = df[
                    (df['team'] == team) & 
                    (df['league'] == league) & 
                    (df['season'] == season) & 
                    (df['date'] < current_date)
                ].tail(5)

                # If no previous games, use current game
                if len(prev_games) == 0:
                    last_games_str = f"{team} {row['goals_for']} {row['goals_against']} {row['opponent']}"
                    df.at[idx, 'last_five_games'] = last_games_str
                    df.at[idx, 'avg_goals_for_last5'] = row['goals_for']
                    df.at[idx, 'avg_goals_against_last5'] = row['goals_against']

                    # Calculate points for current game
                    if row['goals_for'] > row['goals_against']:
                        points = 3
                    elif row['goals_for'] == row['goals_against']:
                        points = 1
                    else:
                        points = 0
                    df.at[idx, 'avg_points_last5'] = points
                else:
                    # Build last_five_games string
                    game_strs = []
                    total_gf = 0
                    total_ga = 0
                    total_points = 0

                    for _, game in prev_games.iterrows():
                        game_str = f"{game['team']} {game['goals_for']} {game['goals_against']} {game['opponent']}"
                        game_strs.append(game_str)
                        total_gf += game['goals_for']
                        total_ga += game['goals_against']

                        # Calculate points
                        if game['goals_for'] > game['goals_against']:
                            total_points += 3
                        elif game['goals_for'] == game['goals_against']:
                            total_points += 1

                    df.at[idx, 'last_five_games'] = ', '.join(game_strs)
                    df.at[idx, 'avg_goals_for_last5'] = total_gf / len(prev_games)
                    df.at[idx, 'avg_goals_against_last5'] = total_ga / len(prev_games)
                    df.at[idx, 'avg_points_last5'] = total_points / len(prev_games)

                # 4. Calculate recent form score
                # Get rankings for all teams in the league
                opponent_rankings = {}
                key = f"{league}_{season}"
                if key in standings:
                    for team_name in df[(df['league'] == league) & (df['season'] == season)]['team'].unique():
                        rank = get_team_ranking(team_name, league, season, standings)
                        if rank:
                            opponent_rankings[team_name] = rank

                form_score = calculate_form_score(
                    df.at[idx, 'last_five_games'],
                    team,
                    opponent_rankings,
                    ranking
                )
                df.at[idx, 'recent_form_score_last5'] = form_score

            all_data.append(df)

        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            continue

    # Combine all dataframes
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)

        # Save to output file
        output_file = 'processed_football_data.csv'
        final_df.to_csv(output_file, index=False)
        print(f"\nProcessing complete! Output saved to {output_file}")
        print(f"Total rows: {len(final_df)}")
    else:
        print("No data processed!")

if __name__ == "__main__":
    process_csv_files()
