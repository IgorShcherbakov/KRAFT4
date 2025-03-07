import uuid
import logging
from confluent_kafka import Producer


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    producer_conf = {
       "bootstrap.servers": "localhost:9011",

       "security.protocol": "SASL_SSL",
       "ssl.ca.location": "ca.crt",  # Сертификат центра сертификации
       "ssl.certificate.location": "kafka-1-creds/kafka-1.crt",  # Сертификат клиента Kafka
       "ssl.key.location": "kafka-1-creds/kafka-1.key",  # Приватный ключ для клиента Kafka

       # Настройки SASL-аутентификации
       "sasl.mechanism": "PLAIN",  # Используемый механизм SASL (PLAIN)
       "sasl.username": "admin",  # Имя пользователя для аутентификации
       "sasl.password": "admin-secret",  # Пароль пользователя для аутентификации
    }

    producer = Producer(producer_conf)

    key = f"key-{uuid.uuid4()}"
    value = "SASL/PLAIN"
    producer.produce(
        "sasl-plain-topic",
        key=key,
        value=value,
    )
    producer.flush()
    logger.info(f"Отправлено сообщение: {key=}, {value=}") 


    #chcp 866
    #chcp 65001