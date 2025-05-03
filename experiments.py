import random
import pandas as pd
from llmproxy import generate

# ---------------------------
# Agent Classes
# ---------------------------
class Agent:
    def __init__(self, name, value, strategy='shade', risk_factor=0.8):
        self.name = name
        self.value = value
        self.strategy = strategy
        self.risk_factor = risk_factor
        self.is_llm = False

    def bid(self):
        if self.strategy == 'truthful':
            return self.value
        elif self.strategy == 'shade':
            return self.value * self.risk_factor
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        

class LLMAgent(Agent):
    def __init__(self, name, value, session_id="LLMAgentSession", model="4o-mini"):
        super().__init__(name, value)
        self.session_id = session_id
        self.model = model
        self.is_llm = True

    def bid(self, context):
        query = f"My private value is {self.value}. {context}"
        system = "You are a strategic bidder in a sealed-bid auction. Return a single number: the bid you would submit."

        try:
            response = generate(
                model=self.model,
                system=system,
                query=query,
                temperature=0.0,
                lastk=0,
                session_id=self.session_id,
                rag_usage=False,
                rag_threshold=0.5,
                rag_k=1
            )
            print(f"[DEBUG] Raw response: {response}")
            return float(response["result"])
        except Exception as e:
            print(f"LLM response error: {response}")
            print("Exception:", e)
            return self.value * 0.8

    def should_continue(self, current_bid, context):
        system = "You're a bidder in an ascending auction. Decide whether to continue bidding given the current price."
        query = f"My private value is {self.value}. The current bid is {current_bid}. {context} Respond 'yes' to continue, 'no' to drop out."

        response = generate(
            model=self.model,
            system=system,
            query=query,
            temperature=0.0,
            session_id=self.session_id,
            rag_usage=False
        )
        return "yes" in response["result"].lower()

# ---------------------------
# Auctioneer Classes
# ---------------------------

class SealedBidAuctioneer:
    def __init__(self, agents):
        self.agents = agents

    def run_auction(self):
        context = "This is a first-price sealed-bid auction. Submit a single bid without knowing the others."

        # bids = {agent.name: agent.bid() for agent in self.agents}
        bids = {}
        for agent in self.agents:
            if agent.is_llm:
                bids[agent.name] = agent.bid(context)
            else:
                bids[agent.name] = agent.bid()
        winner = max(bids, key=bids.get)
        winning_bid = bids[winner]
        winner_value = next(agent.value for agent in self.agents if agent.name == winner)
        is_llm = next(agent.is_llm for agent in self.agents if agent.name == winner)

        return {
            "winner": winner,
            "winning_bid": winning_bid,
            "winner_value": winner_value,
            "utility": winner_value - winning_bid,
            "is_llm": is_llm,
            "bids": bids
        }

class VickreyAuctioneer(SealedBidAuctioneer):
    def run_auction(self):
        bids = {agent.name: agent.bid() for agent in self.agents}
        sorted_bidders = sorted(bids.items(), key=lambda item: item[1], reverse=True)
        winner, _ = sorted_bidders[0]
        second_highest_bid = sorted_bidders[1][1]

        winner_value = next(agent.value for agent in self.agents if agent.name == winner)
        is_llm = next(agent.is_llm for agent in self.agents if agent.name == winner)

        return {
            "winner": winner,
            "winning_bid": second_highest_bid,
            "winner_value": winner_value,
            "utility": winner_value - second_highest_bid,
            "is_llm": is_llm,
            "bids": bids
        }

class EnglishAuctioneer:
    def __init__(self, agents, bid_increment=1.0):
        self.agents = agents
        self.bid_increment = bid_increment

    def run_auction(self):
        active_agents = self.agents[:]
        current_bid = 0
        bid_round = {}

        while True:
            bids_this_round = []
            for agent in active_agents:
                if agent.is_llm:
                    continue_bidding = agent.should_continue(current_bid, context="This is an English auction. Bid increases each round.")
                else:
                    continue_bidding = agent.value > current_bid

                if continue_bidding:
                    bids_this_round.append((agent.name, current_bid + self.bid_increment))

            if not bids_this_round:
                break

            winner, next_bid = max(bids_this_round, key=lambda x: x[1])
            current_bid = next_bid
            bid_round[winner] = current_bid

        winning_agent = next(agent for agent in self.agents if agent.name == winner)
        return {
            "winner": winner,
            "winning_bid": current_bid,
            "winner_value": winning_agent.value,
            "utility": winning_agent.value - current_bid,
            "is_llm": winning_agent.is_llm,
            "bids": bid_round
        }

class DutchAuctioneer:
    def __init__(self, agents, start_price=100.0, decrement=1.0):
        self.agents = agents
        self.start_price = start_price
        self.decrement = decrement

    def run_auction(self):
        current_price = self.start_price
        while current_price > 0:
            for agent in self.agents:
                if agent.value >= current_price:
                    return {
                        "winner": agent.name,
                        "winning_bid": current_price,
                        "winner_value": agent.value,
                        "utility": agent.value - current_price,
                        "is_llm": agent.is_llm,
                        "bids": {agent.name: current_price}
                    }
            current_price -= self.decrement

        return {
            "winner": None,
            "winning_bid": 0,
            "winner_value": 0,
            "utility": 0,
            "is_llm": False,
            "bids": {}
        }

class JapaneseAuctioneer:
    def __init__(self, agents, start_price=0.0, increment=1.0):
        self.agents = agents
        self.start_price = start_price
        self.increment = increment

    def run_auction(self):
        current_price = self.start_price
        remaining_agents = self.agents[:]
        bid_history = {}

        while len(remaining_agents) > 1:
            new_remaining = []
            for agent in remaining_agents:
                if agent.is_llm:
                    stay_in = agent.should_continue(
                        current_bid=current_price,
                        context="This is a Japanese auction. The price increases each round, and bidders drop out if they don't accept the current price."
                    )
                else:
                    stay_in = agent.value >= current_price

                if stay_in:
                    new_remaining.append(agent)
                    bid_history[agent.name] = current_price
            if not new_remaining:
                break
            remaining_agents = new_remaining
            current_price += self.increment

        if remaining_agents:
            winner = remaining_agents[0]
            return {
                "winner": winner.name,
                "winning_bid": current_price,
                "winner_value": winner.value,
                "utility": winner.value - current_price,
                "is_llm": winner.is_llm,
                "bids": bid_history
            }
        else:
            return {
                "winner": None,
                "winning_bid": 0,
                "winner_value": 0,
                "utility": 0,
                "is_llm": False,
                "bids": {}
            }

# ---------------------------
# Simulation Function
# ---------------------------

def simulate_trials(auction_class, num_trials=100, num_bidders=5, llm_per_game=1):
    results = []
    for trial in range(num_trials):
        agents = []
        llm_indices = random.sample(range(num_bidders), llm_per_game)
        for i in range(num_bidders):
            value = random.uniform(60, 100)
            if i in llm_indices:
                agent = LLMAgent(f"Agent_{i}", value)
            else:
                # agent = Agent(f"Agent_{i}", value, strategy='shade', risk_factor=0.8)
                if auction_class.__name__ == 'DutchAuctioneer':
                    agent = Agent(f"Agent_{i}", value, strategy='truthful')  # No shading
                elif auction_class.__name__ == 'VickreyAuctioneer':
                    agent = Agent(f"Agent_{i}", value, strategy='truthful')  # Bid true value
                else:
                    agent = Agent(f"Agent_{i}", value, strategy='shade', risk_factor=0.8)
            agents.append(agent)

        auction = auction_class(agents)
        result = auction.run_auction()
        result["trial"] = trial
        results.append(result)

    return pd.DataFrame(results)

# ---------------------------
# Run and Save Simulations
# ---------------------------

if __name__ == "__main__":
    auction_classes = {
        "FirstPriceSealed": SealedBidAuctioneer,
        "Vickrey": VickreyAuctioneer,
        "English": EnglishAuctioneer,
        "Dutch": DutchAuctioneer,
        "Japanese": JapaneseAuctioneer,
    }

    all_results = []

    for name, auction_class in auction_classes.items():
        print(f"Running {name} Auction...")
        df = simulate_trials(auction_class, num_trials=10, num_bidders=5, llm_per_game=1)
        df["auction_type"] = name
        all_results.append(df)

        # Save each auction type's result to a separate CSV
        filename = f"{name.lower()}_auction_results.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {filename}")

    # Optional: Save combined dataframe
    full_df = pd.concat(all_results, ignore_index=True)
    full_df.to_csv("mas_llm_experiment_results.csv", index=False)
    print("All simulations complete. Results saved to mas_llm_experiment_results.csv")