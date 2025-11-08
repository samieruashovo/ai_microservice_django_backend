import json
import threading
import time
from kafka import KafkaConsumer, KafkaProducer
from django.conf import settings

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def run_inference(prompt: str) -> str:
    """
    Dummy model inference function.
    You can later integrate DeepSeek, GPT, Sora, etc.
    """
    time.sleep(2)  # simulate processing delay
    return f"LLM response for: '{prompt}'"

def start_inference_worker():
    def worker():
        consumer = KafkaConsumer(
            settings.KAFKA_REQUEST_TOPIC,
            bootstrap_servers=settings.KAFKA_BROKER,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id="llm_service"
        )
        print("🧠 LLM worker started and listening for requests...")
        for message in consumer:
            data = message.value
            request_id = data.get("request_id")
            prompt = data.get("prompt")
            print(f"🔹 Received prompt [{request_id}]: {prompt}")

            result = run_inference(prompt)

            response = {"request_id": request_id, "result": result}
            producer.send(settings.KAFKA_RESPONSE_TOPIC, response)
            producer.flush()
            print(f"✅ Sent response for [{request_id}]")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
