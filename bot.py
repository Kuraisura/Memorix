import discord
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_IDS = list(map(int, os.getenv('CHANNEL_IDS').split(',')))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
else:
    data = {}

def save_data():
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f'Received message: {message.content}')

    if message.channel.id in CHANNEL_IDS:
        print(f"Message is from one of the target channels: {message.channel.name} (ID: {message.channel.id})")

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        user_message = f"In channel '{message.channel.name}', {message.author.name} said: \"{message.content}\""

        if message.attachments:
            attachment_url = message.attachments[0].url
            data[current_time] = f"Attachment URL: {attachment_url} - {user_message}"
            save_data()
            print(f'Saved image URL: "{attachment_url}" with date and time: {current_time} to data.json')
        else:
            data[current_time] = user_message
            save_data()
            print(f'Saved message: "{user_message}" with date and time: {current_time} to data.json')

    try:
        if message.content == '!help':
            help_text = (
                "Here are the available commands:\n"
                "`!store <key> <value>` - Store a value with the specified key.\n"
                "`!get <key>` - Retrieve the value associated with the specified key.\n"
                "`!getmsg <message_content>` - Retrieve messages containing the specified content along with the user.\n"
                "`!list` - List all keys in the database.\n"
                "`!delete <key>` - Delete the specified key from the database."
            )
            await message.channel.send(help_text)

        elif message.content.startswith('!store'):
            _, key, value = message.content.split(maxsplit=2)
            data[key] = value
            save_data()
            await message.channel.send(f'Stored `{key}: {value}` in the database.')

        elif message.content.startswith('!get'):
            _, key = message.content.split(maxsplit=1)
            value = data.get(key, "Key not found.")
            await message.channel.send(f'{key}: {value}')

        elif message.content.startswith('!getmsg'):
            _, message_content = message.content.split(maxsplit=1)
            results = [key for key, value in data.items() if message_content in value]
            if results:
                await message.channel.send(f'Messages containing "{message_content}":\n' + "\n".join(results))
            else:
                await message.channel.send(f'No messages found containing "{message_content}".')

        elif message.content == '!list':
            keys = ", ".join(data.keys()) if data else "No keys found."
            await message.channel.send(f'Keys in the database: {keys}')

        elif message.content.startswith('!delete'):
            _, key = message.content.split(maxsplit=1)
            if key in data:
                del data[key]
                save_data()
                await message.channel.send(f'Deleted `{key}` from the database.')
            else:
                await message.channel.send('Key not found.')

    except Exception as e:
        print(f'Error processing message: {e}')

client.run(BOT_TOKEN)
