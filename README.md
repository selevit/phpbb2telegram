# PhpBB 3 topic updates monitor via telegram

Sends new posts from a phpbb topic to a telegram channel.
Tested on phpbb3.

```
docker run \
    -e BOT_TOKEN='<telegram_bot_token>' \
    -e CHANNEL_ID='@your_channel' \
    # query parameter start=50000 means the last page
    -e TOPIC_URL='http://forum.example.com/viewtopic.php?f=1&t=2&start=50000' \
    selevit/phpbb2telegram
```

Optional environment variables:

- `UPDATE_TIMEOUT` - timeout in seconds between HTTP requests for topic page (default=5)
- `DEBUG` - If `DEBUG=1`, messages will not send to telegram, just will be written to stdout (default=0)
