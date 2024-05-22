import discord
from controller import controller
from discord.ext import commands

# load token in a better way, such as from a file
token = ''

description = 'Ame discord interface.'
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.dm_messages = True  # Enable direct message intents

activity = discord.Streaming(name="tears of the sky", url="https://twitch.tv/expl0dingc")

bot = commands.Bot(command_prefix='!', description=description, intents=intents, activity=activity)
ai = controller()

@bot.event
async def on_ready():
    print('Ame discord interface has been initialized and connected. Ready to process messages.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if message is from a guild or a DM
    if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel):
        async with message.channel.typing():
            input_message = message.content.replace(f"<@{bot.user.id}>", "Ame").strip()
            input, output, aud = ai.text_pipeline(input_message)

        response_embed = discord.Embed(title="", description=output, color=0x242768)
        response_embed.set_footer(text='Powered by Ame')
        await message.reply(embed=response_embed, mention_author=False)
    else:  # Message is from a guild
        # Process user mentions
        if bot.user.mentioned_in(message):
            async with message.channel.typing():
                input_message = message.content.replace(f"<@{bot.user.id}>", "Ame").strip()
                input, output, aud = ai.text_pipeline(input_message)

            response_embed = discord.Embed(title="", description=output, color=0x242768)
            response_embed.set_footer(text='Powered by Ame')
            await message.reply(embed=response_embed, mention_author=False)

bot.run(token)
