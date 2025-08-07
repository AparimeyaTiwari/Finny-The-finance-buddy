# Finny - The Gen Z Finance Buddy Bot

Finny is a Discord bot designed to make **personal finance tracking, goal-setting, and money management fun and social for Gen Z**. Using AI (via Perplexity API), engaging games, and a simple persistent database, Finny helps you build healthy financial habits, track progress, and compete with friends—right from your Discord server.

## Table of Contents

- [Demo & Screenshots](#demo--screenshots)
- [Features](#features)
- [How it Works](#how-it-works)
- [Setup & Installation](#setup--installation)
- [Environment Variables & API Keys](#environment-variables--api-keys)
- [Database Schema](#database-schema)
- [Bot Commands](#bot-commands)
- [Extending Finny](#extending-finny)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Demo & Screenshots

*(Insert animated GIFs/screenshots of key commands, like the spend-game, setting goals, leaderboard, etc.)*

## Features

- **Daily Spend-or-Save Game:** Get fun financial dilemmas and make choices that impact your "FinCoins" balance.
- **FinCoins Balance:** Track your in-bot currency, earn rewards, and view history.
- **AI-Powered Finance Chat:** Ask Finny any money question! Get witty, concise, Gen Z-friendly AI answers via Perplexity.
- **Savings Goals:** Set, track, and update personal goals (e.g., a new phone, trip). Gamified progress bars included!
- **Transaction History:** Check your 10 most recent financial actions and decisions.
- **Built-in Help & Guidance:** Use `/help` to see all available commands and their descriptions.
- **Persistent Storage:** All user data stored securely in SQLite (`finny.db`).
- **Multi-user Support:** Each Discord user has their own records—great for servers and communities.

## How it Works

- **Interact with Finny through Discord Slash Commands:** All actions are managed with simple `/` commands.
- **AI Integration:** Uses Perplexity AI to generate dilemmas for the daily game and answer money questions in Finny's signature Gen Z persona.
- **Database:** Tracks user balances, goals, and history across sessions and servers using SQLite.

## Setup & Installation

### 1. **Clone the Repository**
```bash
git clone https://github.com/Vinayak-Khavare/Finny-The-finance-buddy.git
cd Finny-The-finance-buddy
```

### 2. **Set Up Python**
Requires **Python 3.8+**
```bash
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
If `requirements.txt` is missing, you likely need:
- discord.py
- python-dotenv
- aiohttp

```bash
pip install -U discord.py python-dotenv aiohttp
```

### 3. **Configure Environment Variables (.env)**
Create a file named `.env` in your project root:

```
DISCORD_TOKEN=your_discord_bot_token_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```
- [How to get a Discord Bot Token](https://discord.com/developers/applications)
- [How to get a Perplexity Developer Key](https://docs.perplexity.ai)

### 4. **Run the Bot**
```bash
python main.py
```
Invite your bot to a Discord server with **`applications.commands`** and **`bot`** scopes.

## Environment Variables & API Keys

| Name                  | Description                  | Example            |
|-----------------------|------------------------------|--------------------|
| `DISCORD_TOKEN`       | Discord bot token            | `abc123...`        |
| `PERPLEXITY_API_KEY`  | Perplexity AI API Key        | `perplexity-xyz..` |

## Database Schema

The `finny.db` SQLite file manages persistent user, transaction, and goal data. Typical tables include:

- **users**:  
    - `user_id` (INTEGER PRIMARY KEY)
    - `username` (TEXT)
    - `fincoins` (INTEGER, default 100)
- **transactions**:  
    - `id`, `user_id`, `amount` (int), `type` ("spend", "save"), `description`, `timestamp`
- **goals**:  
    - `user_id`, `name`, `target` (float), `saved` (float)

**Table creation and integrity** are handled automatically on bot startup via the `init_db()` function. (See `database.py`.)

## Bot Commands

| Command              | What it Does                                                            |
|----------------------|------------------------------------------------------------------------|
| `/spendgame`         | Play the daily AI-generated spend-or-save dilemma and earn FinCoins     |
| `/balance`           | View your current FinCoin balance, stats, and transaction summary       |
| `/transactions`      | Show your 10 most recent actions (spending, saving, etc.)               |
| `/finnychat`         | Ask any money question, get instant witty AI guidance                   |
| `/goal`              | Set a new savings goal (with target and initial savings)                |
| `/goal_update`       | Add funds to an existing goal (progress tracked with bars and rewards)  |
| `/mygoals`           | List all your current savings goals and their progress                  |
| `/help`              | See all bot commands and what they do                                   |

**Parameters and usage will be shown via Discord’s command bar.**

## Example Usage

- **Play Spend-or-Save Game:**
    - `/spendgame`
- **Set a Goal:**
    - `/goal name: "PS5" target: 50000 initial: 5000`
- **Update Goal Progress:**
    - `/goal_update name: "PS5" amount: 2000`
- **Check Transactions:**
    - `/transactions`
- **Ask a Money Question:**
    - `/finnychat question: "How do I build an emergency fund?"`
- **See All Goals:**
    - `/mygoals`

## Extending Finny

Finny is built with modular Python (OOP), Discord's new slash commands, and clean async code.  
**Easy to extend!**
- Add new games, analysis (spending breakdowns), badges/achievements, reminders, server-wide leaderboards, embed themes, and more by building on the existing command framework.
- API integration (Perplexity, finance APIs) is centralized and easy-to-modify.
- All database access uses lightweight context-managed wrappers for future migration (e.g., to PostgreSQL).

## Troubleshooting

- **Bot won’t start?** Double-check `.env` entries and make sure `DISCORD_TOKEN` and `PERPLEXITY_API_KEY` are correct.
- **Missing permissions?** Grant the bot `Read`, `Send Messages`, and `Use Application Commands` in your Discord server.
- **Database errors?** Delete `finny.db` if corrupted (user data will be lost) or check for race conditions on simultaneous access.
- **Perplexity API errors?** API quota exceeded, or invalid key.

## Contributing

Pull requests, issues, and feature requests are all welcome!  
**Beginner-friendly:** Clear, modular code—great for first open source experience.

- Fork, branch, hack, and open a PR for improvements, bugfixes, or new mini-games!
- Ideas: budget analytics, reminders, streak tracking, Discord economy integration.

## License

This project is open-source, released under the [MIT License](LICENSE).

## Credits

Created by [@Vinayak Khavare](https://github.com/Vinayak-Khavare).  
Inspired by the vision of **demystifying finance for the next generation!**

**Questions? Issues?**  
Open an issue or discussion on GitHub, or ping Finny in your server: `/help`  
Let's make finance fun, social, and accessible! 🚀💰
