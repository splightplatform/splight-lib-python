import os
import datetime

# Kafka queue
TOPIC = os.getenv('CONFLUENT_TOPIC')
COMM_TYPE = os.getenv('COMM_TYPE')

CONSUMER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
    'auto.offset.reset': 'latest',
    'group.id': datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
}

PRODUCER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
}

# Zero MQ queue

DEFAULT_RECEIVER_PORT = int(os.getenv('DEFAULT_RECEIVER_PORT', "5555"))
DEFAULT_SENDER_PORT = int(os.getenv('DEFAULT_SENDER_PORT', "5556"))
