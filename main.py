import discord
from discord import Option
from dotenv import load_dotenv
import os
import aiohttp
from discord.ext import commands
import sqlite3
import random
from database import init_db

# Load env vars
load_dotenv()

# Initialize bot with slash commands
intents = discord.Intents.default()
intents.message_content = True  # For prefix commands if you want them
bot = discord.Bot(intents=intents)

# Perplexity API Integration
async def get_ai_response(query: str) -> str:
    """Get AI response from Perplexity with Finny's personality."""
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Finny, a witty financial assistant for Gen Z. "
                    "Respond in under 200 characters. Use emojis, analogies, "
                    "and humor. Be concise but helpful."
                )
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "max_tokens": 150
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error = await response.text()
                    return f"❌ API Error ({response.status}): {error[:100]}"
    except Exception as e:
        return f"⚠️ Finny glitched: {str(e)}"

# ---------------------------
# Key Features
# ---------------------------

class SpendSaveView(discord.ui.View):
    @discord.ui.button(label="Buy", style=discord.ButtonStyle.red)
    async def buy_callback(self, button, interaction):
        # Deduct coins (optional: check if user exists)
        conn = sqlite3.connect("finny.db")
        cursor = conn.cursor()
        # Ensure user exists
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (interaction.user.id, interaction.user.name))
        cursor.execute("UPDATE users SET fincoins = fincoins - 10 WHERE user_id = ?", (interaction.user.id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message("💸 Enjoy your purchase! (But -10 FinCoins)", ephemeral=True)

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green)
    async def save_callback(self, button, interaction):
        conn = sqlite3.connect("finny.db")
        cursor = conn.cursor()
        # Ensure user exists
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (interaction.user.id, interaction.user.name))
        cursor.execute("UPDATE users SET fincoins = fincoins + 10 WHERE user_id = ?", (interaction.user.id,))
        conn.commit()
        conn.close()
        await interaction.response.send_message("✅ +10 FinCoins! Adulting level +1.", ephemeral=True)

# 1. Spend-or-Save Game
@bot.slash_command(name="spendgame", description="Daily spend/save challenge")
async def spend_game(ctx: discord.ApplicationContext):
    dilemmas = [
        "Your friends are ordering ₹800 sushi. You already ate. 🍣 Buy or Save?",
        "Spotify Premium (₹129/month) vs. Free ads version. Upgrade or Save?",
        "Impulse buy: ₹2000 sneakers on sale. Need or Save?",
        "Uber vs. Bus for ₹300. Ride or Save?",
        "₹150 coffee at Starbucks. Sip or Save?"
    ]
    embed = discord.Embed(
        title="💸 Spend or Save?",
        description=random.choice(dilemmas),
        color=discord.Color.gold()
    )
    await ctx.respond(embed=embed, view=SpendSaveView())

# 2. Goal Tracker
@bot.slash_command(name="goal", description="Set a savings goal")
async def set_goal(
    ctx: discord.ApplicationContext,
    name: Option(str, "Goal name (e.g. 'PS5')"),
    target: Option(float, "Target amount (₹)")
):
    conn = sqlite3.connect("finny.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (ctx.user.id, ctx.user.name))
    cursor.execute(
        "INSERT INTO goals (user_id, name, target) VALUES (?, ?, ?)",
        (ctx.user.id, name, target)
    )
    conn.commit()
    conn.close()
    await ctx.respond(
        f"🎯 Goal set! Saving ₹{target} for {name}. "
        f"Use `/goal_update {name} <amount>` to track progress."
    )

# 3. Finance chat
@bot.slash_command(name="finnychat", description="Ask Finny anything about finance!")
async def finny_chat(
    ctx: discord.ApplicationContext,
    question: Option(str, "Your money question", required=True)
):
    """AI-powered finance advice using Perplexity"""
    await ctx.defer()  # For slower API calls
    response = await get_ai_response(question)
    await ctx.respond(f"🎩 **Finny says:** {response}")

# 4. Help function
@bot.slash_command(name="help", description="Get help with Finny")
async def help_command(ctx):
    # bot.application_commands is a list of registered slash commands
    command_list = [f"/{cmd.name}: {cmd.description or 'No description'}" for cmd in bot.application_commands]
    help_text = "**Available Commands:**\n" + "\n".join(command_list)
    await ctx.respond(help_text)


# Optional: Prefix Command Example (!ping)
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# ---------------------------
# Core Events
# ---------------------------

@bot.event
async def on_ready():
    init_db()
    print(f"Logged in as {bot.user}!")
    await bot.sync_commands()
    print("Slash commands synced!")

# Run bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN not found in .env!")
    else:
        bot.run(token)
