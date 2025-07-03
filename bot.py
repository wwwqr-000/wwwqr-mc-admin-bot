import discord, time, subprocess, textwrap#pip install discord
from discord import app_commands
from discord.ext import commands
from mcrcon import MCRcon#pip install mcrcon
from mcstatus.server import JavaServer# pip install mcstatus
from decouple import config #pip install python-decouple

rconHost = config("RCON_HOST")
mcHostPublicIP = config("MC_HOST_PUBLIC")
rconPort = config("RCON_PORT", cast=int)
mcPort = config("MC_PORT", cast=int)
rconPassword = config("RCON_PASSWORD")
tunnelService = config("TUNNEL_SERVICE")
mcServerService = config("MC_SERVER_SERVICE")
mcServerWorldFolder = config("MC_SERVER_WORLD_FOLDER")
localDiscordTestingServerID = config("DISCORD_DEVELOPER_SERVER_ID", cast=int)
discordBotToken = config("DISCORD_BOT_TOKEN")

guildID = discord.Object(id=localDiscordTestingServerID)
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

def bash(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr

def rcon(cmd):
    with MCRcon(rconHost, rconPassword, rconPort) as mcr:
        return mcr.command(cmd)
    
def getServerInfo():
    try:
        server = JavaServer(mcHostPublicIP, mcPort)
        stat = server.status()
        return stat
    
    except Exception as e: 
        return False
    
def serverIsOnline():
    if (not getServerInfo()): return False
    return True
    

class Bot(commands.Bot):
    async def on_ready(self):
        try:
            synced = await self.tree.sync(guild=guildID)
            print(f"Synced {len(synced)} commands seen development server")
        
        except Exception as e:
            print(f"Error syncing: {e}")
            
        print(f"Bot is user '{self.user}'")
        
    async def on_message(self, message):
        if (message.author == self.user): return
        if (message.content.startswith("hello")):
            await message.channel.send(f"Hi there, {message.author}")
            
    async def on_reaction_add(self, reaction, user):
        await reaction.message.channel.send(f"You reacted")

bot = Bot(command_prefix="!", intents=intents)
    
@bot.tree.command(name="refresh-tunnel", description="Refresh the tunnel", guild=guildID)
async def refreshTunnel(interaction: discord.Interaction):
    bash(f"sudo systemctl restart {tunnelService}")
    await interaction.response.send_message("Refreshing tunnel...")
    
@bot.tree.command(name="start-server", description="Start the minecraft server", guild=guildID)
async def startServer(interaction: discord.Interaction):
    if (serverIsOnline()):
        await interaction.response.send_message("Server already started.")
        return
        
    bash(f"sudo systemctl start {mcServerService}")
    await interaction.response.send_message("Starting server...")
    
@bot.tree.command(name="stop-server", description="Stop the minecraft server", guild=guildID)
async def stopServer(interaction: discord.Interaction):
    if (not serverIsOnline()):
        await interaction.response.send_message("Server already stopped.")
        return
        
    bash(f"sudo systemctl stop {mcServerService}")
    await interaction.response.send_message("Server stopped.")
    
@bot.tree.command(name="restart-server", description="Restart the minecraft server", guild=guildID)
async def restartServer(interaction: discord.Interaction):
    bash(f"sudo systemctl restart {mcServerService}")
    await interaction.response.send_message("Restarting server...")
    
@bot.tree.command(name="delete-world", description="Delete the world folder", guild=guildID)
async def deleteWorld(interaction: discord.Interaction):
    if (serverIsOnline()):
        await interaction.response.send_message("Can not delete world while server is active.")
        return
        
    bash(f"sudo rm -R {mcServerWorldFolder}")
    await interaction.response.send_message("World deleted.")
    
@bot.tree.command(name="cmd", description="Execute a command in the mc server", guild=guildID)
async def cmd(interaction: discord.Interaction, cmd: str):
    if (not serverIsOnline()):
        await interaction.response.send_message("Can not send command, server not active.")
        return
        
    resp = rcon(cmd)
    if (resp == ""): resp = "Bot: empty response, did execute."
    await interaction.response.send_message(resp)
    
@bot.tree.command(name="server-stat", description="Check if the server is online", guild=guildID)
async def cmd(interaction: discord.Interaction):
    resp = ""
    stat = getServerInfo()
    if (not stat): resp = "Server is offline 🔴"
    else:
        motd = "MOTD: ".join(str(part) for part in stat.motd.parsed)
        motd = motd.replace("MOTD: Formatting.RESET", "")
        resp = textwrap.dedent(f"""
        Server is online 🟢
        Latency: {round(stat.latency)}ms
        Players online: {stat.players.online}/{stat.players.max}
        MOTD: {motd}
        """)
    
        
    await interaction.response.send_message(resp)

bot.run(discordBotToken)