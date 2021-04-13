
import os
import matplotlib.pyplot as plt
import numpy as np
import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import time
import threading
from discord.utils import get

client = commands.Bot(command_prefix='!')

#https://discordapp.com/developers



class EventHandler:
    def __init__(self):
        self.events = []
        self.coin_aggregation_members = {}
    
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

        with open('crazy_blazin_database.txt', 'r') as f:
            users = eval(f.read())
            
        for member in self.coin_aggregation_members:
            state = self.coin_aggregation_members[member]
            channel_state = str(state.channel)
            stream_state = state.self_stream

            if member not in users:
                users[member] = {'Coins': 25, 'Tickets': 50}
                with open('crazy_blazin_database.txt', 'w') as f:
                    f.write(str(users))

                with open('crazy_blazin_database.txt', 'r') as f:
                    users = eval(f.read())

            if channel_state != 'None':
                if stream_state:
                    users[member]['Coins'] += 15
                    print(f'Stream activity: {member}')
                else:
                    users[member]['Coins'] += 5

                print(f'Coins to : {member}')

        with open('crazy_blazin_database.txt', 'w') as f:
            f.write(str(users))



events_handler = EventHandler()


def add_coins_after_time():
    try:
        events_handler.coin_aggregation()
        print('Coins distributed!')
        time.sleep(900)
        add_coins_after_time()
    except KeyboardInterrupt:
        exit()


thread_timer = threading.Thread(target = add_coins_after_time)
thread_timer.start()


class Ticket:
    def __init__(self, price, description, id, creator):
        self.price = price
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

    if message.author.name not in users:
        users[message.author.name] = {'Coins': 25, 'Tickets': 1}
        with open('crazy_blazin_database.txt', 'w') as f:
            f.write(str(users))

    if message.content.startswith('!bal'):
        value = users[message.author.name]['Coins']
        ticket = users[message.author.name]['Tickets']
        await message.channel.send(f'{message.author.name} \n {value} <:CBCcoin:831506214659293214> (CBC) \n {ticket} :tickets: (tickets)')


    if message.content.startswith('!raffle'):
        str_split = message.content.split(' ')
        if len(str_split) < 2:
            await message.channel.send(f'Few arguments. Use !raffle price description')
        try:
            price = int(str_split[1])
        except ValueError:
            await message.channel.send(f'Price needs to be integer!')
        description = ''
        for idx in range(2, len(str_split)):
            description += str_split[idx] + ' '

        role_names = [role.name for role in message.author.roles]
        if 'Crazy Blazin Gold' in role_names or 'Admin' in role_names:
            ticket = Ticket(price, description, len(events_handler.events)+1, message.author.name)
            events_handler.add_event(ticket)
            await message.channel.send(f'Raffle startet! [ID {ticket.id}]')
            await message.channel.send(f'Description:')
            await message.channel.send(f'{description}')
            await message.channel.send(f'Tickets needed to join raffle: {price} :tickets: ')
            await message.channel.send(f'To join raffle use !join raffleID ')
        else:
            await message.channel.send(f'You have to be admin or have Crazy Blazin Gold account to start raffles!')

    
    if message.content.startswith('!events'):
        with open('crazy_blazin_database.txt', 'r') as f:
            users = eval(f.read())
        for i, event in enumerate(events_handler.events):
            await message.channel.send(f'EventID: {i+1}, Price: {event.price} :tickets:,  Description: {event.description}')
        if len(events_handler.events) < 1:
            await message.channel.send(f'No events active.')
    
    if message.content.startswith('!join'):
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) < 1:
            await message.channel.send(f'Too many or few arguments. Use !join ID')
        try:
            id = int(str_split[1])
        except ValueError:
            await message.channel.send(f'ID needs to be integer!')
        
        EVENT_FOUND = True
        for event in events_handler.events:
            if event.id == id:
                EVENT_FOUND = False
                if event.price < users[message.author.name]['Tickets']:
                    if message.author.name in event.participants:
                        await message.channel.send(f'{message.author.name} already participate in the raffle!')
                    else:
                        users[message.author.name]['Tickets'] -= event.price
                        with open('crazy_blazin_database.txt', 'w') as f:
                            f.write(str(users))
                        event.participants.append(message.author.name)
                        await message.channel.send(f'{message.author.name} joined the raffle!')
                    
        if EVENT_FOUND:
            await message.channel.send(f'This event does not exist!')


    if message.content.startswith('!startraffle'):
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) < 1:
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
            await message.channel.send(f'{message.author.name} does not have enough <:CBCcoin:831506214659293214> (CBC) to buy {amount} tickets!')
            await message.channel.send(f'Price: <:CBCcoin:831506214659293214> (CBC) per :tickets: .')


    if message.content.startswith('!buy CBCGold'):
        str_split = message.content.split(' ')
        if len(str_split) > 2 or len(str_split) < 1:
            await message.channel.send(f'Too many or few arguments. Use !buy CBCGold')

        if 500 <= users[message.author.name]['Coins']:
            users[message.author.name]['Coins'] -= 500

            member = message.author
            role = get(member.guild.roles, name='Crazy Blazin Gold')
            await member.add_roles(role)
            with open('crazy_blazin_database.txt', 'w') as f:
                f.write(str(users))
            await message.channel.send(f'{message.author.name} Bought Crazy Blazin Gold Role!')
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