# bot.py
import os
import discord
from dotenv import load_dotenv
import os
from pathlib import Path
import tweepy
import pytz
import asyncio
from discord_webhooks import DiscordWebhooks

from twitterauth import *

# @ninjabq, @realDonaldTrump, @ElonMusk, @EarningsWhisper respectively
twitter_ids = ['30705837','25073877','44196397','136136326']

twitter_webhooks = \
{
    '30705837' : 'https://discordapp.com/api/webhooks/718482601052209263/CW8nrN2Qj08cnvwT4yts57jjFJuYTlgDj-Rp78HZAZdvkjJ45tcKWcf3UGvOBbfRTaly', # ninjabq
    '25073877' : 'https://discordapp.com/api/webhooks/716437481565847572/LnLTB2tC77nwh6ijYTOaMLwLoefTW7d_cjDGb-ugjMw9Y8YKXLTU0KjgTQ_Ylf-8lrCh', # Trump
    '44196397' : 'https://discordapp.com/api/webhooks/716437758666735666/gpRQUETtCcJW65etUMFaI_7F_oqz7HKb8TXN_3VSK1wrN3ZFiaUValRfVpuw6w1Ivtbg', # Elon
    '136136326': 'https://discordapp.com/api/webhooks/731672042729898086/SvpHs7gZ26Z2wKYZsQ1Vu07v-EhnATrfDbFXWESaR70MhvSrxiZdeh65fMNeNvCdQP81', # EarningsWhisper
}

role_mentions = \
{
    '30705837' : '<@&716321644121030666>', # ninjabq
    '25073877' : '<@&716776396281741432>', # Trump
    '44196397' : '<@&716776688167682048>', # Elon
    '44196397' : '', # EarningsWhisper
}

client = discord.Client()

'''
Twitter-related Functions
'''
class StreamListener(tweepy.StreamListener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_status(self, status):
        if status.author.id_str in twitter_ids:
            # Get the time
            time_format = "%Y-%m-%d %H:%M:%S"
            timestamp_utc = status.created_at.replace(tzinfo=pytz.utc)
            timestamp_est = timestamp_utc.astimezone(pytz.timezone('America/New_York'))
            timestamp_str = timestamp_est.strftime(time_format)

            tweet_url = f'https://twitter.com/{status.author.screen_name}/status/{status.id}'

            message = f'{role_mentions[status.author.id_str]} New tweet from @{status.author.screen_name} at {timestamp_str}\n{tweet_url}'

            webhook = DiscordWebhooks(twitter_webhooks[status.author.id_str])
            webhook.set_content(content=message, url=tweet_url, color=0x00acee, description=status.text)
            webhook.set_author(name=f'{status.author.name} (@{status.author.screen_name})', url=f'https://twitter.com/{status.author.screen_name}', icon_url=status.author.profile_image_url)
            webhook.set_footer(text="Twitter", icon_url="https://cdn1.iconfinder.com/data/icons/iconza-circle-social/64/697029-twitter-512.png")
            webhook.send()

    def on_error(self, status_code):
        if status_code == 420:
            return False

'''
Main functions for responding to events
'''
@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    start_twitter_stream()

@client.event
async def on_message(message):
    # Ignore bot commands
    if message.author == client.user:
        return

def start_twitter_stream():
    print("starting twitter things")
    #load twitter stream
    auth = tweepy.OAuthHandler(TWITTERCONSUMERKEY, TWITTERCONSUMERSECRET)
    auth.set_access_token(TWITTERACCESSTOKEN, TWITTERACCESSTOKENSECRET)
    api = tweepy.API(auth)

    stream_listener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(follow=twitter_ids, is_async=True)

if __name__ == "__main__":
    print("starting discord bot")
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    client.run(TOKEN)