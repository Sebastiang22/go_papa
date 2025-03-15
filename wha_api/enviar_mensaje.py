#!/usr/bin/env python3
"""
Cliente interactivo para enviar mensajes de WhatsApp
Permite enviar múltiples mensajes sin cerrar el programa
"""

import socketio
import asyncio
import sys
import signal
from datetime import datetime

class ClienteWhatsApp:
    def __init__(self, server_url="http://localhost:3000"):
        # Configurar cliente Socket.IO con más opciones
        self.sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5,
            logger=True,
            engineio_logger=True
        )
        self.server_url = server_url
        self.running = True
        self.esta_conectado = False
        self.setup_eventos()
        
    def setup_eventos(self):
        @self.sio.event
        def connect():
            print(f"\n✅ [{self.get_timestamp()}] Conectado al servidor (ID: {self.sio.get_sid()})")
            self.esta_conectado = True

        @self.sio.event
        def disconnect():
            print(f"\n❌ [{self.get_timestamp()}] Desconectado del servidor")
            self.esta_conectado = False

        @self.sio.event
        def connect_error(data):
            print(f"\n❌ [{self.get_timestamp()}] Error de conexión: {data}")
            self.esta_conectado = False

        @self.sio.event
        def keep_alive():
            print(f"💓 [{self.get_timestamp()}] Keep-alive recibido")

        # Eventos de depuración
        @self.sio.on('*')
        def catch_all(event, data):
            if event not in ['keep_alive']:  # Ignorar keep_alive en los logs generales
                print(f"\n📡 [{self.get_timestamp()}] Evento recibido: {event}")
                print(f"Datos: {data}")

    def get_timestamp(self):
        return datetime.now().strftime('%H:%M:%S')

    async def conectar(self):
        if not self.esta_conectado:
            try:
                print(f"\n🔄 [{self.get_timestamp()}] Intentando conectar a {self.server_url}...")
                await self.sio.connect(self.server_url, wait_timeout=10)
                await asyncio.sleep(1)  # Esperar a que se establezca la conexión
                return self.esta_conectado
            except Exception as e:
                print(f"\n❌ [{self.get_timestamp()}] Error al conectar: {str(e)}")
                return False
        return True

    async def desconectar(self):
        if self.esta_conectado:
            print(f"\n🔌 [{self.get_timestamp()}] Desconectando del servidor...")
            await self.sio.disconnect()
            self.esta_conectado = False

    async def enviar_mensaje(self, numero: str, mensaje: str):
        try:
            if not self.esta_conectado:
                print(f"\n❌ [{self.get_timestamp()}] No hay conexión con el servidor")
                return False

            # Validar y formatear número
            numero = numero.replace('+', '').replace(' ', '').replace('-', '')
            if not numero.isdigit() or len(numero) < 10:
                print(f"\n❌ [{self.get_timestamp()}] Número inválido. Debe contener solo dígitos y tener al menos 10 números")
                return False

            print(f"\n📤 [{self.get_timestamp()}] Enviando mensaje a {numero}...")
            print(f"Mensaje: {mensaje}")
            
            try:
                # Enviar un ping antes del mensaje
                await self.sio.emit('ping')
                
                print(f"⏳ [{self.get_timestamp()}] Esperando respuesta del servidor...")
                response = await asyncio.wait_for(
                    self.sio.call('send_message', {
                        'number': numero,
                        'message': mensaje
                    }),
                    timeout=30.0
                )
                
                # Enviar otro ping después del mensaje
                await self.sio.emit('ping')
                
                print(f"📨 [{self.get_timestamp()}] Respuesta recibida: {response}")
                
                if response and response.get('success'):
                    print(f"✅ [{self.get_timestamp()}] Mensaje enviado exitosamente")
                    return True
                else:
                    error = response.get('error') if response else 'Error desconocido'
                    print(f"❌ [{self.get_timestamp()}] Error al enviar mensaje: {error}")
                    return False
                    
            except asyncio.TimeoutError:
                print(f"⏰ [{self.get_timestamp()}] Tiempo de espera agotado")
                # Intentar reconectar si hay timeout
                if not self.esta_conectado:
                    print(f"🔄 [{self.get_timestamp()}] Intentando reconectar...")
                    await self.conectar()
                return False
                
        except Exception as e:
            print(f"❌ [{self.get_timestamp()}] Error: {str(e)}")
            print(f"📋 Detalles técnicos: {e.__class__.__name__}")
            return False

    async def menu_interactivo(self):
        if not await self.conectar():
            print(f"\n❌ [{self.get_timestamp()}] No se pudo establecer la conexión inicial")
            return

        while self.running:
            try:
                print("\n" + "="*50)
                print("🔷 Cliente WhatsApp - Menú de Envío 🔷")
                print(f"Estado: {'✅ Conectado' if self.esta_conectado else '❌ Desconectado'}")
                print("1. Enviar mensaje")
                print("2. Reconectar")
                print("3. Salir")
                
                opcion = input("\nSeleccione una opción: ").strip()
                
                if opcion == "1":
                    if not self.esta_conectado:
                        print(f"\n🔄 [{self.get_timestamp()}] Reconectando antes de enviar...")
                        if not await self.conectar():
                            continue

                    numero = input("\nNúmero (ej: 573143604303): ").strip()
                    if not numero:
                        print("❌ Debe ingresar un número")
                        continue
                    
                    print("\nEscriba el mensaje (presione Enter dos veces para enviar):")
                    lineas = []
                    while True:
                        linea = input()
                        if linea.strip() == "":
                            break
                        lineas.append(linea)
                    
                    mensaje = "\n".join(lineas)
                    if not mensaje:
                        print("❌ Debe escribir un mensaje")
                        continue

                    await self.enviar_mensaje(numero, mensaje)
                
                elif opcion == "2":
                    print(f"\n🔄 [{self.get_timestamp()}] Intentando reconexión...")
                    await self.conectar()
                    
                elif opcion == "3":
                    print(f"\n👋 [{self.get_timestamp()}] ¡Hasta luego!")
                    self.running = False
                    
                else:
                    print("\n❌ Opción no válida")
                    
            except Exception as e:
                print(f"\n❌ [{self.get_timestamp()}] Error en el menú: {str(e)}")
                print("Intente nuevamente...")
                await asyncio.sleep(1)

async def main():
    cliente = ClienteWhatsApp()
    
    def signal_handler(sig, frame):
        print(f"\n\n🛑 [{cliente.get_timestamp()}] Cerrando cliente...")
        cliente.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"\n🤖 [{cliente.get_timestamp()}] Iniciando Cliente Interactivo de WhatsApp...")
    await cliente.menu_interactivo()
    await cliente.desconectar()

if __name__ == "__main__":
    asyncio.run(main()) 