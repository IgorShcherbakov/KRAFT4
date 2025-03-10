import uuid
import logging
from confluent_kafka import Producer


logger = logging.getLogger(__name__)


def delivery_report(err, msg):
    """
    Проверить статус доставки сообщения
    """
    if err is not None:
        logger.info(f"Ошибка доставки сообщения в топик {msg.topic()}: {err}")
    else:
        logger.info(f"Сообщение «{msg.__str__()}» доставлено в {msg.topic()} [{msg.partition()}]")

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
       "sasl.username": "producer",  # Имя пользователя для аутентификации
       "sasl.password": "producer",  # Пароль пользователя для аутентификации
    }

    # создание продюсера
    producer = Producer(producer_conf)

    # список топиков
    topics = ["topic-1", "topic-2", "topic-3"]

    for topic in topics:
        producer.produce(
            topic,
            key=f"key-{uuid.uuid4()}",
            value="SASL/PLAIN",
            callback=delivery_report 
        )
    producer.flush()