import ssl
import pika
import config
from typing import List
import functools
import threading
from logger import LOGGER
import datetime
import time
import os

last_message = datetime.datetime.now()


def Run(queues: List[str], do_work):
    LOGGER.info("Server started for: " + ", ".join(queues))
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
                                           heartbeat=300)

    # Creare una connessione a RabbitMQ
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    def long_work(connection, channel, delivery_tag, method, properties, body):
        LOGGER.info("New message: " + method.routing_key)
        
        try:
            do_work(channel, method, properties, body)
            LOGGER.info("Message complete: " + method.routing_key)
        except Exception as e:
            LOGGER.error("Message failed: " + method.routing_key)
            LOGGER.error(e)
            pass

        cb = functools.partial(ack_message, channel, delivery_tag)
        connection.add_callback_threadsafe(cb)

    def on_message(channel, method_frame, header_frame, body, args):
        global last_message
        last_message = datetime.datetime.now()
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

    # before
    # try:
    #     channel.start_consuming()
    # except KeyboardInterrupt:
    #     channel.stop_consuming()

    # # test
    # # try:
    # #     connection.process_data_events()
    # # except KeyboardInterrupt:
    # #     pass

    # # Wait for all to complete
    # for thread in threads:
    #     thread.join()

    # connection.close()

    global last_message
    try:
        exit = False
        while not exit:
            LOGGER.debug("RabbitMQ ping")
            connection.process_data_events()

            now = datetime.datetime.now()
            exit = ((now - last_message).total_seconds()) > 300
            if exit:
                for thread in threads:
                    if thread.isAlive():
                        LOGGER.info(
                            "Restore timer because there are running threads")
                        exit = False
                        last_message = datetime.datetime.now()
                        break
            time.sleep(2)
        LOGGER.info("Timeout: shutdown")
    except Exception as e:
        LOGGER.error(e)
    except:
        pass
    finally:
        LOGGER.info("Server shutdown")
        os.system("sudo shutdown")

    # Wait for all to complete
    for thread in threads:
        thread.join()

    LOGGER.info("Server closing")

    connection.close()

    LOGGER.info("Connection closed")
