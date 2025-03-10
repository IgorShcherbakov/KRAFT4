# KRAFT4
## Итоговый проект четвёртого модуля

# Задание 1. Балансировка партиций и диагностика кластера

## Подготовка данных
1. Выполните команду:
```bash
docker compose up -d
```
2. Для просмотра запущенных контейнеров в Docker выполните команду:
```bash
docker ps
```
Эта команда отобразит список всех активных контейнеров, включая их идентификаторы, имена, статус, порты и другие важные параметры.
Ожидаемый результат команды:

![alt text](resources/containers.png)

## Решение
1. Создайте новый топик balanced_topic с 8 партициями и фактором репликации 3.
Необходимо перейти в терминал контейнера kafka-0 при помощи команды:
```bash
docker exec -it kafka-0 bash
```
В терминале контейнера выполнить команду:
```bash
kafka-topics.sh --bootstrap-server localhost:9092 --topic balanced_topic --create --partitions 8 --replication-factor 3
```
Результатом выполнения команды будет следующее предупреждение и создание топика balanced_topic с заданными параметрами:

![alt text](resources/create_topic.png)

2. Определите текущее распределение партиций.
В терминале контейнера выполнить команду:
```bash
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic balanced_topic
```
Результатом выполнения команды будет детальная информация о топике balanced_topic, включая его настройки, количество партиций, репликацию и другие параметры:

![alt text](resources/describe_topic.png)

3. Создайте JSON-файл reassignment.json для перераспределения партиций.
В терминале контейнера выполнить команду (перейдите в директорию /tmp):
```bash
cd /tmp
```
Можно проверить директорию в которой находимся (так же это видно в терминале):
```bash
pwd
```
Результат команды:

![alt text](resources/pwd.png)

В терминале контейнера выполнить команду:
```bash
echo '{
    "version": 1,
    "partitions": [
      {"topic": "balanced_topic", "partition": 0, "replicas": [0, 1, 2], "log_dirs": ["any", "any", "any"]},
      {"topic": "balanced_topic", "partition": 1, "replicas": [1, 2, 0], "log_dirs": ["any", "any", "any"]},
      {"topic": "balanced_topic", "partition": 2, "replicas": [2, 0, 1], "log_dirs": ["any", "any", "any"]},
      {"topic": "balanced_topic", "partition": 3, "replicas": [0, 1, 2], "log_dirs": ["any", "any", "any"]},
      {"topic": "balanced_topic", "partition": 4, "replicas": [1, 2, 0], "log_dirs": ["any", "any", "any"]},
      {"topic": "balanced_topic", "partition": 5, "replicas": [2, 0, 1], "log_dirs": ["any", "any", "any"]},
      {"topic": "balanced_topic", "partition": 6, "replicas": [0, 1, 2], "log_dirs": ["any", "any", "any"]},
      {"topic": "balanced_topic", "partition": 7, "replicas": [1, 2, 0], "log_dirs": ["any", "any", "any"]}
    ]
}' > reassignment.json
```
Результат команды:

![alt text](resources/reassignment.png)

4. Перераспределите партиции.
В терминале контейнера выполнить команду:
```bash
kafka-reassign-partitions.sh \
--bootstrap-server localhost:9092 \
--broker-list "1,2,3" \
--topics-to-move-json-file "/tmp/reassignment.json" \
--generate
```
Результат команды:

![alt text](resources/kafka_reassign_partitions.png)

В терминале контейнера выполнить команду:
```bash
kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --reassignment-json-file /tmp/reassignment.json --execute
```
Результат команды:

![alt text](resources/execute.png)

5. Проверьте статус перераспределения.
Проверим в следующем пункте.

6. Убедитесь, что конфигурация изменилась.
В терминале контейнера выполнить команду:
```bash
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic balanced_topic
```
Результат команды (видим что все соответствует требуемой конфигурации):
![alt text](resources/new_describe_topic.png)

7. Смоделируйте сбой брокера:
7.1. Остановите брокер kafka-1.
В новом терминале выполнить команду:
```bash
docker stop kafka-1
```
Результат команды:

![alt text](resources/docker_stop_kafka_1.png)


7.2. Проверьте состояние топиков после сбоя.
В терминале контейнера выполнить команду:
```bash
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic balanced_topic
```
Результат команды:

![alt text](resources/describe_topic_after_down.png)

7.3. Запустите брокер заново.
В новом терминале выполнить команду:
```bash
docker start kafka-1
```
Результат команды:

![alt text](resources/docker_start_kafka_1.png)

7.4. Проверьте, восстановилась ли синхронизация реплик.
В терминале контейнера выполнить команду:
```bash
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic balanced_topic
```
Результат команды:

![alt text](resources/describe_topic_after_recovery.png)

Вывод: после моделирования сбоя и восстановления брокера видим что была восстановлена синхронизация реплик, но упавший брокер был исключен из лидерства.

# Задание 2. Настройка защищённого соединения и управление доступом

## Подготовка данных
1. Создать виртуальное окружение
```bash
python -m venv venv
```
2. Активировать виртуальное окружение
```bash
venv\Scripts\Activate.ps1
```
3. Установить зависимости
```bash
pip install -r requirements.txt
```
4. Выполните команду:
```bash
docker compose -f docker-compose-zoo.yml up -d
```
5. Для просмотра запущенных контейнеров в Docker выполните команду:
```bash
docker ps
```
Эта команда отобразит список всех активных контейнеров, включая их идентификаторы, имена, статус, порты и другие важные параметры.

## Задача
Создать два топика и настроить права доступа:
- topic-1 (доступен как для продюсеров, так и для консьюмеров)
- topic-2 (продюсеры могут отправлять сообщения, консьюмеры не имеют доступа к чтению данных)

## Решение

1. Подключиться к брокеру и создать топики:

Команда для создания топика topic-1:
```bash
kafka-topics --create --topic topic-1 --bootstrap-server kafka-0:9010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf
```

Команда для создания топика topic-2:
```bash
kafka-topics --create --topic topic-2 --bootstrap-server kafka-0:9010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf
```

Команда для создания топика topic-3:
```bash
kafka-topics --create --topic topic-3 --bootstrap-server kafka-0:9010 --partitions 3 --replication-factor 2 --command-config /etc/kafka/secrets/adminclient-configs.conf
```

Результат:

![alt text](resources/acl_create_topic.png)
![alt text](resources/acl_ui_create_topic.png)

2. Подключиться к брокеру и назначить права:

Дать продюсеру права на запись в топик topic-1:
```bash
kafka-acls --bootstrap-server kafka-0:9010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:producer \
--allow-principal User:producer  \
--operation write \
--topic topic-1 
```

Дать продюсеру права на запись в топик topic-2:
```bash
kafka-acls --bootstrap-server kafka-0:9010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:producer \
--allow-principal User:producer  \
--operation write \
--topic topic-2 
```

Результат:

![alt text](resources/producer_access_terminal.png)
![alt text](resources/producer_access_ui.png)

Дать консьюмеру права на чтение топика topic-1:
```bash
kafka-acls --bootstrap-server kafka-0:9010  \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add   --allow-principal User:consumer \
--allow-principal User:consumer  \
--operation read \
--topic topic-1 
```

Результат:

![alt text](resources/consumer_access_terminal.png)
![alt text](resources/consumer_access_ui.png)

Дать консьюмеру доступ к группе консьюмеров:
```bash
kafka-acls --bootstrap-server kafka-0:9010 \
--command-config /etc/kafka/secrets/adminclient-configs.conf \
--add --allow-principal User:consumer \
--operation Read \
--group consumer-ssl-group
```

Результат:

![alt text](resources/consumer_group_terminal.png)
![alt text](resources/consumer_group_ui.png)


3. Запустим продюсер (producer.py)

Результат:

![alt text](resources/producer_result_terminal.png)
![alt text](resources/produser_result_ui.png)

4. Запустим консьюмер (consumer.py)

Результат:

![alt text](resources/consumer_result_terminal.png)

Вывод: 
1. после запуска продюсера видим что сообщения отправлены только в topic-1 и topic-2 (как мы и хотели), а отправка сообщения в topic-3 закончилась ошибкой.
2. после запуска консьюмера видим сообщения из topic-1, а так же ошибку topic-2 (так как доступ к нему мы не настраивали)