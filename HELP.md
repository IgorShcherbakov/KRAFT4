1.1. Установить OpenSSL

1.2. Создание файла конфигурации для корневого сертификата (Root CA)
Создать новый конфигурационный файл ca.cnf:
```bash
[ policy_match ] 
countryName = match 
stateOrProvinceName = match
organizationName = match
organizationalUnitName = optional
commonName = supplied
emailAddress = optional

[ req ]
prompt = no 
distinguished_name = dn
default_md = sha256
default_bits = 4096
x509_extensions = v3_ca 

[ dn ]
countryName = RU 
organizationName = Yandex
organizationalUnitName = Practice
localityName = Moscow
commonName = yandex-practice-kafka-ca

[ v3_ca ] 
subjectKeyIdentifier=hash
basicConstraints = critical,CA:true
authorityKeyIdentifier = keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign 
```

1.3. Создание корневого сертификата (Root CA)
```bash
openssl req -new -nodes -x509 -days 365 -newkey rsa:2048 -keyout ca.key -out ca.crt -config ca.cnf
```

1.4. Создание файла ca.pem (на windows type ca.crt ca.key > ca.pem)
```bash
cat ca.crt ca.key > ca.pem
```

1.5. Создание файла конфигурации для брокера на примере kafka-1 (kafka-1-creds/kafka-1.cnf)
```bash
[req]
prompt = no
distinguished_name= dn
default_md = sha256
default_bits = 4096 
req_extensions = v3_req 

[ dn ]
countryName = RU 
organizationName = Yandex 
organizationalUnitName = Practice 
localityName = Moscow
commonName=yandex-practice-kafka-1 

[ v3_ca ]
subjectKeyIdentifier=hash
basicConstraints = critical,CA:true
authorityKeyIdentifier=keyid:always,issuer:always
keyUsage = critical,keyCertSign,cRLSign 

[ v3_req ]
subjectKeyIdentifier = hash 
basicConstraints = CA:FALSE
nsComment = "OpenSSL Generated Certificate"
keyUsage = critical, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names 

[ alt_names ] 
DNS.1=kafka-1
DNS.2=kafka-1-external 
DNS.3=localhost 
```

1.6. Создание приватного ключа и запроса на сертификат (CSR)
openssl req -new -newkey rsa:2048 -keyout kafka-1-creds/kafka-1.key -out kafka-1-creds/kafka-1.csr -config kafka-1-creds/kafka-1.cnf -nodes   

1.7. Подпись сертификата брокера с помощью CA
openssl x509 -req -days 3650 -in kafka-1-creds/kafka-1.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out kafka-1-creds/kafka-1.crt -extfile kafka-1-creds/kafka-1.cnf -extensions v3_req

1.8. Создание PKCS12-хранилища
openssl pkcs12 -export -in kafka-1-creds/kafka-1.crt -inkey kafka-1-creds/kafka-1.key -chain -CAfile ca.pem -name kafka-1 -out kafka-1-creds/kafka-1.p12 -password pass:kafka-1

1.9. Создание keystore для Kafka
keytool -importkeystore -deststorepass kafka-1 -destkeystore kafka-1-creds/kafka.kafka-1.keystore.pkcs12 -srckeystore kafka-1-creds/kafka-1.p12 -deststoretype PKCS12 -srcstoretype PKCS12 -noprompt -srcstorepass kafka-1

1.10. Создание truststore для Kafka
keytool -import -file ca.crt -alias ca -keystore kafka-1-creds/kafka.kafka-1.truststore.jks -storepass kafka-1 -noprompt

1.11. Сохранение секретов в файлы
echo kafka-1 > kafka-1-creds/kafka-1_sslkey_creds 
echo kafka-1 > kafka-1-creds/kafka-1_keystore_creds 
echo kafka-1 > kafka-1-creds/kafka-1_truststore_creds

1.12. Проверить корректность настройки SSL в Kafka-брокере, выполнив команду: 
openssl s_client -connect localhost:9091 -CAfile ca.crt
openssl s_client -connect localhost:9093 -CAfile ca.crt
openssl s_client -connect localhost:9095 -CAfile ca.crt

1.13. Поднять/положить сборку
docker compose -f docker-compose-zoo.yml down -v
docker compose -f docker-compose-zoo.yml up -d

bin/kafka-acls.sh --authorizer-properties zookeeper.connect=localhost:2181 --add --allow-principal User:newuser --operation Read --topic your_topic_name

bin/kafka-acls.sh --authorizer-properties zookeeper.connect=localhost:2181 --list --topic your_topic_name

docker compose up
docker exec -it 46d9a3347838 bash

```bash
kafka-acls --bootstrap-server kafka-0:9010 \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--remove \
--allow-principal User:producer \
--operation read \
--topic topic-1
```

# дать все права на кластер
docker exec -it kafka-0 kafka-acls --bootstrap-server kafka-0:9090 
--command-config /tmp/adminclient-configs.conf \
--add --allow-principal User:admin --operation All --cluster

KAFKA_AUTHORIZER_CLASS_NAME: kafka.security.authorizer.AclAuthorizer
KAFKA_SUPER_USERS: User:admin
KAFKA_INTER_BROKER_LISTENER_NAME: SSL
     KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL: PLAIN
     KAFKA_ZOOKEEPER_SET_ACL: 'true'

kafka-topics --create --topic topic-1 --bootstrap-server kafka-2:9094 --partitions 3 --replication-factor 2