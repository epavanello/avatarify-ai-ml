import rabbitmq
import time
# Definire una funzione di callback per il consumer


def do_work(_channel, method, properties, body: bytes):
    print("recived" + str(body))
    time.sleep(30)
    print("completed" + str(body))


def main():
    rabbitmq.Run(["train_photos"], do_work)


if __name__ == "__main__":
    main()
