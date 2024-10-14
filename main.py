import discord
import asyncio
import random
from datetime import timedelta, datetime
from discord.ext import commands
from beartype import beartype
from loguru import logger
import toml
import threading
import os

from utils.github_con import approve_pull_request
from utils.dbhandler import DataBaseHandler
from config import config
from dataclasses import dataclass

intents = discord.Intents.default()
intents.voice_states = True  # Track voice states
intents.message_content = True  # To access message content if needed
intents.guilds = True  # To get guild info and members

@dataclass
class TrackedMessage:
    url: str
    count: int = 0

class MyBot(commands.Bot):
    async def setup_hook(self):
        # Create a task to process the PR queue
        self.loop.create_task(process_pr_queue())

bot = MyBot(command_prefix='!', intents=intents)
db_handler = DataBaseHandler()

# Variable to track whether the multiplier is active
multiplier_active = False
multiplier_active_special = False

# tracked messages for PR approvals
tracked_messages = {}

# Track the last time someone was awarded for being the first to join any voice channel
last_awarded_time = None

from flask import Flask, request
import json

app = Flask(__name__)
pr_queue = asyncio.Queue()

@app.route('/webhook', methods=['POST'])
async def webhook():
    logger.info("Webhook received!")
    try:
        data = json.loads(request.data)
        if data['action'] == 'opened':
            pr_url = data['pull_request']['html_url']
            #channel = bot.get_channel(config.CHAT_CHANNEL_ID)  # Replace with your Discord channel ID
            asyncio.run_coroutine_threadsafe(pr_queue.put(pr_url), bot.loop)

            # try:
            #     # Use asyncio.wait_for to set a timeout for the task
            #     await asyncio.wait_for(post_pr_message(channel, pr_url), timeout=10)  # Set timeout in seconds
            # except asyncio.TimeoutError:
            #     logger.error("Timeout occurred while posting PR message")
            #     return 'Timeout', 504  # HTTP 504 Gateway Timeout
        
        return pr_url, 200
    except Exception as e:
        logger.exception(e)
        return '', 500

# Function to add coins to a user
@beartype
def add_coins(user_id: int, username: str, amount: int) -> None:
    db_handler.add_coins(user_id=user_id, username=username, amount=amount)


@bot.event
async def on_voice_state_update(member, before, after):
    global last_awarded_time

    # Check if the member has joined a voice channel
    if after.channel is not None and before.channel != after.channel:
        now = datetime.utcnow()
        # If there hasn't been a first joiner in the past 24 hours
        if last_awarded_time is None or now - last_awarded_time >= timedelta(days=config.FIRST_IN_CHANNEL_TIMER_DAYS):
            # Award coins to the first joiner in 24 hours
            first_join_reward = config.FIRST_IN_CHANNEL_REWARD_COINS  # Adjust the reward amount as you wish
            db_handler.add_coins(user_id=member.id, username=member.display_name, amount=first_join_reward)

            # Send a message to the specific text channel
            announcement_channel = bot.get_channel(config.CHAT_CHANNEL_ID)
            if announcement_channel:
                await announcement_channel.send(f"🎉 {member.display_name} is the first to join a voice channel in the past 24 hours and earns {first_join_reward} CBC coins!")

            # Update the last awarded time
            last_awarded_time = now


# Background task to give coins to users in voice channels
async def give_coins():
    await bot.wait_until_ready()
    global multiplier_active
    global multiplier_active_special

    while not bot.is_closed():
        for guild in bot.guilds:
            # Fetch leaderboard from the database (this is an example, adjust for your system)
            for vc in guild.voice_channels:
                for member in vc.members:
                    if not member.bot:  # Skip bots
                        coins_to_give = config.PAY_AMOUNT

                        # Apply 2x multiplier if it's active
                        if multiplier_active:
                            coins_to_give *= config.EVENT_MULTIPLIER
                        if multiplier_active_special:
                            coins_to_give *= config.SPECIAL_EVENT_MULTIPLIER

                        # Add bonus coins if the member is streaming
                        if member.voice.self_stream:
                            coins_to_give += config.STREAM_BONUS

                        # Give coins to the member
                        db_handler.add_coins(user_id=member.id, username=member.display_name, amount=coins_to_give)

        # Wait for the next cycle
        await asyncio.sleep(config.GRACIOUS_DELAY)


# Background task to handle the random multiplier
async def manage_multiplier():
    await bot.wait_until_ready()
    global multiplier_active

    # Fetch the specific channel by ID
    channel = bot.get_channel(config.CHAT_CHANNEL_ID)

    while not bot.is_closed():
        # Calculate when the next 24-hour period starts
        next_day = datetime.utcnow() + timedelta(days=1)

        # Choose a random time during the next 24 hours for the multiplier to start
        random_minutes = random.randint(0, config.RANDOM_TIME_WITHIN)  # Random time within 24 hours (in minutes)
        multiplier_start = datetime.utcnow() + timedelta(minutes=random_minutes)

        # Wait until the random start time
        time_to_wait = (multiplier_start - datetime.utcnow()).total_seconds()
        await asyncio.sleep(time_to_wait)

        # Activate the multiplier for 30 minutes
        multiplier_active = True
        logger.info(f"{config.EVENT_MULTIPLIER}x coin multiplier has started!")

        # Send a message to the channel to notify users
        if channel:
            await channel.send(f"🚀 **{config.EVENT_MULTIPLIER}x Coin Multiplier is now active!** Earn double CBC coins for the next {config.BONUS_TIMER_MINUTES} minutes!")

        await asyncio.sleep(config.BONUS_TIMER_MINUTES * 60)
        multiplier_active = False
        logger.info(f"{config.EVENT_MULTIPLIER}x coin multiplier has ended!")

        # Send a message to the channel when the multiplier ends
        if channel:
            await channel.send(f"⏳ **The {config.EVENT_MULTIPLIER}x Coin Multiplier has ended.** Stay tuned for the next random bonus!")

        # Sleep until the start of the next 24-hour period
        time_to_next_day = (next_day - datetime.utcnow()).total_seconds()
        await asyncio.sleep(time_to_next_day)


@bot.event
async def on_ready():
    # Fetch the specific channel by ID
    channel = bot.get_channel(config.CHAT_CHANNEL_ID)
    # read version with toml
    with open("pyproject.toml", "r") as f:
        data = toml.load(f)
        version = data["tool"]["poetry"]["version"]
    if channel:
        # await channel.send(f"🤖 **Bot is online!** Version: {version}")
        pass
    logger.info(f"🤖 Bot is online! Version: {version}")

    bot.loop.create_task(give_coins())
    bot.loop.create_task(manage_multiplier())  # Start the multiplier task


@bot.command()
async def balance(ctx, member: discord.Member = None):
    """Check your coin balance."""
    if member is None:
        member = ctx.author
    result = db_handler.get_coins(user_id=member.id)
    if result is None:
        await ctx.send(f"{member.display_name} has no coins yet.")
    else:
        await ctx.send(f"{member.display_name} has {result[0]} CBC coins.")


@bot.command()
async def reset_coins(ctx, member: discord.Member = None):
    """Reset a member's coin balance."""
    if member is None:
        member = ctx.author
    db_handler.reset_coins(user_id=member.id)
    await ctx.send(f"{member.display_name}'s coins have been reset to 0.")


@bot.command()
async def leaderboard(ctx):
    """Display the top 10 users with the most coins."""
    top_users = db_handler.get_top_users(limit=10)  # Assumes db_handler has a method for this
    if not top_users:
        await ctx.send("No one has earned any coins yet.")
        return

    leaderboard_text = "**Top Coin Leaders:**\n"
    position = 1
    for _, username, coins in top_users:
        if position == 1:
            leaderboard_text += f"🥇 **{username}**: {coins} coins\n"
        elif position == 2:
            leaderboard_text += f"🥈 **{username}**: {coins} coins\n"
        elif position == 3:
            leaderboard_text += f"🥉 **{username}**: {coins} coins\n"
        else:
            leaderboard_text += f"{position}. **{username}**: {coins} coins\n"
        position += 1

    embed = discord.Embed(title="Leaderboard", description=leaderboard_text, color=0x00ff00)
    await ctx.send(embed=embed)


# Parse the pull request URL (to extract repo name and PR number)
def parse_pr_url(pr_url):
    parts = pr_url.split('/')
    repo_name = f"{parts[3]}/{parts[4]}"
    pr_number = int(parts[-1])
    return repo_name, pr_number


@bot.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    if user == bot.user:
        return  # Skip bot's own reactions

    # Check if the message is tracked for a pull request
    if message.id in tracked_messages:
        tracked_message = tracked_messages[message.id]
        if reaction.emoji == '👍':  # Check if the reaction is the specific emoji
            tracked_message.count += 1
            if tracked_message.count >= config.REACTION_THRESHOLD:
                repo_name, pr_number = parse_pr_url(tracked_message.url)
                approve_pull_request(repo_name, pr_number)
                await message.channel.send(f"PR {tracked_message.url} has been approved with {config.REACTION_THRESHOLD} 👍 reactions!")
    
async def process_pr_queue():
    await bot.wait_until_ready()
    while not bot.is_closed():
        pr_url = await pr_queue.get()
        channel = bot.get_channel(config.CHAT_CHANNEL_ID)  # Replace with your Discord channel ID
        message = await channel.send(f'A new PR has been created: {pr_url}')
        tracked_messages[message.id] = TrackedMessage(url = pr_url)
        await message.add_reaction('👍')
        pr_queue.task_done()
# @bot.command()
# async def post_pr_message(ctx, pr_url):
#     message = await ctx.send(f'A new PR has been created: {pr_url}')
#     tracked_messages[message.id] = 0
#     await message.add_reaction('👍')



# Example list of items (weapons and armors)
ITEMS = {
    'Sword': {
        'type': 'weapon',
        'damage_range': (15, 25),
        'accuracy': 0.9,
        'crit_chance': 0.2,
        'armor_penetration': 5,
    },
    'Axe': {
        'type': 'weapon',
        'damage_range': (20, 30),
        'accuracy': 0.75,
        'crit_chance': 0.15,
        'armor_penetration': 3,
    },
    'Bow': {
        'type': 'weapon',
        'damage_range': (10, 20),
        'accuracy': 0.8,
        'crit_chance': 0.25,
        'armor_penetration': 2,
    },
    'Dagger': {
        'type': 'weapon',
        'damage_range': (5, 15),
        'accuracy': 0.95,
        'crit_chance': 0.35,
        'armor_penetration': 1,
    },
    'Spear': {
        'type': 'weapon',
        'damage_range': (18, 28),
        'accuracy': 0.85,
        'crit_chance': 0.1,
        'armor_penetration': 4,
    },
    'Magic Staff': {
        'type': 'weapon',
        'damage_range': (12, 22),
        'accuracy': 0.85,
        'crit_chance': 0.25,
        'armor_penetration': 999,  # Ignores armor completely
    },
    'Flamethrower': {
        'type': 'weapon',
        'damage_range': (8, 18),
        'accuracy': 0.8,
        'crit_chance': 0.2,
        'armor_penetration': 0,
        'damage_over_time': 5,  # Damage per turn
        'dot_duration': 3,  # Lasts for 3 turns
    },
    'Poison Dagger': {
        'type': 'weapon',
        'damage_range': (5, 15),
        'accuracy': 0.9,
        'crit_chance': 0.3,
        'armor_penetration': 1,
        'poison_damage': 4,  # Damage dealt per turn
        'poison_duration': 3,  # Lasts for 3 turns
    },
    'Leather Armor': {
        'type': 'armor',
        'evade': 0.1,
        'health': 10,
        'flat_damage_reduction': 5,
        'percent_damage_reduction': 0.1,
        'thorn_damage': 3,
    },
    'Plate Armor': {
        'type': 'armor',
        'evade': 0.05,
        'health': 20,
        'flat_damage_reduction': 10,
        'percent_damage_reduction': 0.2,
        'thorn_damage': 5,
    },
    'Shield of Reflection': {
        'type': 'armor',
        'evade': 0.05,
        'health': 15,
        'flat_damage_reduction': 8,
        'percent_damage_reduction': 0.15,
        'thorn_damage': 0,  # No thorn damage, reflects damage instead
        'reflect_percentage': 0.2,  # Reflects 20% of damage back
    },
    'Cloak of Invisibility': {
        'type': 'armor',
        'evade': 0.25,  # 25% chance to evade attacks
        'health': 5,
        'flat_damage_reduction': 2,
        'percent_damage_reduction': 0.05,
        'thorn_damage': 0,  # No thorn damage
    },
    'Mithril Armor': {
        'type': 'armor',
        'evade': 0.1,
        'health': 10,
        'flat_damage_reduction': 15,
        'percent_damage_reduction': 0.1,
        'thorn_damage': 1,
    },
}


FULL_HEALTH = 100  # Default full health for each player
KNUCKLE_FIST_DAMAGE = 5  # Default damage for knuckle fist

def calculate_damage(item):
    """Calculate the damage for a weapon, considering critical hits, accuracy, and armor penetration."""
    if item['type'] == 'weapon':
        # Check if the attack hits based on accuracy
        if random.random() > item['accuracy']:
            return 0, "missed"  # Attack missed

        # Calculate base damage
        damage = random.randint(*item['damage_range']) if 'damage_range' in item else KNUCKLE_FIST_DAMAGE

        # Check for critical hit
        if random.random() < item['crit_chance']:
            damage *= 2  # Double damage on crit
            return damage, "critical hit"

        return damage, "hit"  # Regular hit
    else:
        damage = KNUCKLE_FIST_DAMAGE
        return damage, "hit"  # Regular hit

async def start_hunger_games(ctx, database_handler, voice_channel_members):
    """Start the Hunger Games by assigning items and logging the battle in a text file."""
    
    log = []  # List to accumulate log entries
    embed_messages = []  # List to hold embed messages

    # Step 1: Assign random items and set initial health
    log.append("The Hunger Games have begun! Assigning items and setting health...\n")
    
    # Temporary storage for player states
    players = {}
    
    for member in voice_channel_members:
        item = random.choice(list(ITEMS.keys()))
        players[member.id] = {
            'name': member.display_name,
            'item': item,
            'health': FULL_HEALTH + ITEMS[item].get('health', 0),  # Reset health to full + armor health
        }
        log.append(f"{member.display_name} has been assigned a **{item}** and has **{FULL_HEALTH + ITEMS[item].get('health', 0)} health**.\n")
        
        # Create embed for the item
        embed = discord.Embed(title=f"Item Assigned: {item}", color=discord.Color.blue())
        item_data = ITEMS[item]

        embed.add_field(name="Type", value=item_data['type'].capitalize(), inline=False)
        
        if item_data['type'] == 'weapon':
            embed.add_field(name="Damage Range", value=f"{item_data['damage_range'][0]} - {item_data['damage_range'][1]}", inline=True)
            embed.add_field(name="Accuracy", value=f"{item_data['accuracy'] * 100}%", inline=True)
            embed.add_field(name="Critical Chance", value=f"{item_data['crit_chance'] * 100}%", inline=True)
            embed.add_field(name="Armor Penetration", value=item_data['armor_penetration'], inline=True)
            embed.set_footer(text="⚔️ Weapon Stats")
        elif item_data['type'] == 'armor':
            embed.add_field(name="Evade Chance", value=f"{item_data['evade'] * 100}%", inline=True)
            embed.add_field(name="Health Bonus", value=item_data.get('health', 0), inline=True)
            embed.add_field(name="Flat Damage Reduction", value=item_data.get('flat_damage_reduction', 0), inline=True)
            embed.add_field(name="Percent Damage Reduction", value=f"{item_data.get('percent_damage_reduction', 0) * 100}%", inline=True)
            embed.set_footer(text="🛡️ Armor Stats")
        
        # Add the embed to the list
        embed_messages.append(embed)

    # Step 2: Send embed messages for assigned items
    for embed in embed_messages:
        await ctx.send(embed=embed)

    # Simulate battle
    alive_players = voice_channel_members[:]
    log.append("Let the battle begin!\n")

    while len(alive_players) > 1:
        # Pick attacker and defender
        attacker = random.choice(alive_players)
        defender = random.choice([p for p in alive_players if p != attacker])

        # Retrieve attacker and defender's item and health
        attacker_item = players[attacker.id]['item']
        defender_item = players[defender.id]['item']
        attacker_health = players[attacker.id]['health']
        defender_health = players[defender.id]['health']

        # Calculate the damage based on the attacker's item properties
        attack_damage, attack_type = calculate_damage(ITEMS[attacker_item])

        # Apply armor penetration
        armor_penetration = ITEMS[attacker_item].get('armor_penetration', 0)
        flat_reduction = ITEMS[defender_item].get('flat_damage_reduction', 0)
        percent_reduction = ITEMS[defender_item].get('percent_damage_reduction', 0)

        # Calculate effective damage reduction
        effective_reduction = max(0, flat_reduction - armor_penetration)
        damage_after_reduction = max(0, attack_damage - effective_reduction)
        damage_after_reduction *= (1 - percent_reduction)  # Apply percentage reduction

        # Update defender's health if attack wasn't missed
        thorn_damage = ITEMS[defender_item].get('thorn_damage', 0)  # Thorn damage for the defender
        if attack_damage > 0:
            new_health = defender_health - damage_after_reduction
            players[defender.id]['health'] = new_health
            
            # Apply thorn damage to attacker if the defender has armor
            if thorn_damage > 0:
                players[attacker.id]['health'] -= thorn_damage  # Apply thorn damage to attacker
                log.append(f"{players[defender.id]['name']}'s armor deals {thorn_damage} thorn damage to {players[attacker.id]['name']}!\n")

            # Handle special item effects
            if attacker_item == 'Flamethrower':
                # Apply damage over time for Flamethrower
                for _ in range(ITEMS[attacker_item]['dot_duration']):
                    players[defender.id]['health'] -= ITEMS[attacker_item]['damage_over_time']
                    log.append(f"{players[defender.id]['name']} is burned by the Flamethrower, taking {ITEMS[attacker_item]['damage_over_time']} damage over time!\n")

            if attacker_item == 'Poison Dagger':
                # Apply poison damage over turns
                for _ in range(ITEMS[attacker_item]['poison_duration']):
                    players[defender.id]['health'] -= ITEMS[attacker_item]['poison_damage']
                    log.append(f"{players[defender.id]['name']} is poisoned by the Poison Dagger, taking {ITEMS[attacker_item]['poison_damage']} poison damage!\n")

            log.append(f"{players[attacker.id]['name']} attacks {players[defender.id]['name']} with a **{attacker_item}**, dealing {damage_after_reduction} damage!\n")
        else:
            log.append(f"{players[attacker.id]['name']} attempted to attack {players[defender.id]['name']} with a **{attacker_item}**, but it {attack_type}!\n")

        # Check if defender is still alive
        if players[defender.id]['health'] <= 0:
            alive_players.remove(defender)
            log.append(f"{players[defender.id]['name']} has been eliminated!\n")

    # Determine the winner
    winner = alive_players[0]
    log.append(f"The winner is **{players[winner.id]['name']}** with **{players[winner.id]['health']} health remaining**!\n")

    # Write the log to a text file
    file_path = f"{ctx.guild.id}_hunger_games_log.txt"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(log)

    # Send the log file in the Discord channel
    await ctx.send(file=discord.File(file_path))
    await ctx.send(f"The Hunger Games have ended!, winner is **{players[winner.id]['name']}** with **{players[winner.id]['health']} health remaining**!\n")

@bot.command(name="hunger_game")
async def hunger_game(ctx):
    """Start the Hunger Game in the current voice channel."""
    voice_channel = ctx.author.voice.channel  # Get the user's voice channel
    if not voice_channel:
        await ctx.send("You're not in a voice channel!")
        return

    members = voice_channel.members
    if len(members) < 2:
        await ctx.send("Not enough players in the voice channel to start the game!")
        return

    db_handler = DataBaseHandler()
    await start_hunger_games(ctx, db_handler, members)



def run_flask():
    app.run(port=config.WEBHOOK_PORT)


if __name__ == "__main__":
    # Start the Flask server in a separate thread
    try:
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()
        bot.run(config.TOKEN)
    except KeyboardInterrupt:
        flask_thread.join()
        logger.info("Bot stopped.")
