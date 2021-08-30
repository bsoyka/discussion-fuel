from mongoengine import Document, StringField, connect

from config import get_config

connect(host=get_config('MONGO_HOST'))


class DiscordWebhook(Document):
    url = StringField()


def generate_all_webhooks():
    for webhook in DiscordWebhook.objects:  # pylint: disable=no-member
        yield webhook.url
