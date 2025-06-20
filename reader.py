import logging
import threading
import os
import pika
import psycopg2
import time
from datetime import datetime
from dotenv import load_dotenv


def connect_to_postgres():
    """ Подключение к PostgreSQL """
    load_dotenv(dotenv_path='/etc/secrets/.env')
    host = os.getenv('POSTGRES_HOST')
    database = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    port = os.getenv('POSTGRES_PORT')

    try:
        port = int(port)
    except ValueError as e:
        raise Exception(f"Порт '{port}' указан неправильно.") from e
    postgres_conn = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
    return postgres_conn


def create_table() -> None:
    """ Создать таблицу в БД если ее нет """
    conn = connect_to_postgres()
    cursor = conn.cursor()
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            msg_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.commit()
    except Exception as e:
        logging.error(f"Ошибка создания таблицы в БД: {e}")
    finally:
        cursor.close()
        conn.close()


def save_message(message: str) -> None:
    """
    Сохранение сообщения в БД
    :param message: текст полученного сообщения
    """
    conn = connect_to_postgres()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO messages (msg_text, created_at) VALUES (%s, %s)",
                       (message, datetime.now()))
        conn.commit()
    except Exception as e:
        logging.error(f"Ошибка сохранения в БД: {e}")
    finally:
        cursor.close()
        conn.close()


def reader_messages() -> None:
    """ Подключение к RabbitMQ """
    load_dotenv(dotenv_path='/etc/secrets/.env')
    rabbitmq_user = os.getenv('RABBITMQ_USER')
    rabbitmq_pass = os.getenv('RABBITMQ_PASS')
    rabbitmq_host = os.getenv('RABBITMQ_HOST')

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    # par = pika.ConnectionParameters(host='localhost', port=5672, virtual_host='/', credentials=credentials)
    par = pika.ConnectionParameters(host=rabbitmq_host, port=5672, virtual_host='/', credentials=credentials)
    connection = pika.BlockingConnection(par)
    channel = connection.channel()
    queue_name = 'msg_queue'
    channel.queue_declare(queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=msg_callback, auto_ack=True)
    channel.start_consuming()


def msg_callback(ch, method, properties, body):
    """ Вывод полученного из очереди RabbitMQ сообщения в журнал """
    body = body.decode()
    msg = f'{datetime.now()} Получено сообщение: "{body}"'
    logging.info(msg)
    print(msg)
    # internal_log.info(f'Получено сообщение: "{body}"')
    save_message(body)


if __name__ == '__main__':
    logging.basicConfig(
        filename='/log/log.txt', filemode='a', encoding='utf-8',
        format='--> READER | %(asctime)s | %(levelname)s | %(name)s | %(message)s',
        level=logging.INFO)

    # Внутренний логгер
    internal_log = logging.getLogger('internal_log')
    internal_log.setLevel(logging.INFO)
    log_handler = logging.FileHandler('reader.log', mode='a', encoding='utf-8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    internal_log.addHandler(log_handler)

    try:
        # Запускаем поток чтения сообщений из очереди RabbitMQ
        consume_thread = threading.Thread(target=reader_messages)
        consume_thread.daemon = True
        consume_thread.start()

        # Создаем таблицу, если не создана
        create_table()

        # Каждые 30 секунд выводим кол-во строк в таблице PostgreSQL
        while True:
            with connect_to_postgres() as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM messages;")
                count = cur.fetchone()[0]
                # internal_log.info(f"Количество записей в БД: {count}")
                msg = f"Количество записей в БД: {count}"
                logging.info(msg)
                print(msg)
            time.sleep(30)
    except KeyboardInterrupt:
        pass
