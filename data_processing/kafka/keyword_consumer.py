import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
import os

# Download NLTK data (only need to run once)
nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords_with_frequency(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    
    # Remove punctuation and non-alphabetic characters
    tokens = [word for word in tokens if word.isalpha()]
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Count word frequencies
    frequency = Counter(filtered_tokens)
    
    # Convert to list of tuples
    keywords_with_frequency = [(word, count) for word, count in frequency.items()]
    
    return keywords_with_frequency


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
	'session.timeout.ms': 45000,   
    'heartbeat.interval.ms': 15000, # Ensure it's less than session.timeout.ms
    'max.poll.interval.ms': 60000,
	'default.topic.config': {'auto.offset.reset': 'smallest'},
}

# Create a Kafka consumer
consumer = Consumer(**conf)
consumer.subscribe([topic_name])

all_text = ""  

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
			message_value = msg.value().decode('utf-8')
			comment_data = json.loads(message_value)
			all_text += comment_data.get('text', '') + ' '
finally:
	# Extract keywords and their frequencies
    keywords = extract_keywords_with_frequency(all_text)
	# Get the top 50 most frequent keywords
    top_keywords = sorted(keywords, key=lambda item: item[1], reverse=True)[:50]
	# Clean up on exit
    consumer.close()






