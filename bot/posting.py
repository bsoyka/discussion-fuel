from os import remove
from sys import exit

from aiohttp import ClientSession
from discord import AsyncWebhookAdapter, File, Webhook
from loguru import logger
from praw import Reddit
from requests import get, post
from tweepy import API as TwitterAPI
from tweepy import OAuthHandler as TwitterOAuthHandler

from config import get_config
from database import generate_all_webhooks


def post_to_band(text: str) -> None:
    """Posts the topic to BAND"""

    url = 'https://openapi.band.us/v2.2/band/post/create'

    payload = {
        'access_token': get_config('BAND_ACCESS_TOKEN'),
        'band_key': get_config('BAND_KEY'),
        'content': text,
        'do_push': True,
    }

    response = post(url, data=payload)

    response.raise_for_status()
    logger.debug('Post successful')


def post_to_reddit(text: str) -> None:
    """Posts the topic to Reddit"""

    reddit = Reddit(
        client_id=get_config('REDDIT_CLIENT_ID'),
        client_secret=get_config('REDDIT_CLIENT_SECRET'),
        user_agent=get_config('REDDIT_USER_AGENT'),
        username=get_config('REDDIT_USERNAME'),
        password=get_config('REDDIT_PASSWORD'),
    )
    logger.debug('Authenticated')
    reddit.validate_on_submit = True

    subreddit = reddit.subreddit(get_config('REDDIT_SUBREDDIT'))
    logger.debug('Subreddit retrieved')

    submission = subreddit.submit(title=text, selftext='')
    logger.debug(f'Post successful at {submission.url}')

    submission.clear_vote()
    logger.debug('Cleared vote')
    submission.mod.approve()
    logger.debug('Post approved')
    submission.mod.distinguish(how='yes')
    logger.debug('Distinguished')
    submission.mod.ignore_reports()
    logger.debug('Ignored reports')
    submission.mod.set_original_content()
    logger.debug('Set as original content')
    submission.mod.update_crowd_control_level(1)
    logger.debug('Updated crowd control level')


def post_to_twitter(text: str) -> None:
    """Posts the topic to Twitter"""

    auth = TwitterOAuthHandler(
        get_config('TWITTER_API_KEY'), get_config('TWITTER_API_SECRET')
    )
    auth.set_access_token(
        get_config('TWITTER_ACCESS_TOKEN'),
        get_config('TWITTER_ACCESS_TOKEN_SECRET'),
    )
    api = TwitterAPI(auth)
    logger.debug('Authenticated')

    api.update_with_media('temp.png', status=f'{text} #DiscussionFuel')
    logger.debug('Post successful')


async def post_to_discord(text: str) -> None:
    """Posts the topic to Discord"""

    webhook_urls = generate_all_webhooks()

    async with ClientSession() as session:
        for url in webhook_urls:
            webhook: Webhook = Webhook.from_url(
                url, adapter=AsyncWebhookAdapter(session)
            )

            image_file = File('temp.png', 'image.png')

            await webhook.send(
                f'{text} #DiscussionFuel',
                username=get_config('DISCORD_USERNAME'),
                # avatar_url=get_config('DISCORD_AVATAR_URL'),
                file=image_file,
            )
            logger.debug(f'Post successful at {url}')


async def post_to_all_locations(text: str, image_url: str) -> None:
    """Posts the topic to all locations"""

    request = get(image_url, stream=True)

    if request.ok:
        with open('temp.png', 'wb') as image:
            for chunk in request:
                image.write(chunk)

        logger.debug('Image downloaded')
    else:
        logger.critical('Unable to download image')
        exit()

    post_to_band(text)
    post_to_reddit(text)
    post_to_twitter(text)
    await post_to_discord(text)

    remove('temp.png')
    logger.debug('Removed temporary file')
