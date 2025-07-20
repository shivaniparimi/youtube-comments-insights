from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Kafka consumer configuration
topic_name = 'youtube-comments'
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')

# Create a Kafka consumer configuration
conf = {
	'bootstrap.servers': bootstrap_servers,
	'group.id': 'keyword-group',
	'auto.offset.reset': 'earliest',
	'enable.auto.commit': True,
	'session.timeout.ms': 6000,
	'default.topic.config': {'auto.offset.reset': 'smallest'},
}

# Create a Kafka consumer
consumer = Consumer(**conf)
consumer.subscribe([topic_name])

# Consume messages
try:
	while True:
		msg = consumer.poll(timeout=1.0)  # Poll for a message
		if msg is None:
			continue
		if msg.error():
			if msg.error().code() == KafkaError._PARTITION_EOF:
				# End of partition event
				print('End of partition reached {0}/{1}'.format(msg.topic(), msg.partition()))
			elif msg.error():
				raise KafkaException(msg.error())
		else:
			# Message is a normal message
			print(f"Received message: {msg.value().decode('utf-8')}")
finally:
	# Clean up on exit
	consumer.close()