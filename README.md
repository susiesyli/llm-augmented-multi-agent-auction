# LLMBidder: Multi-Agent Auctions with LLM-Powered Agents

This project explores how Large Language Models (LLMs) can function as intelligent bidding agents within classical multi-agent auction systems. It implements five auction mechanisms—First-Price Sealed-Bid, Vickrey (Second-Price), English, Dutch, and Japanese—and simulates bidding behavior across a hybrid environment of rule-based agents and LLM-driven agents.

## Overview

- **Classical Agents**: Follow strategy rules grounded in auction theory.
- **LLM Agents**: Use prompt-based reasoning to determine bids or decisions via the BridgeLLM API.
- **Auctioneer**: Manages auction flow, collects bids, determines winners, and computes utility.
- **Output**: Trial-level CSV logs for each auction type + analysis-ready unified dataset.

## Objectives

- Integrate LLMs into a Multi-Agent System (MAS)
- Compare performance between LLM and rule-based agents
- Evaluate adaptability, reasoning, and utility across auction formats
- Demonstrate the value of prompt engineering in shaping LLM behavior

## Auction Types Implemented

| Auction Type             | Strategy Logic (Classical)          | LLM Behavior |
|--------------------------|-------------------------------------|--------------|
| First-Price Sealed-Bid   | Shade bid (value × 0.8)             | Prompted bid |
| Vickrey (Second-Price)   | Truthful (bid = value)              | Prompted bid |
| English (Ascending)      | Stay until value is reached         | Prompt: stay in or drop |
| Dutch (Descending)       | Accept when price ≤ value           | Prompt: accept or wait |
| Japanese (Dropout Model) | Drop out when price > value         | Prompt: yes/no continue |

## Example Prompts (LLM)

```text
You are a strategic bidder in a sealed-bid auction. Return a single number: the bid you would submit.

My private value is 82. This is a first-price sealed-bid auction. Submit a single bid without knowing the others.
