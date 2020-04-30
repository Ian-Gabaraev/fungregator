import pika
import uuid
from telegram_rpc.conf import rpc_params
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker


class TelegramLog:
    def __init__(self, cback_q, message):
        self.corr_id = str(uuid.uuid4())
        self.cback_q = cback_q
        self.message = message
        self.ready = False
        self.message_read = False

        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(rpc_params['host'])
            )
        except AMQPConnectionError:
            """
            RabbitMQ is offline
            """
            pass
        else:
            try:
                self.channel = self.connection.channel()
                self.channel.queue_declare(rpc_params['telegram q'],
                                           passive=True)
            except ChannelClosedByBroker:
                """
                server.py is offline
                """
                pass
            else:
                self.result = self.channel.queue_declare('', auto_delete=True)
                self.gateway_callback = self.result.method.queue
                self.ready = True

    def callback(self, ch, method, props, body):
        try:
            ch.queue_declare(props.reply_to, passive=True)
        except ChannelClosedByBroker:
            """
            Message sender callback queue is offline
            """
            pass
        else:
            if props.correlation_id == self.corr_id:
                self.message_read = True
                ch.basic_publish(
                    body='[+] Telegram notification OK',
                    exchange='',
                    routing_key=self.cback_q,
                )
            else:
                pass

    def send_message(self):
        try:
            assert self.ready
        except AssertionError:
            pass
        else:
            self.channel.basic_publish(
                body=str(self.message),
                exchange='',
                routing_key=rpc_params['telegram q'],
                properties=pika.BasicProperties(
                    reply_to=self.gateway_callback,
                    correlation_id=self.corr_id
                )
            )
            self.channel.basic_consume(
                queue=self.gateway_callback,
                auto_ack=True,
                on_message_callback=self.callback
            )
            self.connection.process_data_events(time_limit=5)


def register_error(obj, message):
    msg = '[x] %r says: %s' % (obj.__str__, message)
    TelegramLog(rpc_params['cback'], msg).send_message()
