import logging
from dotenv import load_dotenv
import os
import pika
import time
from datetime import datetime


def sender_messages(queue_name: str):
    """ Подключение к RabbitMQ """
    load_dotenv(dotenv_path='/etc/secrets/.env')
    rabbitmq_user = os.getenv('RABBITMQ_USER')
    rabbitmq_pass = os.getenv('RABBITMQ_PASS')
    rabbitmq_host = os.getenv('RABBITMQ_HOST')

    try:
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        # parameters = pika.ConnectionParameters(host='localhost', port=5672, virtual_host='/', credentials=credentials)
        parameters = pika.ConnectionParameters(host=rabbitmq_host, port=5672, virtual_host='/', credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name)
    except Exception as er:
        logging.error(er.args, stack_info=True)
        raise
    return channel, connection


if __name__ == '__main__':
    # Основной логгер
    logging.basicConfig(
        filename='/etc/secrets/log.txt', filemode='a', encoding='utf-8',
        format='SENDER --> | %(asctime)s | %(levelname)s | %(name)s | %(message)s',
        level=logging.INFO)

    # Внутренний логгер
    internal_log = logging.getLogger('internal_log')
    internal_log.setLevel(logging.INFO)
    log_handler = logging.FileHandler('sender.log', mode='a', encoding='utf-8')
    log_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    internal_log.addHandler(log_handler)

    queue_name = 'msg_queue'

    channel, connection = sender_messages(queue_name)

    try:
        i = 0
        while True:
            i += 1
            message = f'Сообщение #{i} отправлено {datetime.now()}'
            channel.basic_publish(exchange='', routing_key=queue_name, body=message.encode())
            internal_log.info(f'Отправлено сообщение: "{message}"')
            time.sleep(5)
    finally:
        connection.close()
