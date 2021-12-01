import os

TOPIC = os.getenv('CONFLUENT_TOPIC')

CONSUMER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
    'group.id': os.getenv('CONFLUENT_GROUP_ID'),
    'auto.offset.reset': 'latest',
}

PRODUCER_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVER'),
    'security.protocol': os.getenv('CONFLUENT_SECURITY_PROTOCOL'),
    'sasl.mechanisms': os.getenv('CONFLUENT_SASL_MECHANISM'),
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_SECRET_KEY'),
}
