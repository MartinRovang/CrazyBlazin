
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

# client = commands.Bot(command_prefix='!')

#https://discordapp.com/developers


class Database:
    def __init__(self):
        self.dbName = 'crazy_blazin_database.txt' 
    def read(self):
        with open(self.dbName, 'r') as f:
            return eval(f.read())

    def write(self, users):
        with open(self.dbName, 'w') as f:
            f.write(str(users))



class EventHandler:
    def __init__(self):
        self.events = []
        self.coin_aggregation_members = {}
        self.db = Database()
    
    def current_events(self):
        if len(self.events) < 1:
            return 'No events active'
        else:
            return self.events

    def add_event(self, ticket):
        self.events.append(ticket)

    def raffle_machine(self, event):
        winner = np.random.choice(event.participants, 1)
        return winner

    def coin_aggregation(self):
        users = self.db.read()
        for members in self.coin_aggregation_members:
            state = self.coin_aggregation_members[members]
            channel_state = str(state.channel)
            stream_state = state.self_stream

            if channel_state != 'None':
                if stream_state:
                    users[members]['Coins'] += 15
                    print(f'Stream activity: {members}')
                else:
                    users[members]['Coins'] += 5

                print(f'Coins to : {members}')
        self.db.write(users)
        return users



class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # an attribute we can access from our task
        self.counter = 0
        # start the task to run in the background
        self.add_coins_after_time.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    @tasks.loop(seconds=900) # task runs every 60 seconds
    async def add_coins_after_time(self):
        users = events_handler.db.read()
        events_handler.coin_aggregation()
        print('Coins distributed!')
        probability = np.random.randint(0, 100)
        member = False
        members = self.get_all_members()
        for key in users:
            if 'Timer' in users[key]:
                if users[key]['Timer'] > 0:
                    users[key]['Timer'] -= 900
                else:
                    users[key]['Timer'] = 0
                    # next(user for user in client.users if user.name == key)
                    for mem in members:
                        if mem.name == key:
                            member = mem
                            break
                    if not member:
                        continue
                    role_names = [role.name for role in member.roles]
                    if 'Crazy Blazin Gold' in role_names:
                        role = get(member.guild.roles, name='Crazy Blazin Gold')
                        await member.remove_roles(role)
                events_handler.db.write(users)


        #803982821923356773
        print(probability)
        if probability >= 5:
            channel = self.get_channel(795729201498947624)
            await channel.send('hello')



    @add_coins_after_time.after_loop
    async def after_my_task(self):
        print('help im being violated')
        if (self.add_coins_after_time.is_being_cancelled()):
            print('cancelled')

    @add_coins_after_time.before_loop
    async def before_my_task(self):
        await self.wait_until_ready() # wait until the bot logs in



events_handler = EventHandler()
intents = discord.Intents.default()
intents.members = True
client = MyClient(intents = intents)



class Ticket:
    def __init__(self, description, id, creator):
        self.description = description
        self.id = id
        self.participants = []
        self.creator = creator


@client.event
async def on_voice_state_update(member, before, after):
    member = str(member).split("#")[0]
    print('Changed state: ' + member)
    events_handler.coin_aggregation_members[member] = after


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    with open('crazy_blazin_database.txt', 'r') as f:
        users = eval(f.read())

    
    for user in users:
        if 'Boosters' not in users[user]:

    if message.author.name not in users:
        users[message.author.name] = {'Coins': 25, 'Tickets': 1}
        with open('crazy_blazin_database.txt', 'w') as f:
            f.write(str(users))

    if message.content.startswith('!bal'):
        value = users[message.author.name]['Coins']
        ticket = users[message.author.name]['Tickets']
        await message.channel.send(f'{message.author.name} \n {value} <:CBCcoin:831506214659293214> (CBC) \n {ticket} :tickets: (tickets)')


    if message.content.startswith('!top'):
        index = 1
        with open('crazy_blazin_database.txt', 'r') as f:
            users = eval(f.read())

        embed = discord.Embed(title="Top wealth", description="Top owners of Crazy Blazin Coins") #,color=Hex code
            
        temp_stats = {}
        for key_user in users:
            temp_stats[key_user] = users[key_user]['Coins']
        for key in sorted(temp_stats, key=temp_stats.get, reverse=True):
            if (index < 11):
                embed.add_field(name=f"{index}. {key}", value=f'{users[key]["Coins"]} <:CBCcoin:831506214659293214>')
            else: 
                await message.channel.send(embed=embed)
                return
            index += 1

    if message.content.startswith('!raffle'):
        str_split = message.content.split(' ')
        if len(str_split) < 2:
            await message.channel.send(f'Few arguments. Use !raffle description')

        description = ''
        for idx in range(1, len(str_split)):
            description += str_split[idx] + ' '

        role_names = [role.name for role in message.author.roles]
        if 'SOMEROLE' in role_names or 'Admin' in role_names:
            ticket = Ticket(description, len(events_handler.events)+1, message.author.name)
            embed = discord.Embed(title=f"Raffle ----Raffle startet! [ID {ticket.id}]----", description=f"{description}") #,color=Hex code
            events_handler.add_event(ticket)
            embed.add_field(name=f"Info: ", value=f"""
            1. You need at least 1 :tickets: to join, but adding more ticket increases chance to win.
            2. To join raffle use !join raffleID amount
            """)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f'You need to have admin role to start raffles!')

    if message.content.startswith('!events'):
        with open('crazy_blazin_database.txt', 'r') as f:
            users = eval(f.read())
        for i, event in enumerate(events_handler.events):
            await message.channel.send(f'EventID: {i+1}, Price: {event.price} :tickets:,  Description: {event.description}')
        if len(events_handler.events) < 1:
            await message.channel.send(f'No events active.')
    
    if message.content.startswith('!join'):
        str_split = message.content.split(' ')
        if len(str_split) > 3 or len(str_split) < 2:
            await message.channel.send(f'Too many or few arguments. Use !join raffleID ticket_amount')
        try:
            id = int(str_split[1])
            tickets = int(str_split[2])
        except ValueError:
            await message.channel.send(f'ID needs to be integer!')
        
        EVENT_FOUND = True
        for event in events_handler.events:
            if event.id == id:
                EVENT_FOUND = False
                if tickets <= users[message.author.name]['Tickets']:

                    users[message.author.name]['Tickets'] -= tickets
                    with open('crazy_blazin_database.txt', 'w') as f:
                        f.write(str(users))
                    if message.author.name in event.participants:
                        await message.channel.send(f'{message.author.name} added {tickets} :tickets: to the raffle!')
                    else:
                        await message.channel.send(f'{message.author.name} joined the raffle with {tickets} :tickets:')
                    for i in range(tickets):
                        event.participants.append(message.author.name)
                else:
                    await message.channel.send(f'You do not have enough :tickets: to join raffle!')
        
            counted_tickets = Counter(event.participants)

            embed = discord.Embed(title=f"Raffle {id}", description=f"{event.description}") #,color=Hex code
            for i, key in enumerate(sorted(counted_tickets, key=counted_tickets.get, reverse=True)):
                embed.add_field(name=f"{1+i} {key}", value=f'{counted_tickets[key]} :tickets: ')
            await message.channel.send(embed=embed)
            
        if EVENT_FOUND:
            await message.channel.send(f'This event does not exist!')


    if message.content.startswith('!startraffle'):
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) <= 1:
            await message.channel.send(f'Too many or few arguments. Use !startraffle ID')
        try:
            id = int(str_split[1])
        except ValueError:
            await message.channel.send(f'ID needs to be integer!')
        role_names = [role.name for role in message.author.roles]
        for event in events_handler.events:
            if event.id == id:
                if message.author.name in event.creator or 'Admin' in role_names:
                    await message.channel.send(f':giraffe: :giraffe: Raffle has begun!:giraffe: :giraffe: ')
                    time.sleep(3)
                    await message.channel.send(f':eye: :eye: READY!??:eye: :eye: ')
                    winner = events_handler.raffle_machine(event)
                    time.sleep(3)
                    await message.channel.send(f':partying_face:  :partying_face: WINNER IS: {winner[0]}! :partying_face:  :partying_face: ')
                    events_handler.events.remove(event)
                else:
                    await message.channel.send(f'You are not the raffle creator!')
                    
    if message.content.startswith('!buy tickets'):
        str_split = message.content.split(' ')
        if len(str_split) > 3 or len(str_split) < 2:
            await message.channel.send(f'Too many or few arguments. Use !buy tickets amount')
        try:
            amount = int(str_split[2])
        except ValueError:
            await message.channel.send(f'amount needs to be integer!')

        if 100*amount <= users[message.author.name]['Coins']:

            users[message.author.name]['Tickets'] += amount
            users[message.author.name]['Coins'] -= 100*amount
            with open('crazy_blazin_database.txt', 'w') as f:
                f.write(str(users))
            await message.channel.send(f'{message.author.name} Bought {amount} :tickets: (tickets)')
            

        else:
            await message.channel.send(f'{message.author.name} does not have enough <:CBCcoin:831506214659293214> (CBC) to buy {amount} :tickets:!')
            await message.channel.send(f'Price: <:CBCcoin:831506214659293214> (CBC) per :tickets: .')


    if message.content.startswith('!buy CBG'):
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) < 1:
            await message.channel.send(f'Too many or few arguments. Use !buy CBCGold')

        if 500 <= users[message.author.name]['Coins']:
            users[message.author.name]['Coins'] -= 500
            with open('crazy_blazin_database.txt', 'w') as f:
                f.write(str(users))

            member = message.author
            role = get(member.guild.roles, name='Crazy Blazin Gold')
            await member.add_roles(role)
            # await bot.remove_roles(user, 'member')
            await message.channel.send(f'{message.author.name} Bought Crazy Blazin Gold Role!')

            users[message.author.name]['Timer'] = 2592000

        else:
            await message.channel.send(f'{message.author.name} does not have enough <:CBCcoin:831506214659293214> (CBC) to buy Crazy Blazin Gold!')
            await message.channel.send(f' Price:Crazy Blazin Gold! <:CBCcoin:831506214659293214> (CBC).')


    if message.content.startswith('!giveCBC'):
        str_split = message.content.split(' ')
        print(str_split)
        print(len(str_split))
        if len(str_split) > 3 or len(str_split) < 2:
            await message.channel.send(f'Too many or few arguments. Use !giveCBC username amount')
        try:
            amount = int(str_split[2])
        except ValueError:
            await message.channel.send(f'value needs to be integer!')

        role_names = [role.name for role in message.author.roles]
        reciever_user = str_split[1]
        if 'Admin' in role_names:
            for user in users:
                if user == reciever_user:
                    users[user]['Coins'] += amount
            await message.channel.send(f'{reciever_user} recieved {amount} <:CBCcoin:831506214659293214> (CBC)')
            with open('crazy_blazin_database.txt', 'w') as f:
                f.write(str(users))
        else:
            await message.channel.send('You need to be admin for this command')
    
    if message.content.startswith('!givetickets'):
        str_split = message.content.split(' ')
        if len(str_split) > 3 or len(str_split) < 1:
            await message.channel.send(f'Too many or few arguments. Use !givetickets username amount')
        try:
            amount = int(str_split[2])
        except ValueError:
            await message.channel.send(f'value needs to be integer!')

        role_names = [role.name for role in message.author.roles]
        reciever_user = str_split[1]
        if 'Admin' in role_names:
            for user in users:
                if user == reciever_user:
                    users[user]['Tickets'] += amount
            await message.channel.send(f'{reciever_user} recieved {amount} :tickets: (tickets)')
            with open('crazy_blazin_database.txt', 'w') as f:
                f.write(str(users))




        

        




    


        
        
    
        











        

        # role_names = [role.name for role in message.author.roles]
        # if 'Cheeki Breeki Gold' in role_names:
        #     await message.channel.send('Beeb boob, i change backgrounds!')

        # else:
        #     await message.channel.send('Only users with Cheeki Breeki Gold can use this function.')

            
client.run(k)


# fig, ax = plt.subplots(1, 3)
# ax[0].imshow(input_image_)
# ax[1].imshow(input_image_masked)
# ax[2].imshow(r)
# plt.show()