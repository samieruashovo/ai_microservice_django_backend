import json
import threading
from kafka import KafkaProducer, KafkaConsumer
from django.conf import settings
from django.core.cache import cache

# Producer setup
producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_inference_request(request_id, prompt):
    message = {"request_id": request_id, "prompt": prompt}
    producer.send(settings.KAFKA_REQUEST_TOPIC, message)
    producer.flush()

# Consumer setup (runs in background)
def start_response_consumer():
    def consume():
        consumer = KafkaConsumer(
            settings.KAFKA_RESPONSE_TOPIC,
            bootstrap_servers=settings.KAFKA_BROKER,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id="api_gateway"
        )
        for message in consumer:
            data = message.value
            request_id = data.get("request_id")
            result = data.get("result")
            cache.set(request_id, result, timeout=300)
            print(f"✅ Cached response for {request_id}")

    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
