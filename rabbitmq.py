import ssl
import pika
import config
from typing import List
import functools
import threading


def Run(queues: List[str], do_work):
    conf = config.Settings()

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_NONE

    credentials = pika.PlainCredentials(
        conf.rabbitmq_username, conf.rabbitmq_password)
    parameters = pika.ConnectionParameters(host=conf.rabbitmq_host,
                                           port=conf.rabbitmq_port,
                                           credentials=credentials,
                                           ssl_options=pika.SSLOptions(
                                               context),
                                           heartbeat=0)

    # Creare una connessione a RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    def long_work(connection, channel, delivery_tag, method, properties, body):
        print("New message")
        do_work(channel, method, properties, body)

        print("Completed")
        cb = functools.partial(ack_message, channel, delivery_tag)
        connection.add_callback_threadsafe(cb)

    def on_message(channel, method_frame, header_frame, body, args):
        (connection, threads) = args
        delivery_tag = method_frame.delivery_tag
        t = threading.Thread(target=long_work, args=(
            connection, channel, delivery_tag, method_frame, header_frame, body))
        t.start()
        threads.append(t)

    # Note: prefetch is set to 1 here as an example only and to keep the number of threads created
    # to a reasonable amount. In production you will want to test with different prefetch values
    # to find which one provides the best performance and usability for your solution
    channel.basic_qos(prefetch_count=1)

    threads = []
    on_message_callback = functools.partial(
        on_message, args=(connection, threads))

    def ack_message(channel, delivery_tag):
        """Note that `channel` must be the same pika channel instance via which
        the message being ACKed was retrieved (AMQP protocol constraint).
        """
        if channel.is_open:
            channel.basic_ack(delivery_tag)
        else:
            # Channel is already closed, so we can't ACK this message;
            # log and/or do something that makes sense for your app in this case.
            pass

    for queue in queues:
        # Consumiamo i messaggi dalla seconda coda in un nuovo thread
        channel.basic_consume(queue=queue,
                              on_message_callback=on_message_callback)

    # Avviare il consumer in modalità blocking, in attesa di ricevere messaggi
    print('In attesa di ricevere messaggi...')
    channel.start_consuming()
