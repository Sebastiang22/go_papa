#!/usr/bin/env python3
import socketio
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from inference.graphs.restaurant_graph import RestaurantChatAgent
from langchain.schema import AIMessage

class ClienteWhatsApp:
    def __init__(self, server_url="http://localhost:3000"):
        self.sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5,
            logger=True,
            engineio_logger=True
        )
        self.server_url = server_url
        self.esta_conectado = False
        self.setup_eventos()

    def setup_eventos(self):
        @self.sio.event
        async def connect():
            print(f"[{self.get_timestamp()}] Conectado al servidor (ID: {self.sio.get_sid()})")
            self.esta_conectado = True

        @self.sio.event
        async def disconnect():
            print(f"[{self.get_timestamp()}] Desconectado del servidor")
            self.esta_conectado = False

        @self.sio.event
        async def connect_error(data):
            print(f"[{self.get_timestamp()}] Error de conexión: {data}")
            self.esta_conectado = False

        @self.sio.event
        async def keep_alive():
            print(f"[{self.get_timestamp()}] Keep-alive recibido")

        @self.sio.on('new_message')
        async def on_new_message(data: Dict[str, Any]):
            try:
                message_info = self._extract_message_info(data)
                if not message_info:
                    print(f"[{self.get_timestamp()}] Error: Invalid message data received")
                    return

                self._print_message_info(message_info)
                await self._process_and_respond(message_info)

            except Exception as e:
                print(f"[{self.get_timestamp()}] Error processing message: {str(e)}")

    def _extract_message_info(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            timestamp = datetime.fromtimestamp(data.get('timestamp', 0) / 1000).strftime('%H:%M:%S')
        except Exception:
            timestamp = self.get_timestamp()

        sender = data.get('sender', 'desconocido')
        raw_number = data.get('from', '')
        if not raw_number:
            return None

        number = raw_number.split('@')[0] if '@' in raw_number else raw_number
        incoming_message = data.get('message', '')
        if not incoming_message:
            return None

        return {
            'timestamp': timestamp,
            'sender': sender,
            'number': number,
            'message': incoming_message
        }

    def _print_message_info(self, message_info: Dict[str, Any]) -> None:
        print(f"\n{'='*50}")
        print(f"📱 [{message_info['timestamp']}] Mensaje de {message_info['sender']}")
        print(f"📞 Número: {message_info['number']}")
        print(f"💬 Mensaje: {message_info['message']}")
        print(f"{'='*50}")

    async def _process_and_respond(self, message_info: Dict[str, Any]) -> None:
        try:
            agent = RestaurantChatAgent()
            state, _ = await agent.invoke_flow(
                user_input=message_info['message'],
                conversation_id=f"conversation_{message_info['number']}",
                conversation_name=f"Conversación con {message_info['number']}",
                user_id=message_info['number'],
                restaurant_name="go_papa"
            )

            if not isinstance(state, dict):
                raise ValueError("Invalid state returned from agent")

            messages = state.get("messages", [])
            if not messages:
                raise ValueError("No messages found in state")

            ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
            if not ai_messages:
                raise ValueError("No AI messages found in conversation")

            response = ai_messages[-1].content.replace("**", "*")
            
            if isinstance(response, (list, dict)):
                response = str(response)
            elif not isinstance(response, str):
                response = str(response)

            print(f"[{self.get_timestamp()}] Respuesta generada: {response}")
            await self.enviar_mensaje(message_info['number'], response)

        except Exception as e:
            print(f"[{self.get_timestamp()}] Error al procesar mensaje: {str(e)}")
            return

    def get_timestamp(self) -> str:
        return datetime.now().strftime('%H:%M:%S')

    async def conectar(self) -> bool:
        if not self.esta_conectado:
            try:
                print(f"[{self.get_timestamp()}] Conectando a {self.server_url}...")
                await self.sio.connect(self.server_url, wait_timeout=10)
                await asyncio.sleep(1)
                return self.esta_conectado
            except Exception as e:
                print(f"[{self.get_timestamp()}] Error al conectar: {str(e)}")
                return False
        return True

    async def desconectar(self) -> None:
        if self.esta_conectado:
            print(f"[{self.get_timestamp()}] Desconectando...")
            await self.sio.disconnect()
            self.esta_conectado = False

    async def enviar_mensaje(self, numero: str, mensaje: str) -> bool:
        if not self.esta_conectado:
            print(f"[{self.get_timestamp()}] No hay conexión con el servidor")
            return False

        numero_formateado = self._format_phone_number(numero)
        if not numero_formateado:
            return False

        print(f"[{self.get_timestamp()}] Enviando mensaje a {numero_formateado}...")
        try:
            await self.sio.emit('ping')
            response = await asyncio.wait_for(
                self.sio.call('send_message', {'number': numero_formateado, 'message': mensaje}),
                timeout=30.0
            )
            await self.sio.emit('ping')

            if response and response.get('success'):
                print(f"[{self.get_timestamp()}] Mensaje enviado exitosamente")
                return True
            else:
                error = response.get('error') if response else 'Error desconocido'
                print(f"[{self.get_timestamp()}] Error al enviar mensaje: {error}")
                return False

        except asyncio.TimeoutError:
            print(f"[{self.get_timestamp()}] Tiempo de espera agotado")
            return False
        except Exception as e:
            print(f"[{self.get_timestamp()}] Error: {str(e)}")
            return False

    async def enviar_pdf(self, numero: str) -> bool:
        """Envía un archivo PDF al número especificado.

        Args:
            numero (str): Número de teléfono del destinatario.

        Returns:
            bool: True si el envío fue exitoso, False en caso contrario.
        """
        if not self.esta_conectado:
            print(f"[{self.get_timestamp()}] No hay conexión con el servidor")
            return False

        numero_formateado = self._format_phone_number(numero)
        if not numero_formateado:
            return False

        print(f"[{self.get_timestamp()}] Enviando PDF a {numero_formateado}...")
        try:
            await self.sio.emit('ping')
            response = await asyncio.wait_for(
                self.sio.call('send_pdf', {'number': numero_formateado}),
                timeout=30.0
            )
            await self.sio.emit('ping')

            if response and response.get('success'):
                print(f"[{self.get_timestamp()}] PDF enviado exitosamente")
                return True
            else:
                error = response.get('error') if response else 'Error desconocido'
                print(f"[{self.get_timestamp()}] Error al enviar PDF: {error}")
                return False

        except asyncio.TimeoutError:
            print(f"[{self.get_timestamp()}] Tiempo de espera agotado al enviar PDF")
            return False
        except Exception as e:
            print(f"[{self.get_timestamp()}] Error al enviar PDF: {str(e)}")
            return False

    def _format_phone_number(self, numero: str) -> Optional[str]:
        numero_formateado = numero.replace('+', '').replace(' ', '').replace('-', '')
        if not numero_formateado.isdigit() or len(numero_formateado) < 10:
            print(f"[{self.get_timestamp()}] Número inválido: {numero}")
            return None
        return numero_formateado

if __name__ == "__main__":
    async def main():
        cliente = ClienteWhatsApp()
        if not await cliente.conectar():
            print("No se pudo conectar al servidor")
            return

        print("Cliente listo para recibir mensajes...\nPresiona Ctrl+C para salir.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nCerrando cliente...")
        await cliente.desconectar()

    asyncio.run(main())
