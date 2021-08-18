from os import getenv

from mongoengine import Document, StringField, connect

connect(host=getenv('MONGO_HOST'))


class DiscordWebhook(Document):
    url = StringField()


def generate_all_webhooks():
    for webhook in DiscordWebhook.objects:  # pylint: disable=no-member
        yield webhook.url
