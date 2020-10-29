# bot.py
import os
import sys
import discord
import requests as r
import raiderio

from discord.ext import commands

## CONFIG RELATED CONSTS
TOKEN = os.getenv('DISCORD_TOKEN')
RAIDERIO_URL = "https://raider.io/api/v1"
NO_DUNGEONS_CS = 11
FIFTTEEN_TIMED = 161


# TODO: break out into multi-class for character return info etc
class RecruitDecision:
    """Class responsable for performing recruitment type decisions."""
    def __init__(self, role, apirsp):
        self.role = role
        self.body = apirsp
        self.rolescore = self.body['mythic_plus_scores_by_season'][0]['scores'][self.role]
        self.onehundredp = NO_DUNGEONS_CS * FIFTTEEN_TIMED
        self.sixtysixp = round(((NO_DUNGEONS_CS * 2) / 3) * FIFTTEEN_TIMED)
        self.recruitanswer = self.getdecision()

    def __str__(self):
        return "Recruit Decision Object..."

    def getdecision(self):
        decision = "Unknown..."
        if self.rolescore >= self.onehundredp:
            decision = "Recruit! Very Good - 15+ on all dungeons likely."
        elif self.rolescore >= self.sixtysixp:
            decision = "Check ilvl and gain more info - Average - in 66p for this season assuming 15+ 2/3 keys."
        elif self.rolescore < self.sixtysixp:
            decision = "No - Below Average - below 66p for this season and likely needs work."
        return decision

    def readymsg(self):
        """Make message to discord look ok"""
        prsp = (
            f"CharName: {self.body['name']}\n",
            f"ilvl: {self.body['gear']['item_level_equipped']}\n",
            f"profilepicthumb: {self.body['thumbnail_url']}\n",
            f"Role Score (current season): {self.rolescore}\n",
            f"Recruit(?): {self.recruitanswer}"
        )
        return prsp


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    io_api_conn = r.get(RAIDERIO_URL)
    if io_api_conn.status_code == 200:
        print(f'{bot.user.name} has established connection to raider.io...')
    else:
        print(f'{bot.user.name} could not establish connection to raider.io...exiting')
        sys.exit(1) 

@bot.command(name='recruit',
             help='Provides rudimentary recommendation engine for recruitment purposes.',
             usage='[PlayerName] [Role] [Region] [Realm]')
async def recruit(ctx, player: str, role: str, region: str, realm: str):
    sr = raiderio.resource("characters")
    s_params = {'player': player,
                'role': role,
                'region': region,
                'realm': realm}
    stat_code, grsp =  sr.get_char(**s_params)
    if stat_code == 200:
        rsp = grsp
    elif stat_code == 400:
        rsp = "Character Not Found..."
    else:
        rsp = "Unknown Error..."
    descision = RecruitDecision(role, rsp)
    await ctx.send(descision.readymsg())

bot.run(TOKEN)