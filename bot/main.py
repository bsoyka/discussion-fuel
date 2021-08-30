from sys import exc_info

from discord.ext import commands
from dislash import Option, SlashClient, Type, is_owner
from loguru import logger

from config import get_config
from database import DiscordWebhook, generate_all_webhooks
from posting import post_to_all_locations

bot = commands.Bot(command_prefix='!')
slash = SlashClient(bot)

guilds = [int(get_config('DISCORD_GUILD_ID'))]


@bot.event
async def on_connect():
    logger.debug('Connected')


@bot.event
async def on_ready():
    logger.info(f"Ready as '{bot.user}'")


@bot.event
async def on_disconnect():
    logger.warning('Disconnected')


@bot.event
async def on_resumed():
    logger.info('Resumed session')


@bot.event
async def on_error(event, *args, **kwargs):
    logger.opt(exception=exc_info()[0]).error(f'{event} caused an error')


@is_owner()
@slash.command(
    name='addwebhook',
    description='Adds a webhook to the distribution database',
    guild_ids=guilds,
    options=[
        Option(
            'url',
            'The webhook URL, as provided by Discord',
            Type.STRING,
            required=True,
        )
    ],
)
async def add_webhook(ctx, url: str):
    logger.debug(f'/addwebhook called with url {url}')

    DiscordWebhook(url=url).save()
    logger.info(f'Saved webhook to database with url {url}')

    await ctx.send('Webhook saved!', ephemeral=True)


@is_owner()
@slash.command(
    name='listwebhooks',
    description='Lists all webhooks in the database',
    guild_ids=guilds,
)
async def list_webhooks(ctx):
    logger.debug('/listwebhooks called')

    webhooks = '\n'.join(generate_all_webhooks())
    await ctx.send(f'```\n{webhooks}\n```', ephemeral=True)


@is_owner()
@slash.command(
    name='removewebhook',
    description='Removes a webhook from the distribution database',
    guild_ids=guilds,
    options=[
        Option(
            'url',
            'The webhook URL, as provided by Discord',
            Type.STRING,
            required=True,
        )
    ],
)
async def remove_webhook(ctx, url: str):
    logger.debug(f'/removewebhook called with url {url}')

    DiscordWebhook.objects(url=url).delete()  # pylint: disable=no-member
    logger.info(f'Removed webhook from database with {url}')

    await ctx.send('Webhook removed!', ephemeral=True)


@is_owner()
@slash.command(
    name='post',
    description='Posts a message to all locations',
    guild_ids=guilds,
    options=[
        Option(
            'text',
            'The message to be posted',
            Type.STRING,
            required=True,
        ),
        Option(
            'image_url',
            'The image URL to be posted',
            Type.STRING,
            required=True,
        ),
    ],
)
async def post_everywhere(ctx, text: str, image_url: str):
    msg = await ctx.send(type=5, ephemeral=True)

    logger.debug(f'/post called with text {text} and image_url {image_url}')

    await post_to_all_locations(text, image_url)
    logger.info(f'Posted to all locations with {text}')

    await ctx.send('Posted to all locations!', ephemeral=True)


bot.run(get_config('DISCORD_BOT_TOKEN'))
