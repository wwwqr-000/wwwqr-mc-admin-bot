import discord, time, subprocess
from discord.ext import commands
from mcrcon import MCRcon

def bash(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr

host = "127.0.0.1"
port = 25575
password = "RCON_PASSWORD"

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if (channel.permissions_for(guild.me).send_messages):
                await channel.send("Bot online!")
                break

@bot.command()
async def refreshtunnel(ctx):
    bash("sudo systemctl restart mc-tunnel")
    await ctx.send(f"Refreshing tunnel...")

@bot.command()
async def startserver(ctx):
    bash("sudo systemctl start better-mc-daemon")
    await ctx.send(f"Starting server...")

@bot.command()
async def stopserver(ctx):
    bash("sudo systemctl stop better-mc-daemon")
    await ctx.send(f"Stopping server...")

@bot.command()
async def restartserver(ctx):
    bash("sudo systemctl restart better-mc-daemon")
    await ctx.send(f"Restarting server...")

@bot.command()
async def c(ctx, *, cmd):
    with MCRcon(host, password, port) as mcr:
        resp = mcr.command(cmd)
        await ctx.send(resp) 

bot.run("BOT_TOKEN")