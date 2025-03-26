from locust import HttpUser, task, between
import uuid
import logging
class MessageUser(HttpUser):
    wait_time = between(1, 3)  # Tiempo de espera entre tareas simuladas
    host = "https://af-gopapa.azurewebsites.net"  # Cambia esta URL por la de tu API

    @task
    def test_message_endpoint(self):
        
        unique_message_id = f"msg-{uuid.uuid4()}"
        unique_conversation_id = f"conv-{uuid.uuid4()}"
        
        payload = {
        "query": "que hay en el menu",
        "conversation_id": "1",
        "conversation_name": "1",
        "user_id": "12",
        "restaurant_name": "go_papa"
        }
        # Envía la petición POST al endpoint /message
        response = self.client.post("/agent/chat/message", json=payload)
        # Valida que la respuesta sea exitosa
        print(response.status_code, "  ",response.text)
        logging.info(f"Status Code: {response.status_code}, Response: {response.text}")
        if response.status_code != 200:
            response.failure(f"Error en /api/chat/message: {response.text}")


## Test:
# sh: locust -f load_test.py --host=https://af-gopapa.azurewebsites.net
