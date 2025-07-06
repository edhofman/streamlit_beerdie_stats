import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Beerdie Player Stats", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("csv_data_beerdie.csv")

df = load_data()
df = df[df["Spil"] == "beerdie"]

players = [
    "Boogie", "Christian", "Emil", "G", "Ibh", "Jakob",
    "Lutz", "Mads", "Martin", "Nick", "Ruben"
]

player = st.selectbox("Choose a player", players)
player_df = df[df["Spiller"] == player]

if player_df.empty:
    st.warning("No data for selected player.")
else:
    st.header(f"Stats for {player}")

    # Summary stats
    total_games = len(player_df)
    wins = player_df["Sejr"].sum()
    win_rate = wins / total_games if total_games else 0
    beers = player_df["min_antal_øl"].sum()
    streak = 0
    max_streak = 0
    for val in player_df.sort_values("Kamp Nr")["Sejr"]:
        if val:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    st.markdown(
        f"""
        - Total Games: **{total_games}**  
        - Wins: **{wins}**  
        - Win Rate: **{win_rate:.1%}**  
        - Total Beers: **{int(beers)}**  
        - Longest Win Streak: **{max_streak}**
        """
    )

    # Cumulative win plot
    player_df = player_df.sort_values("Kamp Nr").copy()
    player_df["Cumulative Wins"] = player_df["Sejr"].cumsum()

    fig, ax = plt.subplots()
    ax.plot(player_df["Kamp Nr"], player_df["Cumulative Wins"], marker='o')
    for i, row in player_df.iterrows():
        score = f"{int(row['Holdpoint'])}-{int(row['modstanderpoint'])}"
        ax.annotate(score, (row["Kamp Nr"], row["Cumulative Wins"]),
                    textcoords="offset points", xytext=(0, 8), ha='center', fontsize=8)
    ax.set_xlabel("Game Number")
    ax.set_ylabel("Cumulative Wins")
    ax.set_title("Cumulative Wins Over Time")
    st.pyplot(fig)

    # Match table
    st.subheader("Match History")
    show_df = player_df[["Kamp Nr", "Holdpoint", "modstanderpoint", "Sejr", "min_antal_øl"]]
    show_df.columns = ["Game", "Team", "Opp", "Win", "Beers"]
    st.dataframe(show_df.reset_index(drop=True))
