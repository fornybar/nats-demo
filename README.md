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

