# Random Notes
For debugging

```bash
export BOTURL=botXXXX
export CHATID=-12345
export CONNECTHOST=http://localhost:8083
export BOOTSTRAPSERVER=localhost:9092
```

## Telegram

```bash
curl https://api.telegram.org/${BOTURL}/getUpdates
curl -X POST -H "Content-Type: application/json" -d '{"chat_id":"'${CHATID}'", "text":"Hello world!"}' https://api.telegram.org/${BOTURL}/sendMessage
```


## Telegram and Kafka

```bash
curl -s -X GET ${CONNECTHOST}/connectors?expand=status | jq '.'
curl -X DELETE ${CONNECTHOST}/connectors/teaddybear-telegram-sink

echo "MESSAGE=one two three" | kafka-console-producer --broker-list ${BOOTSTRAPSERVER} --topic TEDDYTOPIC

kafka-topics --bootstrap-server ${BOOTSTRAPSERVER} --delete --topic teaddybear-telegram-topic
kafka-console-consumer --bootstrap-server ${BOOTSTRAPSERVER} --topic error-responses --from-beginning
kafka-console-consumer --bootstrap-server ${BOOTSTRAPSERVER} --topic success-responses --from-beginning
kafka-console-consumer --bootstrap-server ${BOOTSTRAPSERVER} --topic teaddybear-telegram-topic --from-beginning
```


