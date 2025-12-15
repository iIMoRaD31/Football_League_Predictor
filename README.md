# Football League Predictor
Football League Predictor is a full-stack app that predicts match scorelines (home goals + away goals) using a multi-output neural network, then uses those match predictions to simulate the remaining fixtures of a league season and generate a predicted league table.

The project includes:
- A **Flask API** that loads the trained model and produces scoreline predictions for any matchup.
- A **React/Vite frontend** that lets you select teams, run predictions, and simulate leagues.
- A **data pipeline** that converts raw league CSVs into a leakage-free training dataset with team-level, form-level, and player-level features.

## How it works (high-level)

### Data & features
We build a match feature vector from:
- **Team strength / expectation**: `club_ranking` (final league standing used as a proxy).
- **Recent form (last 5 games)**: average goals for/against, points, and a custom opponent-adjusted form score.
- **Home/away indicator**: `is_home`.
- **Interaction (matchup) features**: ranking diffs, quality ratios, xG matchup differentials, mismatch flags, etc.
- **Player aggregation**: fixed-size roster representation (15 outfield + 1 goalkeeper) using rolling mean of each player's prior appearances (team/league/season constrained), with padding for missing players.

### Model
A multi-output feedforward neural network:
- Shared trunk: Dense(512→256→128) with BatchNorm + Dropout
- Two heads (home + away): Dense(64) + Dense(10) with Softmax
- Outputs: **probability distribution over goals 0–9** for home and away

### League simulation
For future fixtures where some features are unavailable, inference approximates them consistently:
- Roster = **most-used players** in the season so far (aggregated stats)
- Recent form = updated autoregressively using **predicted matches**
- xG for/against = season-average estimates

## Repo structure

### Link to Drive containing the app directory

https://drive.google.com/file/d/13jl20YtAODdEZ3me-cFXkIkJTBWlVaJc/view?usp=sharing

The extracted folder should have the following structure:

```text
.
├── api_server.py
├── process_football_data.py
├── processed_football_data.csv
├── trained_model/
│   ├── football_predictor.keras
│   ├── scaler.pkl
│   └── feature_columns.pkl
├── vite.config.ts
├── package.json
├── src/
├── build/
...
```
## Running the app

After you extract the zip file you should open the terminal inside the that folder. 

#### 1) Install Prereqs(if needed)
Linux:
```bash
sudo apt update && sudo apt install -y python3 python3-pip curl && curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs

```
Windows (Restart terminal after installing):
```bash
winget install -e --id Python.Python.3.10 && winget install -e --id OpenJS.NodeJS.LTS

```

#### 2) Create/activate a venv

Linux:
```bash
python -m venv .venv && source .venv/bin/activate


```
Windows :
```bash
python -m venv .venv && .venv\Scripts\activate

```
#### 3) Install Python deps (core ones used by ```api_server.py```)

```bash
pip install flask flask-cors pandas numpy joblib tensorflow scikit-learn

```
#### 4) Run the API

```bash
python api_server.py
```
#### 5) Frontend (React/Vite)

```bash
npm install # Install deps
npm run dev # Run dev server
npm run build # Build for production
```

## Link to Drive containing collceted data

https://drive.google.com/file/d/1LCmSlCbwfgz9xNFMJMpgiXxuMrVOiEqf/view?usp=sharing


