import os
import datetime

# Kafka queue
CONFLUENT_TOPIC = os.getenv('CONFLUENT_TOPIC')

CONFLUENT_CONSUMER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
    'auto.offset.reset': 'latest',
    'group.id': datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
}

CONFLUENT_PRODUCER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
}

# Zero MQ queue
ZMQ_RECEIVER_PORT = int(os.getenv('ZMQ_RECEIVER_PORT', "5555"))
ZMQ_SENDER_PORT = int(os.getenv('ZMQ_SENDER_PORT', "5556"))
