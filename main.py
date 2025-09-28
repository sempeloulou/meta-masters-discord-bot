import discord
from discord.ext import commands
import requests
import json
import os

# 🔧 Configuration sécurisée
TOKEN = os.getenv('DISCORD_TOKEN')  # Token via variable d'environnement
GUILD_ID = 1421669500109066375
VIP_COUNTERS_CHANNEL = 1421670499955642459
VIP_MONTHLY_ROLE = 1421670147709468762
VIP_LIFETIME_ROLE = 1421735904401297489

# 🎮 Base de données des counters
COUNTERS = {
    'bonnie': 'Charlie, Gus, Piper, Belle, Eve, Tick',
    'ollie': 'Poco, Stu, Corde, Frank, Buster',
    'corde': 'Sandy, Jae, Stu, Ruff, Hank',
    'kit': 'Corde, Bull, RT, Frank, Buster',
    'kaze': 'Corde, Amber, Crow, Gene',
    'lumi': 'Kit, Lily, Barley, Willow, Belle, Squeak',
    'byron': 'Kit, Lily, Bonnie, Ollie, Piper',
    'jae': 'Crow, Kenji, Belle',
    'charlie': 'Amber, Willow, Squeak, Carl, Jae',
    'lily': 'Jackie, Frank, Buster, Doug',
    'gus': 'Byron, Gray, Gene, Darryl, Jae',
    'carl': 'Darryl, Jae, Buzz, Buster, Crow, Stu',
    'amber': 'Crow, Bea, Belle, Byron, Throwers',
    'hank': 'Kenji, Lou, Bea, Dyna, Ash',
    'kenji': 'Crow, Corde, Tara, Frank, Otis, Stu, Jackie, Ash',
    'ruff': 'Squeak, Carl, Throwers',
    'draco': 'Frank, Bea, Lou, Willow, Lumi',
    'crow': 'Ruff, Gus, Spike, Belle, Charlie',
    'grey': 'Charlie, Tara, Mr P, Gus',
    'gray': 'Charlie, Tara, Mr P, Gus',
    'belle': 'Angelo, Piper, Throwers',
    'tara': 'Sandy, Buster, Jae, Squeak, Amber',
    'gene': 'Mr P, Charlie, Belle, Throwers',
    'buster': 'Brock, Squeak, Ash, Willow, Barley, Darryl',
    'ash': 'Frank, Otis, Willow',
    'otis': 'Squeak, Byron, Belle, Throwers',
    'shade': 'Griff, Frank, Jackie, Hank, Stu',
    'mr p': 'Charlie, Tara, Gray, Gus',
    'rt': 'Kit, Lily, Bonnie, Ollie, Piper'
}

# 🤖 Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 🔍 Recherche intelligente de brawler
def find_brawler(query):
    query = query.lower().strip()
    
    # Recherche exacte
    if query in COUNTERS:
        return query
    
    # Recherche qui commence par
    for brawler in COUNTERS:
        if brawler.startswith(query) or query.startswith(brawler):
            return brawler
    
    # Recherche qui contient
    for brawler in COUNTERS:
        if query in brawler or brawler in query:
            return brawler
    
    return None

# 🔐 Vérifier si l'utilisateur a le rôle VIP
def is_vip(member):
    vip_roles = {VIP_MONTHLY_ROLE, VIP_LIFETIME_ROLE}
    member_roles = {role.id for role in member.roles}
    return bool(vip_roles & member_roles)

# 🚀 Bot prêt
@bot.event
async def on_ready():
    print(f'✅ {bot.user} est connecté!')
    print(f'🎮 {len(COUNTERS)} brawlers chargés')
    print('⚡ Prêt à répondre aux counters!')

# 📝 Gestion des messages
@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author.bot:
        return
    
    # Seulement dans le channel VIP counters
    if message.channel.id != VIP_COUNTERS_CHANNEL:
        return
    
    # Vérifier le rôle VIP
    if not is_vip(message.author):
        reply = await message.reply('🔒 **VIP Access Required** - Upgrade in 💎-vip-upgrade!')
        # Supprimer après 5 secondes
        await reply.delete(delay=5)
        await message.delete(delay=5)
        return
    
    content = message.content.strip()
    
    # Commande help
    if content.lower() == '!help':
        embed = discord.Embed(
            title="🎮 Meta Masters Counters",
            description="**How to use:**",
            color=0x00ff00
        )
        embed.add_field(name="🎯 Get Counters", value="Type any brawler name", inline=False)
        embed.add_field(name="📋 !list", value="Show all available brawlers", inline=True)
        embed.add_field(name="❓ !help", value="Show this help", inline=True)
        embed.set_footer(text="Meta Masters VIP")
        
        await message.reply(embed=embed)
        return
    
    # Commande list
    if content.lower() == '!list':
        brawlers = [brawler.capitalize() for brawler in COUNTERS.keys() if ' ' not in brawler]
        brawlers.sort()
        
        # Diviser en chunks pour éviter les messages trop longs
        chunk_size = 20
        chunks = [brawlers[i:i + chunk_size] for i in range(0, len(brawlers), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"📋 Available Brawlers {i+1}/{len(chunks)}",
                description=", ".join(chunk),
                color=0x0099ff
            )
            await message.reply(embed=embed)
        return
    
    # Recherche de counter
    brawler = find_brawler(content)
    
    if brawler:
        counters = COUNTERS[brawler]
        name = brawler.capitalize()
        
        embed = discord.Embed(
            title=f"🎯 {name} Counters",
            description=f"**{counters}**",
            color=0xffd700
        )
        embed.set_footer(text="Meta Masters VIP • Season XX")
        
        await message.reply(embed=embed)
        print(f"⚡ Counter envoyé: {name} pour {message.author.name}")
    
    else:
        # Brawler non trouvé
        embed = discord.Embed(
            title="❌ Brawler Not Found",
            description=f'"{content}" is not in our database.\n\nTry `!list` to see all available brawlers.',
            color=0xff0000
        )
        
        reply = await message.reply(embed=embed)
        await reply.delete(delay=8)

# 🧪 Commande de test (pour les admins)
@bot.command(name='test')
async def test_command(ctx):
    """Commande de test pour vérifier que le bot fonctionne"""
    if ctx.channel.id == VIP_COUNTERS_CHANNEL:
        embed = discord.Embed(
            title="🧪 Test du Bot",
            description="Le bot fonctionne parfaitement!",
            color=0x00ff00
        )
        embed.add_field(name="📊 Stats", value=f"{len(COUNTERS)} brawlers chargés", inline=True)
        embed.add_field(name="⚡ Status", value="Online et opérationnel", inline=True)
        
        await ctx.reply(embed=embed)

# 🛡️ Gestion des erreurs
@bot.event
async def on_error(event, *args, **kwargs):
    print(f'❌ Erreur dans {event}')

# 🚀 Démarrage du bot
if __name__ == "__main__":
    print("🐍 Démarrage du bot Python...")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Token Discord manquant! Ajoutez la variable d'environnement DISCORD_TOKEN")
