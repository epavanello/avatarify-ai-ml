import rabbitmq
import generate_photos_queue
import train_photos_queue


def do_work(channel, method, properties, body):
    if method.routing_key == 'train_photos':
        train_photos_queue.do_work(channel, method, properties, body)
    elif method.routing_key == 'generate_photos':
        generate_photos_queue.do_work(channel, method, properties, body)


# Doesn't work for multiple queues, need to be single thread
rabbitmq.Run(["train_photos", "generate_photos"], do_work)
