# Обмен данными между docker-контейнерами (docker-compose)

#### Первый скрипт:

• публикует в очередь `RabbitMQ` каждые 5 секунд любое сообщение

#### Второй скрипт:

• читает из очереди `RabbitMQ` эти сообщения и записывает в таблицу БД `PostgreSQL`  
• выводит лог текста сообщения в docker контейнер (время получения, текст сообщения)  
• каждые 30 секунд выводит кол-во строк в таблице `PostgreSQL`  
  
Стэк развернуть в docker контейнерах через docker-compose (1 и 2 скрипты, `RabbitMQ`, `PostgreSQL`). 
В образах не должны быть чувствительных данных (креды подключения к `RabbitMQ`). Все чувствительные 
данные выносятся в `.env` и подключаются через mount в контейнеры. Контейнеры работаю в своей 
собственной docker сети.

---

В процессе выполнения скриптов ведется логирование. Пример записей в журнале:
```
SENDER --> | 2025-06-18 18:39:25,308 | INFO | pika.adapters.utils.connection_workflow | Pika version 1.3.2 connecting to ('172.19.0.3', 5672)
SENDER --> | 2025-06-18 18:39:25,310 | INFO | pika.adapters.utils.io_services_utils | Socket connected: <socket.socket fd=8, family=2, type=1, proto=6, laddr=('172.19.0.4', 40588), raddr=('172.19.0.3', 5672)>
SENDER --> | 2025-06-18 18:39:25,310 | INFO | pika.adapters.utils.connection_workflow | Streaming transport linked up: (<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7fcc246e8470>, _StreamingProtocolShim: <SelectConnection PROTOCOL transport=<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7fcc246e8470> params=<ConnectionParameters host=rabbit port=5672 virtual_host=/ ssl=False>>).
SENDER --> | 2025-06-18 18:39:25,322 | INFO | pika.adapters.utils.connection_workflow | AMQPConnector - reporting success: <SelectConnection OPEN transport=<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7fcc246e8470> params=<ConnectionParameters host=rabbit port=5672 virtual_host=/ ssl=False>>
SENDER --> | 2025-06-18 18:39:25,322 | INFO | pika.adapters.utils.connection_workflow | AMQPConnectionWorkflow - reporting success: <SelectConnection OPEN transport=<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7fcc246e8470> params=<ConnectionParameters host=rabbit port=5672 virtual_host=/ ssl=False>>
SENDER --> | 2025-06-18 18:39:25,323 | INFO | pika.adapters.blocking_connection | Connection workflow succeeded: <SelectConnection OPEN transport=<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7fcc246e8470> params=<ConnectionParameters host=rabbit port=5672 virtual_host=/ ssl=False>>
SENDER --> | 2025-06-18 18:39:25,323 | INFO | pika.adapters.blocking_connection | Created channel=1
SENDER --> | 2025-06-18 18:39:25,327 | INFO | internal_log | Отправлено сообщение: "Сообщение #1 отправлено 2025-06-18 18:39:25.327714"
SENDER --> | 2025-06-18 18:39:30,328 | INFO | internal_log | Отправлено сообщение: "Сообщение #2 отправлено 2025-06-18 18:39:30.328046"
SENDER --> | 2025-06-18 18:39:36,198 | INFO | internal_log | Отправлено сообщение: "Сообщение #3 отправлено 2025-06-18 18:39:36.198377"
SENDER --> | 2025-06-18 18:39:41,199 | INFO | internal_log | Отправлено сообщение: "Сообщение #4 отправлено 2025-06-18 18:39:41.198896"
SENDER --> | 2025-06-18 18:39:46,199 | INFO | internal_log | Отправлено сообщение: "Сообщение #5 отправлено 2025-06-18 18:39:46.199375"
--> READER | 2025-06-18 18:39:50,674 | INFO | pika.adapters.utils.connection_workflow | Pika version 1.3.2 connecting to ('172.19.0.3', 5672)
--> READER | 2025-06-18 18:39:50,675 | INFO | pika.adapters.utils.io_services_utils | Socket connected: <socket.socket fd=9, family=2, type=1, proto=6, laddr=('172.19.0.5', 33616), raddr=('172.19.0.3', 5672)>
--> READER | 2025-06-18 18:39:50,675 | INFO | pika.adapters.utils.connection_workflow | Streaming transport linked up: (<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7f4199c00440>, _StreamingProtocolShim: <SelectConnection PROTOCOL transport=<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7f4199c00440> params=<ConnectionParameters host=rabbit port=5672 virtual_host=/ ssl=False>>).
--> READER | 2025-06-18 18:39:50,678 | INFO | pika.adapters.utils.connection_workflow | AMQPConnector - reporting success: <SelectConnection OPEN transport=<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7f4199c00440> params=<ConnectionParameters host=rabbit port=5672 virtual_host=/ ssl=False>>
--> READER | 2025-06-18 18:39:50,678 | INFO | pika.adapters.utils.connection_workflow | AMQPConnectionWorkflow - reporting success: <SelectConnection OPEN transport=<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7f4199c00440> params=<ConnectionParameters host=rabbit port=5672 virtual_host=/ ssl=False>>
--> READER | 2025-06-18 18:39:50,678 | INFO | pika.adapters.blocking_connection | Connection workflow succeeded: <SelectConnection OPEN transport=<pika.adapters.utils.io_services_utils._AsyncPlaintextTransport object at 0x7f4199c00440> params=<ConnectionParameters host=rabbit port=5672 virtual_host=/ ssl=False>>
--> READER | 2025-06-18 18:39:50,678 | INFO | pika.adapters.blocking_connection | Created channel=1
--> READER | 2025-06-18 18:39:50,681 | INFO | internal_log | Получено сообщение: "Сообщение #1 отправлено 2025-06-18 18:39:25.327714"
--> READER | 2025-06-18 18:39:50,711 | INFO | internal_log | Получено сообщение: "Сообщение #2 отправлено 2025-06-18 18:39:30.328046"
--> READER | 2025-06-18 18:39:50,714 | INFO | internal_log | Количество записей в БД: 35
--> READER | 2025-06-18 18:39:50,717 | INFO | internal_log | Получено сообщение: "Сообщение #3 отправлено 2025-06-18 18:39:36.198377"
--> READER | 2025-06-18 18:39:50,725 | INFO | internal_log | Получено сообщение: "Сообщение #4 отправлено 2025-06-18 18:39:41.198896"
--> READER | 2025-06-18 18:39:50,733 | INFO | internal_log | Получено сообщение: "Сообщение #5 отправлено 2025-06-18 18:39:46.199375"
SENDER --> | 2025-06-18 18:39:51,200 | INFO | internal_log | Отправлено сообщение: "Сообщение #6 отправлено 2025-06-18 18:39:51.199870"
--> READER | 2025-06-18 18:39:51,200 | INFO | internal_log | Получено сообщение: "Сообщение #6 отправлено 2025-06-18 18:39:51.199870"
SENDER --> | 2025-06-18 18:39:56,200 | INFO | internal_log | Отправлено сообщение: "Сообщение #7 отправлено 2025-06-18 18:39:56.200424"
--> READER | 2025-06-18 18:39:56,201 | INFO | internal_log | Получено сообщение: "Сообщение #7 отправлено 2025-06-18 18:39:56.200424"
SENDER --> | 2025-06-18 18:40:01,201 | INFO | internal_log | Отправлено сообщение: "Сообщение #8 отправлено 2025-06-18 18:40:01.201051"
--> READER | 2025-06-18 18:40:01,202 | INFO | internal_log | Получено сообщение: "Сообщение #8 отправлено 2025-06-18 18:40:01.201051"
SENDER --> | 2025-06-18 18:40:07,069 | INFO | internal_log | Отправлено сообщение: "Сообщение #9 отправлено 2025-06-18 18:40:07.069624"
--> READER | 2025-06-18 18:40:07,070 | INFO | internal_log | Получено сообщение: "Сообщение #9 отправлено 2025-06-18 18:40:07.069624"
SENDER --> | 2025-06-18 18:40:12,070 | INFO | internal_log | Отправлено сообщение: "Сообщение #10 отправлено 2025-06-18 18:40:12.070215"
--> READER | 2025-06-18 18:40:12,070 | INFO | internal_log | Получено сообщение: "Сообщение #10 отправлено 2025-06-18 18:40:12.070215"
SENDER --> | 2025-06-18 18:40:17,071 | INFO | internal_log | Отправлено сообщение: "Сообщение #11 отправлено 2025-06-18 18:40:17.070788"
--> READER | 2025-06-18 18:40:17,071 | INFO | internal_log | Получено сообщение: "Сообщение #11 отправлено 2025-06-18 18:40:17.070788"
--> READER | 2025-06-18 18:40:21,589 | INFO | internal_log | Количество записей в БД: 45
```

### Статистика RabbitMQ:
![RabbitMQ](https://github.com/Topotun77/vk_tw/blob/master/ScreenShots/001.JPG?raw=true)


## Для запуска приложения:
1. **Файл с чувствительными данными `.env` поместить в корень проекта.**  
2. **Запустите весь стэк командой:**  
```
docker-compose up -d
```
Это запустит все сервисы одновременно в отдельных контейнерах:

- **RabbitMQ** (сервер очередей) - контейнер `rabbitmq-container`  
- **PostgreSQL** (база данных) - контейнер `postgres-container`  
- **Sender** (отправка сообщений) - контейнер `sender-container`  
- **Reader** (чтение сообщений и запись в БД) - контейнер `reader-container`.
