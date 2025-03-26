# nats-demo

# Oppgave 1 - Connect to the chatserver
In order to chat with each other you need to connect to our NATS chat server. This task will get you started with NATS, and requires installation and use of the NATS CLI. Instructions are found [here](https://github.com/nats-io/natscli?tab=readme-ov-file#installation), you can use your preferred method of installation.

Next you will need to connect to the server which is hosted at\*:
```
nats://booster.fornybar.eviny.io:4222
```
Authentication is with username/password:
```
username: booster
password:
```
Now we are ready to connect to our chatroom. We will make use of the  [NATS subject-based messaging](https://docs.nats.io/nats-concepts/subjects) to send and receive messages. The subject pattern we will follow is:
```
chat.<your_name>
```
chech the linked document for more information on how nats subjects work and feel free to play around with it later. For now open a terminal and subscribe to our chat.\*\*

Are you receiving any chats yet? If not, maybe you're the first to enter the chatroom. Easy to check, lets write a message. Open another terminal window for this and publish a message. Be sure to use the subject pattern above. \*\*\*

If all is well you now have 2 terminals open, 1 that subscribes to our chatroom and 1 to write messages. Now feel free to chat with the rest before we move on :)


\**Hint 1: create a context*

\*\**Hint 2: What is a logical subject to subscribe to in order to receive other peoples messages? chekc the docs for subject wildcarding*

\*\*\**Hint 3: Command is almost the same as for subscribe*

# Oppgave 2 - Create your own data flow

Now we want to create our own application using NATS. First we need to [download our own nats server](https://docs.nats.io/running-a-nats-service/introduction/installation) and start it up.

This task will use a lot of nats nats-concepts like
- jetstream to persist messages
- durable consumer to remember our progress
- key value bucket to store state
- key value bucket to emulate a database
- request-reply to simulate client server communication like an api

We will connect to a [public api](https://github.com/public-apis/public-apis?tab=readme-ov-file) to collect data, parse this data to our desired format, store in a database and create our own api to serve this data to our customers.
To create a robust architecture we will use multiple microservices all interacting with NATS.

We have included a complete working example connecting to one of [Statnetts public apis](https://driftsdata.statnett.no/restapi): Reserves PrimaryReservesPerDay which you are free to try out on your own and take inspiration from.

Then you should try to create your own example by following the steps below on your favorite api. For instance the [pokemon api](https://pokeapi.co/).

## Connect to the api and get some data (ingest)

Think about how often your application needs to collect new data and how it can know when something is updated

## Extract interesting information and parse it to a desired format (parse)

What do you want to serve to your customers and how can we store it.

## Create an api layer using request-reply (optionally create a http api)

What should be the query paramteters? Authentication?

## Further work

What are some next steps? Using NATS jetstream for logging? Key value bucket for statistics? [Object store](https://docs.nats.io/nats-concepts/jetstream/obj_store)?

Only your imagination can stop you from using `NATS for everything`



# Further reading:
[NATS by example](https://natsbyexample.com/)
