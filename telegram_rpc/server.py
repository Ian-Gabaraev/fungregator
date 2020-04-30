import pika
import time
from telegram_rpc.conf import rpc_params
from telegram_rpc.messaging import TelegramMessage
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker


def callback(ch, method, props, body):
    try:
        TelegramMessage().send(str(body))
    except Exception as e:
        pass
    else:
        try:
            ch.queue_declare(props.reply_to, passive=True)
        except ChannelClosedByBroker:
            """
            Message sender callback queue is offline
            """
            pass
        else:
            ch.basic_publish(
                body='[+] Telegram notification OK',
                exchange='',
                routing_key=props.reply_to,
                properties=pika.BasicProperties(
                    reply_to=props.reply_to,
                    correlation_id=props.correlation_id
                )
            )


try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(rpc_params['host'])
    )
except AMQPConnectionError:
    """
    RabbitMQ is offline
    """
    pass
else:
    channel = connection.channel()
    channel.queue_declare(
        rpc_params['telegram q'], auto_delete=True)
    channel.basic_consume(
        queue=rpc_params['telegram q'],
        auto_ack=True,
        on_message_callback=callback,
    )
    channel.start_consuming()
