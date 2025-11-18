from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api_gateway.core"

    def ready(self):
        from api_gateway.core.kafka_client import start_response_consumer
        start_response_consumer()
