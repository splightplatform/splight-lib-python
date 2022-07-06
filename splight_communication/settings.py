import os
import datetime

# Kafka queue
CONFLUENT_CONSUMER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'group.id': datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
    'auto.offset.reset': 'latest',
}
CONFLUENT_CONSUMER_CONFIG = {key: value for key, value in CONFLUENT_CONSUMER_CONFIG.items() if value}

CONFLUENT_PRODUCER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
}
CONFLUENT_PRODUCER_CONFIG = {key: value for key, value in CONFLUENT_PRODUCER_CONFIG.items() if value is not None}

CONFLUENT_ADMIN_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
}

# Zero MQ queue
ZMQ_RECEIVER_PORT = int(os.getenv('ZMQ_RECEIVER_PORT', "5555"))
ZMQ_SENDER_PORT = int(os.getenv('ZMQ_SENDER_PORT', "5556"))
