
from asyncio.tasks import wait
import os
import matplotlib.pyplot as plt
import numpy as np
import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import time
import threading
from discord.utils import get
from collections import Counter
import asyncio
from discord.ext import tasks
import datetime
import socketio
import uuid
import requests
from flask import jsonify
import logging


# logging.basicConfig(filename='main.log', level=logging.DEBUG)


# sio = socketio.Client()



# with open('musicdatabase.txt', 'r') as f:
#     musicdatabase = eval(f.read())


# def run():
#     sio.connect('http://127.0.0.1:5000', wait = True)
#     while True:
#         with open('musicdatabase.txt', 'r') as f:
#             musicdatabase = eval(f.read())
        
#         ordered = {}
#         final = []
#         for music in musicdatabase:
#             if 'upvotes' in musicdatabase[music]:
#                 ordered[music] = len(musicdatabase[music]['upvotes'])
#         for link in sorted(ordered, key=ordered.get, reverse=True):
#             final.append([link, ordered[link], musicdatabase[link]['added_by']])
#         sio.emit('msg', final)
#         sio.sleep(3)

# sio.start_background_task(target = run)


with open('database.txt', 'r') as f:
    database = eval(f.read())


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        members = self.get_all_members()
        for member in members:
            role_names = [role.name for role in member.roles]
            if member.name not in database:
                role_names = [role.name for role in member.roles]
                if 'Bots' in role_names:
                    pass
                else:
                    database[member.name] = {'coins': 100}
        

intents = discord.Intents.default()
intents.members = True
client = MyClient(intents = intents)


temp_status  = {}


def add_coins(stream_state, user, cointype):
    with open('database.txt', 'r') as f:
        database = eval(f.read())
    if stream_state:
        if cointype in database[user]:
            database[user][cointype] = round(database[user][cointype] + 1, 2)
        else:
            database[user][cointype] =  100
    else:
        if cointype in database[user]:
            database[user][cointype] = round(database[user][cointype] + 0.33, 2)
        else:
            database[user][cointype] =  100
    print(f'Coins to : {user}')
    with open('database.txt', 'w', encoding='utf-8') as f:
        f.write(str(database))


def ticksystem():
    while True:
        with open('database.txt', 'r') as f:
            database = eval(f.read())
        names = [user for user in database]
        for user in names:
            if user in temp_status:
                state = temp_status[user]
                try:
                    channelid = str(state.channel.id)
                except:
                    channelid = str(0)
                channel_state = str(state.channel)
                stream_state = state.self_stream
                if channel_state != 'None':
                    if channelid != str(847583212926009374):
                        add_coins(stream_state, user, 'coins')
                    else:
                        add_coins(stream_state, user, 'shekels')


            with open('database.txt', 'r') as f:
                database = eval(f.read())
            
            if 'Timer' in database[user]:
                if database[user]['Timer'] <= 0:
                    database[user]['Timer'] = 0
                else:
                    database[user]['Timer'] -= 10
            
            if 'Crowned' not in database[user]:
                database[user]['Crowned'] = False
                
            if database[user]['Crowned']:
                if 'coins' in database[user]:
                    database[user]['coins'] = round(database[user]['coins'] + 0.1, 2)
                    print(f'Crowned Coins to : {user}')
                else:
                    database[user]['coins'] =  100
            
            with open('database.txt', 'w', encoding='utf-8') as f:
                f.write(str(database))

        time.sleep(10)

t = threading.Thread(target=ticksystem)
t.daemon = False
t.start()


@client.event
async def on_voice_state_update(member, before, after):
    with open('database.txt', 'r') as f:
        database = eval(f.read())
    if member.name not in database:
        database[member.name] = {'coins': 1000}
        print(member.name)
        with open('database.txt', 'w', encoding='utf-8') as f:
            f.write(str(database))
    

    temp_status[member.name] = after
    if member.name in database:
        if 'Timer' in database[member.name]:
            curr_timer = database[member.name]['Timer']
            role_names = [role.name for role in member.guild.roles]
            if curr_timer <= 0 and 'Crazy Blazin Gold' in role_names:
                role = get(member.guild.roles, name='Crazy Blazin Gold')
                await member.remove_roles(role)



# @client.event
# async def on_reaction_add(reaction, user):
#     if str(reaction.message.channel.id) == str(795738540251545620):
#         if reaction.emoji == '💥':
#             with open('musicdatabase.txt', 'r') as f:
#                 musicdatabase = eval(f.read())
#             if reaction.message.content in musicdatabase:
#                 musicdatabase[reaction.message.content]['upvotes'].append(reaction.message.author.name)

#             with open('musicdatabaseBACKUP.txt', 'w') as f:
#                 f.write(str(musicdatabase))
            
#             with open('musicdatabase.txt', 'w') as f:
#                 f.write(str(musicdatabase))


# @client.event
# async def on_reaction_remove(reaction, user):
#     if str(reaction.message.channel.id) == str(795738540251545620):
#         if reaction.emoji == '💥':
#             with open('musicdatabase.txt', 'r') as f:
#                 musicdatabase = eval(f.read())
#             with open('musicdatabaseBACKUP.txt', 'w') as f:
#                 f.write(str(musicdatabase))
#             if reaction.message.content in musicdatabase:
#                 if reaction.message.author.name in musicdatabase[reaction.message.content]['upvotes']:
#                     musicdatabase[reaction.message.content]['upvotes'].remove(reaction.message.author.name)
#             with open('musicdatabase.txt', 'w') as f:
#                 f.write(str(musicdatabase))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if str(message.channel.id) == str(795738540251545620):
        with open('musicdatabase.txt', 'r') as f:
            musicdatabase = eval(f.read())
        with open('musicdatabaseBACKUP.txt', 'w') as f:
                f.write(str(musicdatabase))
        if str(message.content) not in musicdatabase:
            musicdatabase[message.content] = {}
            musicdatabase[message.content]['upvotes'] = []
            musicdatabase[message.content]['added_by'] = message.author.name
        with open('musicdatabase.txt', 'w') as f:
            f.write(str(musicdatabase))

    if message.content.startswith('!bal'):
        with open('database.txt', 'r') as f:
            database = eval(f.read())
        value = database[message.author.name]['coins']
        if 'spankcoin' in database[message.author.name]:
            valuespank = database[message.author.name]['spankcoin']
        if 'shekels' in database[message.author.name]:
            shekval = database[message.author.name]['shekels']
        else:
            shekval = 100
            database[message.author.name]['shekels'] = shekval
        embed = discord.Embed(title=f"Balance", description=f"{message.author.name} current balance") #,color=Hex code

        # if 'spankcoin' in database[message.author.name]:
        #     embed.add_field(name=f"Spank coins", value=f'{round(valuespank,2)} <:raised_hands_tone1:859521216115900457>')
        embed.add_field(name=f"Crazy Blazin Coins", value=f'{round(value,2)} <:CBCcoin:831506214659293214>')
        embed.add_field(name=f"Sheqalim", value=f'₪ {round(shekval,2)}')
        await message.channel.send(embed=embed)


    if message.content.startswith('!transfer'):
        msgsplit = message.content.split(' ')
        if message.author.name == 'Foxxravin':
                
            if len(msgsplit) > 3 or len(msgsplit) < 3:
                await message.channel.send(f'Too many or few arguments. Use !transfer <user> <amount>')
            else:
                amount = int(msgsplit[2])
                account = str(msgsplit[1])
                with open('database.txt', 'r') as f:
                    users = eval(f.read())
                if account in users:
                    if 'spankcoin' in users[account]:
                        users[account]['spankcoin'] += amount
                    else:
                        users[account]['spankcoin'] = amount

                    await message.channel.send(f'{message.author.name} sent {amount} <:raised_hands_tone1:859521216115900457> (spank coins) to {account}')                    
                    with open('database.txt', 'w') as f:
                        f.write(str(users))
                else:
                    await message.channel.send(f'User does not exist!')
                
        else:
            await message.channel.send(f'You are not Foxxravin. (Spank bank)')


    
    if message.content.startswith('!buy gold'):
        
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) < 2:
            await message.channel.send(f'Too many or few arguments. Use !buy gold')
        else:
            with open('database.txt', 'r') as f:
                users = eval(f.read())
            if 1000 <= users[message.author.name]['coins']:
                users[message.author.name]['coins'] -= 1000

                member = message.author
                role = get(member.guild.roles, name='Crazy Blazin Gold')
                await member.add_roles(role)
                # await bot.remove_roles(user, 'member')
                await message.channel.send(f'{message.author.name} Bought Crazy Blazin Gold Role for one month!')

                users[message.author.name]['Timer'] = 2592000
                with open('database.txt', 'w') as f:
                    f.write(str(users))

            else:
                await message.channel.send(f'{message.author.name} does not have enough <:CBCcoin:831506214659293214> (CBC) to buy Crazy Blazin Gold! Price: 1000 <:CBCcoin:831506214659293214> (CBC)')
                

    if message.content.startswith('!gamble '):
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) < 2:
            await message.channel.send(f'Too many or few arguments. Use !gamble <amount>')
        else:
            with open('database.txt', 'r') as f:
                users = eval(f.read())
            amount = float(str_split[1])*np.sign(float(str_split[1]))
            if amount <= users[message.author.name]['coins']:
                users[message.author.name]['coins'] -= amount

                roll = np.random.randint(0, 101)
                if roll > 50:
                    users[message.author.name]['coins'] += 2*amount
                    users[message.author.name]['coins'] = round(users[message.author.name]['coins'], 2)
                    await message.channel.send(f'{message.author.name} Rolled {roll} and won {round(2*amount,2)}<:CBCcoin:831506214659293214>  :partying_face:')
                else:
                    await message.channel.send(f'{message.author.name} Rolled {roll} and lost {amount} <:CBCcoin:831506214659293214>! :frowning2:')

                with open('database.txt', 'w') as f:
                    f.write(str(users))

            else:
                await message.channel.send(f'{message.author.name} does not have enough <:CBCcoin:831506214659293214> (CBC) to gamble!')


    if message.content.startswith('!uwuprison'):
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) < 2:
            await message.channel.send(f'Too many or few arguments. Use !uwuprison <target>')
        else:
            with open('database.txt', 'r') as f:
                users = eval(f.read())
            
            target = str(str_split[1])
            if 1 <= users[message.author.name]['coins']:
                users[message.author.name]['coins'] -= 1

                await message.channel.send(f'{message.author.name} sent {target} to UwU prison <:aegao:849030455189438485> !')
                with open('database.txt', 'w') as f:
                    f.write(str(users))
            else:
                await message.channel.send(f'{message.author.name} does not have enough <:CBCcoin:831506214659293214> (CBC) to send {target} to UwU prison!')
                
    
    if message.content.startswith('!crown'):
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) < 2:
            await message.channel.send(f'Too many or few arguments. Use !crown <target>')
        else:
            if message.author.name == 'JordanLTD':
                with open('database.txt', 'r') as f:
                    users = eval(f.read())
                
                target = str_split[1]
                members = client.get_all_members()

                for user in users:
                    if 'Crowned' not in users[user]:
                        users[user]['Crowned'] = False
                    if users[user]['Crowned']:
                        users[user]['Crowned'] = False
                    if user == target:
                        users[user]['Crowned'] = True

                for member in members:
                    if member.name == target:
                        role = get(member.guild.roles, name='Crowned')
                        await member.add_roles(role)
                    else:
                        role_names = [role.name for role in member.roles]
                        if 'Crowned' in role_names:
                            role = get(member.guild.roles, name='Crowned')
                            await member.remove_roles(role)

                with open('database.txt', 'w') as f:
                    f.write(str(users))

                await message.channel.send(f'{target} has been crowned by {message.author.name}:princess:, {target} will now have passive <:CBCcoin:831506214659293214> income until the crown is given to someone else or removed!')
            else:
                await message.channel.send(f'Only Yarden/Jordan/ירדן‎ :princess: can give someone the crown!‎')
    
    if message.content.startswith('!removecrown'):
        if message.author.name == 'JordanLTD':
            with open('database.txt', 'r') as f:
                users = eval(f.read())
            for user in users:
                if 'Crowned' not in users[user]:
                    users[user]['Crowned'] = False
                if users[user]['Crowned']:
                    users[user]['Crowned'] = False
                
            with open('database.txt', 'w') as f:
                f.write(str(users))

            members = client.get_all_members()
            for member in members:
                role_names = [role.name for role in member.roles]
                if 'Crowned' in role_names:
                    role = get(member.guild.roles, name='Crowned')
                    await member.remove_roles(role)

            await message.channel.send(f'{message.author.name}:princess: has removed the crown from the holder!')
        else:
            await message.channel.send(f'Only Yarden/Jordan/ירדן‎ :princess: can remove crown!')

client.run(k)