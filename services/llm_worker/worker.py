import json
import redis
from kafka import KafkaConsumer, KafkaProducer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# --------------------------
# Load your model (LOCAL)
# --------------------------
MODEL_PATH = "/home/samier/Documents/llm-models/gemma-3-270m"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float32
)

# --------------------------
# Connect Redis (OPTIONAL in Option B)
# --------------------------
r = redis.Redis(host="localhost", port=6379, db=0)

# --------------------------
# Kafka Producer (send response back)
# --------------------------
response_producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# --------------------------
# Kafka Consumer (requests)
# --------------------------
consumer = KafkaConsumer(
    "inference_requests",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="llm_worker_group"
)

print("🚀 LLM Worker started. Listening for Kafka messages...")

# --------------------------
# Handle incoming messages
# --------------------------
for msg in consumer:
    data = msg.value
    request_id = data["request_id"]
    prompt = data["prompt"]

    print(f"\n📩 Got request: {request_id}")
    print(f"Prompt: {prompt}")

    # --------------------------
    # Run inference
    # --------------------------
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.8
    )
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(f"📝 Generated result: {result}")

    # --------------------------
    # Option B → send result back to Kafka
    # --------------------------
    response_message = {
        "request_id": request_id,
        "result": result
    }

    response_producer.send("inference_responses", response_message)
    response_producer.flush()
    print(f"📤 Sent result back to Kafka for {request_id}")

    # OPTIONAL: Still save in Redis if you want dual system
    r.set(request_id, result)
    print(f"📦 Saved result to Redis with key {request_id}")
