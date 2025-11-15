import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

from api_gateway.core.kafka_client import send_inference_request


@api_view(['POST'])
def generate_response(request):
    """
    Receives prompt and sends it to Kafka for background processing.
    """
    prompt = request.data.get('prompt')

    if not prompt:
        return Response({'error': 'Prompt is required'}, status=400)

    # Generate unique request ID
    request_id = str(uuid.uuid4())
    print(f"🆔 Generated request ID: {request_id}")
    # Send request to Kafka topic
    send_inference_request(request_id, prompt)

    return Response({
        'request_id': request_id,
        'message': 'Request sent to LLM service'
    })

import redis
r = redis.Redis(host="localhost", port=6379, db=0)

@api_view(['GET'])
def get_response(request, request_id):
    # Ensure request_id is string
    request_id_str = str(request_id)

    result = r.get(request_id_str)  # or cache.get(request_id_str)
    if result:
        return Response({
            "request_id": request_id_str,
            "result": result.decode() if isinstance(result, bytes) else result
        })
    return Response({
        "status": "processing",
        "request_id": request_id_str
    })
