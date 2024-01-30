
import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI

# Max conversation length before it starts forgetting older messages
CONVERSATION_MAX = 10

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE ELSE
load_dotenv()
TOKEN = os.getenv('TOKEN')
client = AsyncOpenAI(
    api_key=os.getenv('API_KEY'),
)
messages = [{"role":"system", "content":"you are a friendly chatbot keeping up multiple conversations with different users. The username of these users are going to be told to you at the start of each message."}]

# STEP 1: SETUP BOT INTENTS (PERMISSIONS)
bot = commands.Bot(command_prefix='!', intents= discord.Intents.all())

# STEP 3: HANDLING THE STARTUP
@bot.event
async def on_ready() -> None:
    try:
        synced = await bot.tree.sync()
        print(f'{bot.user} is now running with {len(synced)} command(s)!')
    except Exception as e:
        print(e)

# STEP 4: HANDLING INCOMING MESSAGES
@bot.tree.command(name="gpt", description="Call upon ChatGPT")
@app_commands.describe(thing_to_say = "What would you like to say to ChatGPT?")
async def gpt(interaction: discord.Interaction, thing_to_say: str):
    await interaction.response.defer()
    messages.append({
                "role": "user",
                "content": "this is " + interaction.user.name + " who says: " + thing_to_say
            })
    # Forget first user message (0th element is the system message, which we wanna keep)
    if (len(messages) > CONVERSATION_MAX):
        del messages[1]
    chat_completion = await client.chat.completions.create(
        messages=messages
        ,
        model="gpt-3.5-turbo",
    )
    reply = chat_completion.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    await interaction.followup.send(f"{interaction.user.name}: {thing_to_say} \n Response: {reply}")

@bot.tree.command(name="reset", description="Reset ChatGPT conversation")
async def reset(interaction: discord.Interaction):
    global messages
    messages = [{"role":"system", "content":"you are a friendly chatbot keeping up multiple conversations with different users. The username of these users are going to be told to you at the start of each message."}]

bot.run(TOKEN)