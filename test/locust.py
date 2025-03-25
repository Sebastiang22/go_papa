from locust import HttpUser, task, between
import uuid
import logging
class MessageUser(HttpUser):
    wait_time = between(1, 3)  # Tiempo de espera entre tareas simuladas
    host = "https://ca-gopapa-backend.blueriver-8537145c.westus2.azurecontainerapps.io"  # Cambia esta URL por la de tu API

    @task
    def test_message_endpoint(self):
        
        unique_message_id = f"msg-{uuid.uuid4()}"
        unique_conversation_id = f"conv-{uuid.uuid4()}"
        
        payload = {
            "query": "Hola, ¿cómo estás?",
            "message_id": unique_message_id,  # Asigna el UUID
            "conversation_id": unique_conversation_id,
            "conversation_name": "Conversacion de prueba",
            "user_id": "locust_user-001",
            "flag_modifier": False,
            "model_name": "gpt-4o",
            "search_tool": False
        }
        # Envía la petición POST al endpoint /message
        response = self.client.post("/api/chat/message", json=payload)
        # Valida que la respuesta sea exitosa
        print(response.status_code, "  ",response.text)
        logging.info(response.status_code, "  ",response.text)
        if response.status_code != 200:
            response.failure(f"Error en /api/chat/message: {response.text}")


## Test:
# sh: locust -f locust.py --host=https://ca-gopapa-backend.blueriver-8537145c.westus2.azurecontainerapps.io
