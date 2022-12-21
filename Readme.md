#  Dreambooth

## Cli

- Start rabbitmq `sudo rabbitmq-server`
- Stop rabbitmq `sudo rabbitmqctl stop`
- list rabbitmq queues `sudo rabbitmqctl list_queues`
- Dev Launch FastAPI `uvicorn app.server:app --reload`
- Dev launch rabbit queue `python rabbitmq_queue.py`
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