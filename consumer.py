import logging
from confluent_kafka import Consumer


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    consumer_conf = {
        "bootstrap.servers": "localhost:9011",
        "group.id": "consumer-ssl-group",
        "auto.offset.reset": "earliest",

        "security.protocol": "SASL_SSL", 
        "ssl.ca.location": "ca.crt",  # Сертификат центра сертификации
        "ssl.certificate.location": "kafka-1-creds/kafka-1.crt",  # Сертификат клиента Kafka
        "ssl.key.location": "kafka-1-creds/kafka-1.key",  # Приватный ключ для клиента Kafka

        # Настройки SASL-аутентификации
       "sasl.mechanism": "PLAIN",  # Используемый механизм SASL (PLAIN)
       "sasl.username": "admin",  # Имя пользователя для аутентификации
       "sasl.password": "admin-secret",  # Пароль пользователя для аутентификации
    }
    consumer = Consumer(consumer_conf)
    consumer.subscribe(["sasl-plain-topic"])

    try:
        while True:
            message = consumer.poll(0.1)

            if message is None:
                continue
            if message.error():
                logger.error(f"Ошибка: {message.error()}")
                continue

            key = message.key().decode("utf-8")
            value = message.value().decode("utf-8")
            logger.info(f"Получено сообщение: {key=}, {value=}, offset={message.offset()}")
    finally:
        consumer.close()