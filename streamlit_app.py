import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import numpy as np

st.set_page_config(page_title="🍺 Beerdie Player Stats", layout="wide", page_icon="🍺")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B35;
        margin-bottom: 2rem;
    }
    .player-header {
        font-size: 2rem;
        font-weight: bold;
        color: #004E89;
        margin-bottom: 1rem;
    }
    .stat-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B35;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #004E89;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6C757D;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("csv_data_beerdie.csv")

def find_best_partner(player_name, df):
    """Find the best partner for a given player"""
    # Get all games where the player participated
    player_games = df[df["Spiller"] == player_name]
    
    # For each game, find the teammate
    partners = []
    partner_wins = []
    
    for _, game in player_games.iterrows():
        game_num = game["Kamp Nr"]
        team = game["Hold"]
        
        # Find teammate in the same game and team
        teammate = df[(df["Kamp Nr"] == game_num) & 
                     (df["Hold"] == team) & 
                     (df["Spiller"] != player_name)]
        
        if not teammate.empty:
            partner_name = teammate.iloc[0]["Spiller"]
            win = game["Sejr"]
            partners.append(partner_name)
            partner_wins.append(win)
    
    # Calculate win rates with each partner
    partner_stats = {}
    for partner, win in zip(partners, partner_wins):
        if partner not in partner_stats:
            partner_stats[partner] = {"games": 0, "wins": 0}
        partner_stats[partner]["games"] += 1
        partner_stats[partner]["wins"] += win
    
    # Calculate win rates and find best partner
    best_partner = None
    best_win_rate = 0
    best_games = 0
    
    for partner, stats in partner_stats.items():
        win_rate = stats["wins"] / stats["games"] if stats["games"] > 0 else 0
        if stats["games"] >= 3 and win_rate > best_win_rate:  # At least 3 games together
            best_partner = partner
            best_win_rate = win_rate
            best_games = stats["games"]
    
    return best_partner, best_win_rate, best_games, partner_stats

def get_opponent_names(player_name, game_num, df):
    """Get the names of opponents in a specific game"""
    # Get the player's team for this game
    player_game = df[(df["Spiller"] == player_name) & (df["Kamp Nr"] == game_num)]
    if player_game.empty:
        return "Unknown"
    
    player_team = player_game.iloc[0]["Hold"]
    opponent_team = "A" if player_team == "B" else "B"
    
    # Get all opponents in this game
    opponents = df[(df["Kamp Nr"] == game_num) & (df["Hold"] == opponent_team)]["Spiller"].tolist()
    
    if not opponents:
        return "Unknown"
    
    return " & ".join(opponents)

def get_teammate_name(player_name, game_num, df):
    """Get the name of teammate in a specific game"""
    # Get the player's team for this game
    player_game = df[(df["Spiller"] == player_name) & (df["Kamp Nr"] == game_num)]
    if player_game.empty:
        return "Unknown"
    
    player_team = player_game.iloc[0]["Hold"]
    
    # Get teammate in the same team and game
    teammate = df[(df["Kamp Nr"] == game_num) & 
                  (df["Hold"] == player_team) & 
                  (df["Spiller"] != player_name)]
    
    if teammate.empty:
        # Check if this is actually a 1v1 game or data issue
        all_players_in_game = df[df["Kamp Nr"] == game_num]["Spiller"].tolist()
        if len(all_players_in_game) == 2:
            return "1v1"
        return "Unknown"
    
    return teammate.iloc[0]["Spiller"]

# Load and filter data
df = load_data()
df = df[df["Spil"].str.lower().str.strip() == "beerdie"]

# Filter for specific players only
allowed_players = ["Boogie", "Christian", "Emil", "G", "Ibh", "Jakob", "Lutz", "Mads", "Martin", "Nick", "Ruben"]
#df = df[df["Spiller"].isin(allowed_players)]

# Title
st.markdown('<div class="main-header">🍺 Beerdie Championship Stats</div>', unsafe_allow_html=True)

# Player selection
players = sorted([p for p in df["Spiller"].unique() if p in allowed_players])
player = st.selectbox("🎯 Choose a player", players, index=0)

player_df = df[df["Spiller"] == player]

if player_df.empty:
    st.warning("No data for selected player.")
else:
    st.markdown(f'<div class="player-header">📊 Stats for {player}</div>', unsafe_allow_html=True)
    
    # Calculate stats
    total_games = len(player_df)
    wins = player_df["Sejr"].sum()
    win_rate = wins / total_games if total_games else 0
    beers = player_df["min_antal_øl"].sum()
    
    # Calculate win streak
    streak = 0
    max_streak = 0
    for val in player_df.sort_values("Kamp Nr")["Sejr"]:
        if val:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    
    # Find best partner
    best_partner, best_partner_win_rate, best_partner_games, all_partners = find_best_partner(player, df)
    
    # Display summary stats in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🎮 Total Games", total_games)
    
    with col2:
        st.metric("🏆 Wins", wins)
    
    with col3:
        st.metric("📈 Win Rate", f"{win_rate:.1%}")
    
    with col4:
        st.metric("🍺 Total Beers", int(beers))
    
    with col5:
        st.metric("🔥 Longest Win Streak", max_streak)
    
    # Best partner section
    st.subheader("🤝 Partnership Analysis")
    
    if all_partners:
        col1, col2 = st.columns(2)
        
        with col1:
            if best_partner:
                st.info(f"**Best Partner:** {best_partner}")
                st.write(f"Win Rate: {best_partner_win_rate:.1%} ({best_partner_games} games)")
            else:
                # Find partner with most games if no best partner
                most_games_partner = max(all_partners.items(), key=lambda x: x[1]["games"])
                st.info(f"**Most Frequent Partner:** {most_games_partner[0]}")
                st.write(f"Games: {most_games_partner[1]['games']}")
        
        with col2:
            # Show all partnerships
            st.write("**All Partnerships:**")
            partnership_df = pd.DataFrame([
                {
                    "Partner": partner,
                    "Games": stats["games"],
                    "Wins": stats["wins"],
                    "Win Rate": f"{stats['wins']/stats['games']:.1%}"
                }
                for partner, stats in all_partners.items()
            ]).sort_values("Games", ascending=False)
            st.dataframe(partnership_df, hide_index=True)
    else:
        st.info("No partnership data available")
    
    # Enhanced cumulative win plot
    st.subheader("📈 Performance Over Time")
    
    player_df_sorted = player_df.sort_values("Kamp Nr").copy()
    player_df_sorted["Cumulative Wins"] = player_df_sorted["Sejr"].cumsum()
    
    # Create a more beautiful plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot the line
    ax.plot(player_df_sorted["Kamp Nr"], player_df_sorted["Cumulative Wins"], 
            marker='o', linewidth=2.5, markersize=6, color='#FF6B35')
    
    # Add score annotations with better positioning to avoid overlap
    annotations = []
    for i, row in player_df_sorted.iterrows():
        score = f"{int(row['Holdpoint'])}-{int(row['modstanderpoint'])}"
        annotations.append((row["Kamp Nr"], row["Cumulative Wins"], score))
    
    # Sort annotations by x-coordinate to handle overlaps
    annotations.sort(key=lambda x: x[0])
    
    # Apply smart positioning to avoid overlaps
    for i, (x, y, score) in enumerate(annotations):
        # Calculate offset based on position and nearby annotations
        base_offset = 15
        
        # Check for nearby annotations and adjust offset
        offset_multiplier = 1
        for j, (other_x, other_y, _) in enumerate(annotations):
            if i != j and abs(x - other_x) <= 2:  # If games are close
                if abs(y - other_y) <= 2:  # And cumulative wins are close
                    offset_multiplier = 2 + (i % 3)  # Stagger the offsets
                    break
        
        # Alternate between positive and negative offsets
        y_offset = base_offset * offset_multiplier if i % 2 == 0 else -base_offset * offset_multiplier
        
        ax.annotate(score, (x, y),
                    textcoords="offset points", xytext=(0, y_offset), 
                    ha='center', fontsize=7, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', alpha=0.7))
    
    # Style the plot
    ax.set_xlabel("Game Number", fontsize=12, fontweight='bold')
    ax.set_ylabel("Cumulative Wins", fontsize=12, fontweight='bold')
    ax.set_title(f"Cumulative Wins Over Time - {player}", fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#F8F9FA')
    
    # Set integer ticks for both axes
    ax.set_xticks(range(int(player_df_sorted["Kamp Nr"].min()), 
                       int(player_df_sorted["Kamp Nr"].max()) + 1))
    ax.set_yticks(range(0, int(player_df_sorted["Cumulative Wins"].max()) + 1))
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Enhanced match table
    st.subheader("📋 Detailed Match History")
    
    # Create enhanced match data
    match_data = []
    for _, row in player_df_sorted.iterrows():
        game_num = row["Kamp Nr"]
        teammate = get_teammate_name(player, game_num, df)
        opponents = get_opponent_names(player, game_num, df)
        
        match_data.append({
            "Game": int(game_num),
            "Teammate": teammate,
            "Opponents": opponents,
            "Score": f"{int(row['Holdpoint'])}-{int(row['modstanderpoint'])}",
            "Result": "✅ Win" if row["Sejr"] else "❌ Loss",
            "Beers": int(row["min_antal_øl"])
        })
    
    match_df = pd.DataFrame(match_data)
    
    # Style the dataframe
    st.dataframe(
        match_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Game": st.column_config.NumberColumn("Game #", width="small"),
            "Teammate": st.column_config.TextColumn("Teammate", width="medium"),
            "Opponents": st.column_config.TextColumn("Opponents", width="medium"),
            "Score": st.column_config.TextColumn("Score", width="small"),
            "Result": st.column_config.TextColumn("Result", width="small"),
            "Beers": st.column_config.NumberColumn("Beers 🍺", width="small")
        }
    )
    
    # Additional insights
    st.subheader("🔍 Additional Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average score analysis
        avg_team_score = player_df["Holdpoint"].mean()
        avg_opp_score = player_df["modstanderpoint"].mean()
        st.metric("📊 Avg Team Score", f"{avg_team_score:.1f}")
        st.metric("📊 Avg Opponent Score", f"{avg_opp_score:.1f}")
    
    with col2:
        # Close games analysis
        close_games = player_df[abs(player_df["Holdpoint"] - player_df["modstanderpoint"]) <= 3]
        close_game_wins = close_games["Sejr"].sum()
        close_game_total = len(close_games)
        
        if close_game_total > 0:
            st.metric("🎯 Close Games (≤3 pts)", close_game_total)
            st.metric("🎯 Close Game Win Rate", f"{close_game_wins/close_game_total:.1%}")
        else:
            st.metric("🎯 Close Games (≤3 pts)", 0)

# Beer Simulator Section
st.subheader("🍺 Beer Simulator")
st.write("Simulate additional beers consumed based on random dice throwing probability!")

col1, col2 = st.columns(2)

with col1:
    st.info("Random simulation based on dice throwing probability")
    st.write("*It is assumed that the player throws a dice on the table between 3-6 times pr. game, dependening on the length of the game. We then simulate the probability of hitting a 5 given these throws.*")
    st.write("Points in game <= 15: The player throws a dice 3 times on the table.")
    st.write("Points in game <= 20: The player throws a dice 4 times on the table.")
    st.write("Points in game <= 25: The player throws a dice 5 times on the table.")
    st.write("Points in game <= 30: The player throws a dice 6 times on the table.")
    st.write("Points in game >  30: The player throws a dice 7 times on the table.")
    st.write("Probability of getting a 5 on a single throw: 1/6")

with col2:
    if st.button("🎲 Run Simulation"):
        # Calculate simulated beers using random approach
        simulated_beers = []
        total_simulated = 0
        
        for _, row in player_df_sorted.iterrows():
            # Random simulation based on total points in game
            total_points = int(row['Holdpoint']) + int(row['modstanderpoint'])
            game_beers = int(row["min_antal_øl"])
            
            # # For each point, simulate two dice throws
            # for point in range(total_points):
            #     # Probability of getting at least one 5 in two throws: 1-(5/6)²
            #     prob_success = 1 - (5/6)**2
            #     if np.random.random() < prob_success:
            #         game_beers += 1
            # For each game simulate amount of dices on board
            if total_points <= 15:
                sims = 3
            elif total_points <=20:
                sims = 4
            elif total_points <=25:
                sims = 5
            elif total_points <=30:
                sims = 6
            elif total_points <=100:
                sims=7
            for point in range(sims):
                # Probability of getting at least one 5 in two throws: 1-(5/6)²
                prob_success = 1 - 5/6
                if np.random.random() < prob_success:
                    game_beers += 1
            
            total_simulated += game_beers
            simulated_beers.append(total_simulated)
        
        # Create comparison plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot actual beers
        actual_cumulative = player_df_sorted["min_antal_øl"].cumsum()
        ax.plot(player_df_sorted["Kamp Nr"], actual_cumulative, 
                marker='o', linewidth=2.5, markersize=6, color='#FF6B35', 
                label='Actual Beers')
        
        # Plot simulated beers
        ax.plot(player_df_sorted["Kamp Nr"], simulated_beers, 
                marker='s', linewidth=2.5, markersize=6, color='#004E89', 
                label='Simulated Beers (Random)')
        
        # Style the plot
        ax.set_xlabel("Game Number", fontsize=12, fontweight='bold')
        ax.set_ylabel("Cumulative Beers", fontsize=12, fontweight='bold')
        ax.set_title(f"Beer Consumption: Actual vs Simulated - {player}", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#F8F9FA')
        ax.legend()
        
        # Set integer ticks
        ax.set_xticks(range(int(player_df_sorted["Kamp Nr"].min()), 
                           int(player_df_sorted["Kamp Nr"].max()) + 1))
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Show comparison stats
        st.subheader("📊 Simulation Results")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🍺 Actual Total Beers", int(beers))
        
        with col2:
            st.metric("🍺 Simulated Total Beers", int(total_simulated))
        
        with col3:
            difference = total_simulated - beers
            st.metric("📈 Difference", f"{difference:+.0f}")
        
        st.write(f"**Average beers per game (simulated):** {total_simulated/total_games:.1f}")
        st.write(f"**Average beers per game (actual):** {beers/total_games:.1f}")
