#  Dreambooth

## Cli

- Start rabbitmq `sudo rabbitmq-server -detached`
- Stop rabbitmq `sudo rabbitmqctl stop`
- list rabbitmq queues `sudo rabbitmqctl list_queues`
- Declare queues `rabbitmqadmin declare queue name=train_photos durable=true` `rabbitmqadmin declare queue name=generate_photos durable=true`
- Dev Launch FastAPI `uvicorn server:app --reload`
- Dev launch rabbit queue `python train_photos_queue.py`
- Test new queue message `rabbitmqadmin -u guest -p guest publish routing_key="train_photos" payload="test"`
- Enabling rabbitmq admin UI `sudo rabbitmq-plugins enable rabbitmq_management` and then expose port: 15672 and login with guest:guest

## GTD

- [-] Api training
- [ ] Api generate
- [ ] Add styles
- [ ] Web app client
  - [ ] Homepage
  - [ ] App
  - [ ] Signup
  - [ ] Payments
- [ ] Mobile app