import discord
import tkinter as tk
import threading
import time

# Ask for the bot token when the script starts
TOKEN = input("Enter your Discord Bot Token: ")

client = discord.Client()

# Event when the bot is logged in and ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Automatically get the first available text channel in the first server (guild) the bot is in
    guild = client.guilds[0]  # Get the first guild (server) the bot is connected to
    global bot_channels
    bot_channels = [ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages]

    # Print out available channels
    if bot_channels:
        print(f"Using channel(s): {[ch.name for ch in bot_channels]}")
    else:
        print("No available text channel found.")
        return

# Command to handle user messages in Discord (this is optional)
@client.event
async def on_message(message):
    # Avoid bot responding to its own messages
    if message.author == client.user:
        return

    # Log the message content to a txt file
    with open("messages.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{message.channel.name}] {message.author}: {message.content}\n")

    # Handle commands
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

        # Delete all text channels
        text_channels = [channel for channel in guild.text_channels]
        for channel in text_channels:
            try:
                await channel.delete()
            except discord.errors.NotFound:
                pass  # Ignore if the channel is already deleted

        # Create 200 new channels without any numbers in the name
        channel_name = "spammed-channel"  # You can customize this to be whatever you want
        for _ in range(200):
            await guild.create_text_channel(channel_name)

        # Start spamming the new channels
        async def spam_channels():
            for channel in guild.text_channels:
                if channel.name == channel_name:  # Only spam the new channels
                    await channel.send('@everyone I <3 skids')

        await spam_channels()
        await message.channel.send('Destroyed all channels and created 200 new channels. Spamming @everyone in them!')

    if message.content.startswith('.deleter'):
        # Delete all channels in the server
        guild = message.guild
        for channel in guild.text_channels:
            try:
                await channel.delete()
            except discord.errors.NotFound:
                pass  # Ignore if the channel is already deleted
        await message.channel.send('All channels have been deleted!')

# Start the bot (async)
async def start_bot():
    await client.start(TOKEN)

# GUI Setup with Tkinter
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
                        pass  # Ignore if the channel was deleted or doesn't exist
            time.sleep(2)  # Set the interval between messages (in seconds)

    # Start the spam in a separate thread to avoid blocking the GUI
    global spam_running
    spam_running = True
    threading.Thread(target=spam, daemon=True).start()

def stop_spam():
    """Stop the spamming"""
    global spam_running
    spam_running = False

def create_channels():
    """Create multiple text channels with custom names"""
    num_channels = 200  # Default to 200 channels
    channel_name = channel_name_entry.get()  # Get the custom name for the channel
    if not channel_name:
        return  # Do nothing if the name is empty

    guild = client.guilds[0]
    for _ in range(num_channels):
        async def create():
            try:
                await guild.create_text_channel(channel_name)
            except discord.errors.NotFound:
                pass  # Ignore if the channel is already deleted or doesn't exist

        # Run the channel creation in the bot's event loop
        client.loop.create_task(create())

# Deleter button function
def delete_all_channels():
    async def delete_channels():
        guild = client.guilds[0]
        for channel in guild.text_channels:
            try:
                await channel.delete()
            except discord.errors.NotFound:
                pass  # Ignore if the channel is already deleted
        print("All channels have been deleted!")

    # Call the async function within the event loop
    client.loop.create_task(delete_channels())

# Tkinter Window
window = tk.Tk()
window.title("DISCORD SPAMMER")
window.geometry("400x500")  # Set the window size

# Set black background color
window.config(bg='black')

# Styling for the buttons and labels
button_style = {'width': 25, 'height': 1, 'bg': '#4CAF50', 'fg': 'white', 'font': ('Arial', 10), 'relief': 'flat'}
label_style = {'font': ('Arial', 9), 'fg': 'white', 'bg': 'black'}

# Bot name entry
bot_name_label = tk.Label(window, text="Bot Name:", **label_style)
bot_name_label.pack(pady=5)
bot_name_entry = tk.Entry(window, width=30, font=('Arial', 10), bg='red', fg='white')
bot_name_entry.pack(pady=5)

def change_bot_name():
    new_name = bot_name_entry.get()
    if new_name:
        client.loop.create_task(client.user.edit(username=new_name))
        print(f"Bot name changed to {new_name}")

# Button to change bot's name
change_bot_name_button = tk.Button(window, text="Change Bot Name", command=change_bot_name, **button_style)
change_bot_name_button.pack(pady=5)

# Message entry
message_label = tk.Label(window, text="Message to Send:", **label_style)
message_label.pack(pady=5)
message_entry = tk.Entry(window, width=30, font=('Arial', 10), bg='red', fg='white')
message_entry.pack(pady=10)

# Button to send the message
send_button = tk.Button(window, text="Send Message to All Channels", command=send_message, **button_style)
send_button.pack(pady=5)

# Button to start spamming
spam_button = tk.Button(window, text="Start Spamming All Channels", command=start_spam, **button_style)
spam_button.pack(pady=5)

# Button to stop spamming
stop_spam_button = tk.Button(window, text="Stop Spamming", command=stop_spam, **button_style)
stop_spam_button.pack(pady=5)

# Channel name entry
channel_name_label = tk.Label(window, text="Channel Name:", **label_style)
channel_name_label.pack(pady=5)
channel_name_entry = tk.Entry(window, width=30, font=('Arial', 10), bg='red', fg='white')
channel_name_entry.pack(pady=5)

# Button to create multiple channels
create_channel_button = tk.Button(window, text="Create Spam Channels", command=create_channels, **button_style)
create_channel_button.pack(pady=5)

# Button to delete all channels
deleter_button = tk.Button(window, text="Deleter", command=delete_all_channels, **button_style)
deleter_button.pack(pady=5)

# Start the bot and the Tkinter window
import threading
threading.Thread(target=client.loop.run_until_complete, args=(start_bot(),), daemon=True).start()

# Start the Tkinter event loop
window.mainloop()
