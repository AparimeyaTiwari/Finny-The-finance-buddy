import discord
from discord import Option
from dotenv import load_dotenv
import os
import aiohttp
from discord.ext import commands
import sqlite3
import random
from database import init_db
import json

# Load env vars
load_dotenv()

# Initialize bot with slash commands
intents = discord.Intents.default()
intents.message_content = True  # For prefix commands if you want them
bot = discord.Bot(intents=intents)

# connecting database
# Consider using a context manager or connection pooling
def get_db_connection():
    conn = sqlite3.connect("finny.db")
    conn.row_factory = sqlite3.Row  # For dict-like access
    return conn

# Perplexity API Integration for finnychat responses
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
    
# Perplexity API Integration for spend-or-save game
async def get_spend_game_dilemma() -> tuple:
    """Get AI-generated spend/save dilemma with point values"""
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Generate ONLY raw JSON for a financial dilemma with these EXACT fields:\n"
                    '{\n'
                    '  "dilemma": "text",\n'
                    '  "spend_points": integer,\n'
                    '  "save_points": integer,\n'
                    '  "spend_response": "text",\n'
                    '  "save_response": "text"\n'
                    '}\n'
                    "No additional text, comments, or markdown. Just pure JSON."
                )
            },
            {
                "role": "user", 
                "content": "Generate a spend/save dilemma in strict JSON format only."
            }
        ],
        "max_tokens": 250,
        "temperature": 0.7
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
                    content = data["choices"][0]["message"]["content"]
                    
                    # Extract JSON from markdown if needed
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    json_str = content[json_start:json_end]
                    
                    try:
                        result = json.loads(json_str)
                        # Validate all required fields exist
                        required_fields = ["dilemma", "spend_points", "save_points", 
                                         "spend_response", "save_response"]
                        if all(field in result for field in required_fields):
                            return (
                                result["dilemma"],
                                result["spend_points"],
                                result["save_points"],
                                result["spend_response"],
                                result["save_response"]
                            )
                        raise ValueError("Missing required fields")
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        print(f"JSON parse error: {e}\nContent: {content}")
                        return get_fallback_dilemma()
                else:
                    error = await response.text()
                    print(f"API Error ({response.status}): {error}")
                    return get_fallback_dilemma()
    except Exception as e:
        print(f"Connection error: {str(e)}")
        return get_fallback_dilemma()

def get_fallback_dilemma():
    """Hardcoded fallback when API fails"""
    return (
        "🍔 Order in (₹350) vs. cook ramen (₹50). Treat yourself or save?",
        -10,
        5,
        "😋 Yum! But -10 FinCoins...",
        "🧠 +5 FinCoins! Future you approves"
    )

# ---------------------------
# Key Features
# ---------------------------

class SpendSaveView(discord.ui.View):
    def __init__(self, spend_points, save_points, spend_response, save_response, dilemma_text):
        super().__init__()
        self.spend_points = spend_points
        self.save_points = save_points
        self.spend_response = spend_response
        self.save_response = save_response
        self.dilemma_text = dilemma_text
    
    async def update_balance(self, interaction, amount, tx_type):
        conn = None
        try:
            conn = sqlite3.connect("finny.db")
            cursor = conn.cursor()
            
            # Update user balance
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username, fincoins) VALUES (?, ?, 100)",
                (interaction.user.id, interaction.user.name)
            )
            cursor.execute(
                "UPDATE users SET fincoins = fincoins + ? WHERE user_id = ?",
                (amount, interaction.user.id)
            )
            
            # Record transaction
            cursor.execute(
                """INSERT INTO transactions 
                (user_id, amount, type, description) 
                VALUES (?, ?, ?, ?)""",
                (interaction.user.id, amount, tx_type, self.dilemma_text)
            )
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    @discord.ui.button(label="Spend", style=discord.ButtonStyle.red, emoji="💸")
    async def spend_callback(self, button, interaction):
        success = await self.update_balance(
            interaction, 
            self.spend_points, 
            "spend"
        )
        if success:
            await interaction.response.send_message(
                f"{self.spend_response} ({self.spend_points} FinCoins)",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚠️ Oops! Something went wrong updating your balance.",
                ephemeral=True
            )
    
    @discord.ui.button(label="Save", style=discord.ButtonStyle.green, emoji="💰")
    async def save_callback(self, button, interaction):
        success = await self.update_balance(
            interaction, 
            self.save_points, 
            "save"
        )
        if success:
            await interaction.response.send_message(
                f"{self.save_response} (+{self.save_points} FinCoins)",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚠️ Oops! Something went wrong updating your balance.",
                ephemeral=True
            )

# 1. Spend-or-Save Game
@bot.slash_command(name="spendgame", description="Daily spend/save challenge (AI-generated)")
async def spend_game(ctx: discord.ApplicationContext):
    """Generate an AI-powered financial dilemma"""
    await ctx.defer()  # Give the AI time to respond
    
    dilemma, spend_pts, save_pts, spend_resp, save_resp = await get_spend_game_dilemma()
    
    embed = discord.Embed(
        title="💸 Spend or Save?",
        description=dilemma,
        color=discord.Color.gold()
    )
    embed.set_footer(text="Choose wisely! Each decision affects your FinCoin balance")
    
    view = SpendSaveView(
        spend_points=spend_pts,
        save_points=save_pts,
        spend_response=spend_resp,
        save_response=save_resp,
        dilemma_text=dilemma  # Pass the dilemma text for transaction recording
    )
    
    await ctx.respond(embed=embed, view=view)

# 2. Goal Tracker
@bot.slash_command(name="goal", description="Set a savings goal")
async def set_goal(
    ctx: discord.ApplicationContext,
    name: Option(str, "Goal name (e.g. 'GTA VI')"),
    target: Option(float, "Target amount (₹)"),
    initial: Option(float, "Initial amount saved (₹)", required=False, default=0)
):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", 
                      (ctx.user.id, ctx.user.name))
        
        # Check if goal already exists
        cursor.execute(
            "SELECT 1 FROM goals WHERE user_id = ? AND name = ?",
            (ctx.user.id, name)
        )
        if cursor.fetchone():
            await ctx.respond(f"⚠️ You already have a goal named '{name}'. Use `/goal_update` to add to it.")
            return
            
        cursor.execute(
            "INSERT INTO goals (user_id, name, target, saved) VALUES (?, ?, ?, ?)",
            (ctx.user.id, name, target, initial)
        )
        conn.commit()
        
        embed = discord.Embed(
            title="🎯 New Goal Set!",
            description=f"**{name}**: ₹{initial:.2f}/₹{target:.2f}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Use /goal_update {name} <amount> to add savings")
        await ctx.respond(embed=embed)
        
    except Exception as e:
        print(f"Error setting goal: {e}")
        await ctx.respond("⚠️ An error occurred while setting your goal.")
    finally:
        conn.close()

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

# 5. FinCoins balance
@bot.slash_command(name="balance", description="Check your FinCoin balance")
async def check_balance(ctx):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.fincoins, 
                   (SELECT COUNT(*) FROM transactions WHERE user_id = ?) as tx_count,
                   (SELECT SUM(amount) FROM transactions WHERE user_id = ?) as net_change
            FROM users u 
            WHERE user_id = ?
        """, (ctx.user.id, ctx.user.id, ctx.user.id))
        
        result = cursor.fetchone()
        if result:
            embed = discord.Embed(
                title="💰 Your FinCoin Status",
                color=discord.Color.gold()
            )
            embed.add_field(name="Current Balance", value=f"{result['fincoins']} FinCoins")
            embed.add_field(name="Total Transactions", value=result['tx_count'])
            embed.add_field(name="Net Change", value=result['net_change'] or 0)
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("💰 Your balance: 100 FinCoins (default)")
    finally:
        conn.close()

# 6. Transaction history
@bot.slash_command(name="transactions", description="View your transaction history")
async def view_transactions(ctx):
    conn = sqlite3.connect("finny.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT amount, type, description, timestamp 
    FROM transactions 
    WHERE user_id = ?
    ORDER BY timestamp DESC
    LIMIT 10
    """, (ctx.user.id,))
    
    transactions = cursor.fetchall()
    conn.close()
    
    if not transactions:
        await ctx.respond("📊 No transactions yet! Play /spendgame to get started.")
        return
    
    embed = discord.Embed(
        title=f"📊 {ctx.user.name}'s Transaction History",
        color=discord.Color.blue()
    )
    
    for amount, tx_type, description, timestamp in transactions:
        sign = "+" if amount >= 0 else ""
        embed.add_field(
            name=f"{tx_type.capitalize()} ({sign}{amount} FinCoins)",
            value=f"{description}\n`{timestamp}`",
            inline=False
        )
    
    await ctx.respond(embed=embed)

# 7. Tracking goals
@bot.slash_command(name="mygoals", description="List your savings goals")
async def list_goals(ctx):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, target, saved, (saved/target)*100 as progress 
            FROM goals 
            WHERE user_id = ?
        """, (ctx.user.id,))
        
        goals = cursor.fetchall()
        if not goals:
            await ctx.respond("You haven't set any goals yet! Use `/goal` to create one.")
            return
            
        embed = discord.Embed(
            title="🎯 Your Savings Goals",
            color=discord.Color.green()
        )
        
        for goal in goals:
            completed = " ✅" if goal['saved'] >= goal['target'] else ""
            progress_bar = "🟩" * int(goal['progress']/10) + "⬜" * (10 - int(goal['progress']/10))
            embed.add_field(
                name=f"{goal['name']}{completed}",
                value=f"₹{goal['saved']:.2f}/₹{goal['target']:.2f}\n{progress_bar} {goal['progress']:.1f}%",
                inline=False
            )
        
        await ctx.respond(embed=embed)
    finally:
        conn.close()

# 8. Update goal progress
@bot.slash_command(name="goal_update", description="Update your savings goal progress")
async def update_goal(
    ctx: discord.ApplicationContext,
    name: Option(str, "Goal name to update (e.g. 'GTA VI')"),
    amount: Option(float, "Amount to add to your savings")
):
    """Update your savings goal progress"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if goal exists
        cursor.execute(
            "SELECT target, saved FROM goals WHERE user_id = ? AND name = ?",
            (ctx.user.id, name)
        )
        goal = cursor.fetchone()
        
        if not goal:
            await ctx.respond(f"❌ You don't have a goal named '{name}'. Create it with `/goal` first.")
            return
            
        target = goal['target']
        current_saved = goal['saved']
        new_saved = current_saved + amount
        
        # Update the goal
        cursor.execute(
            "UPDATE goals SET saved = ? WHERE user_id = ? AND name = ?",
            (new_saved, ctx.user.id, name)
        )
        
        # Check if goal is accomplished
        if new_saved >= target:
            accomplishment_msg = " 🎉 GOAL ACCOMPLISHED! 🎉"
            # Optional: Award bonus FinCoins for completing goal
            cursor.execute(
                "UPDATE users SET fincoins = fincoins + ? WHERE user_id = ?",
                (target * 0.1, ctx.user.id)  # 10% bonus of target
            )
        else:
            accomplishment_msg = ""
            
        conn.commit()
        
        progress = (new_saved / target) * 100
        progress_bar = "🟩" * int(progress / 10) + "⬜" * (10 - int(progress / 10))
        
        embed = discord.Embed(
            title=f"💰 Updated Goal: {name}",
            color=discord.Color.green() if new_saved >= target else discord.Color.blue()
        )
        embed.add_field(
            name="Progress",
            value=f"₹{new_saved:.2f}/₹{target:.2f}\n{progress_bar} {progress:.1f}%{accomplishment_msg}",
            inline=False
        )
        
        await ctx.respond(embed=embed)
        
    except Exception as e:
        print(f"Error updating goal: {e}")
        await ctx.respond("⚠️ An error occurred while updating your goal.")
    finally:
        conn.close()

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
