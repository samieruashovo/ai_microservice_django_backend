import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .kafka_client import send_inference_request

@api_view(['POST'])
def generate_response(request):
    prompt = request.data.get('prompt')
    if not prompt:
        return Response({'error': 'Prompt is required'}, status=400)

    request_id = str(uuid.uuid4())
    send_inference_request(request_id, prompt)
    return Response({'request_id': request_id, 'message': 'Request sent to LLM service'})
    

@api_view(['GET'])
def get_response(request, request_id):
    result = cache.get(request_id)
    if result:
        return Response({'request_id': request_id, 'result': result})
    return Response({'status': 'processing', 'request_id': request_id})
