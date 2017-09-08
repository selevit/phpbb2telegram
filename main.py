"""
Topic monitor for PHPBB 3 forum.

Listen new messages from phpbb forum and sends
They to the telegram channel.
Used for getting updates about a free Visa slots in Russian Embossy.
"""
import logging
import os
import re
import time

import lxml.html
import requests
import telegram
from html2text import html2text

BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
PHPBB_URL = os.environ['TOPIC_URL']
UPDATE_TIMEOUT = int(os.environ.get('UPDATE_TIMEOUT', '5'))

ID_REGEX = re.compile('^pc(\d+)$')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LAST_MESSAGE_ID_FILE = os.path.join(BASE_DIR, 'var/last_message_id')
DEBUG = bool(os.environ.get('DEBUG', '0'))


logger = logging.getLogger(__file__)


class Message:

    def __init__(self, id, text):
        self.id = id
        self.text = text

    def __repr__(self):
        return 'Message(id={}, text="{}")'.format(self.id, self.text)


def extract_text(html):
    return html2text(html.decode('utf-8')).strip()


def notify_telegram(text):
    bot = telegram.Bot(token=BOT_TOKEN)
    if not DEBUG:
        bot.send_message(chat_id=CHANNEL_ID, text=text)
    logger.warn(text)


def parse_messages(page_html):
    doc = lxml.html.document_fromstring(page_html)
    elements = doc.xpath("//div[@class='content']")
    messages = []
    for el in elements:
        match = ID_REGEX.match(el.attrib.get('id', ''))
        if not match:
            continue
        numeric_id = int(match.group(1))
        innerHTML = lxml.html.tostring(el)
        message = Message(numeric_id, extract_text(innerHTML))
        messages.append(message)
    return messages


class TopicMonitor:

    def __init__(self, uri, notify_func, timeout=5):
        self.uri = uri
        self.timeout = timeout
        self.last_message_id = self.load_last_message_id()
        self.notify_func = notify_func

    def load_messages(self):
        resp = requests.get(self.uri)
        return parse_messages(resp.text)

    def load_last_message_id(self):
        data = '-1'
        dirname = os.path.dirname(LAST_MESSAGE_ID_FILE)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        try:
            with open(LAST_MESSAGE_ID_FILE) as f:
                data = f.read()
        except IOError:
            pass
        return int(data)

    def update_last_message_id(self, last_id):
        with open(LAST_MESSAGE_ID_FILE, 'w') as f:
            f.write(str(last_id))
        self.last_message_id = last_id

    def show_new_messages(self, messages):
        for message in messages:
            if message.id > self.last_message_id:
                self.notify_func(message.text)
                self.update_last_message_id(message.id)

    def start(self):
        while True:
            messages = self.load_messages()
            self.show_new_messages(messages)
            time.sleep(self.timeout)


if __name__ == "__main__":
    monitor = TopicMonitor(
        uri=PHPBB_URL, notify_func=notify_telegram,
        timeout=UPDATE_TIMEOUT,
    )
    monitor.start()
