import ssl
import pika
import config


def get_connection():
    conf = config.Settings()

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_NONE

    credentials = pika.PlainCredentials(
        conf.rabbitmq_username, conf.rabbitmq_password)
    parameters = pika.ConnectionParameters(host=conf.rabbitmq_host,
                                           port=conf.rabbitmq_port,
                                           credentials=credentials,
                                           ssl_options=pika.SSLOptions(context),
                                           heartbeat=0)

    # Creare una connessione a RabbitMQ
    return pika.BlockingConnection(parameters)
