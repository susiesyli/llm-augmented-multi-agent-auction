import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
plt.rcParams['font.family'] = 'Times New Roman'

# Paths to CSV files
base_path = Path("./auction-data/data_2")
files = {
    "Sealed First-Price": "first_price_sealed_auction_results_2.csv",
    "Vickrey": "vickrey_auction_results_2.csv",
    "English": "english_auction_results_2.csv",
    "Dutch": "dutch_auction_results_2.csv",
    "Japanese": "japanese_auction_results_2.csv"
}

# Load and annotate each DataFrame
dfs = {}
for auction_name, filename in files.items():
    df = pd.read_csv(base_path / filename)
    df["auction_type"] = auction_name
    dfs[auction_name] = df

# Combine all auctions into a single DataFrame
full_df = pd.concat(dfs.values(), ignore_index=True)

# ------------------------
# Utility Comparison
# ------------------------
# Add readable agent labels
full_df["agent_type"] = full_df["is_llm"].map({True: "LLM Agent", False: "Classical Agent"})

summary_utility = (
    full_df.groupby(["auction_type", "agent_type"])["utility"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(12, 6))
sns.barplot(data=summary_utility, x="auction_type", y="utility", hue="agent_type")
plt.title("Average Utility of Winning Agent by Auction Type")
plt.ylabel("Utility")
plt.xlabel("Auction Type")
plt.xticks(rotation=45)
plt.legend(title="Agent Type")
plt.tight_layout()
plt.savefig("utility_comparison.pdf", format="pdf")
plt.show()

# ------------------------
# Win Rate Plot
# ------------------------
# Count wins per agent type
win_counts = (
    full_df.groupby(["auction_type", "agent_type"])
    .size()
    .reset_index(name="count")
)

# Total number of trials per auction type
total_trials = (
    full_df.groupby("auction_type")
    .size()
    .reset_index(name="total")
)

# Merge to compute win rate
win_rate = win_counts.merge(total_trials, on="auction_type")
win_rate["win_rate"] = win_rate["count"] / win_rate["total"]

plt.figure(figsize=(12, 6))
sns.barplot(data=win_rate, x="auction_type", y="win_rate", hue="agent_type")
plt.title("Win Rate by Agent Type and Auction Type")
plt.ylabel("Win Rate")
plt.xlabel("Auction Type")
plt.xticks(rotation=45)
plt.legend(title="Agent Type")
plt.tight_layout()
plt.savefig("win_rate_comparison.pdf", format="pdf")
plt.show()