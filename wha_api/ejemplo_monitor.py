#!/usr/bin/env python3
"""
Monitor simple de WhatsApp
- Muestra mensajes entrantes en tiempo real
- Permite enviar mensajes a números específicos
"""

import socketio
import asyncio
from datetime import datetime
import signal
import sys

class MonitorWhatsApp:
    def __init__(self, server_url="https://tars-whatsapp.blueriver-8537145c.westus2.azurecontainerapps.io"):
        self.sio = socketio.AsyncClient(
            reconnection=True,
            reconnection_attempts=10,
            reconnection_delay=1,
            reconnection_delay_max=5
        )
        self.server_url = server_url
        self.running = True
        self.setup_events()
        
    def setup_events(self):
        @self.sio.on('connect')
        def on_connect():
            print("\n✅ Conectado al servidor de WhatsApp")
            print("Monitoreando mensajes entrantes...\n")
            print("Presiona Ctrl+C para mostrar el menú")

        @self.sio.on('disconnect')
        async def on_disconnect():
            print("\n❌ Desconectado del servidor de WhatsApp")
            # Intentar reconectar
            if self.running:
                try:
                    await self.sio.connect(self.server_url)
                except:
                    pass

        @self.sio.on('new_message')
        def on_message(data):
            # Formatear y mostrar el mensaje recibido
            timestamp = datetime.fromtimestamp(data['timestamp']/1000).strftime('%H:%M:%S')
            print(f"\n{'='*50}")
            print(f"📱 [{timestamp}] Mensaje de {data['sender']} ({data['from'].split('@')[0]}):")
            print(f"💬 {data['message']}")
            print(f"{'='*50}")

        @self.sio.on('connection_status')
        def on_status(data):
            print(f"\n📡 Estado de WhatsApp: {data['status']}")

    async def ensure_connected(self):
        """Asegura que estamos conectados antes de realizar operaciones"""
        if not self.sio.connected:
            try:
                await self.sio.connect(self.server_url)
                await asyncio.sleep(1)  # Esperar a que la conexión se establezca
            except Exception as e:
                print(f"\n❌ Error al reconectar: {e}")
                return False
        return True

    async def connect(self):
        try:
            await self.sio.connect(self.server_url)
        except Exception as e:
            print(f"\n❌ Error al conectar: {e}")
            sys.exit(1)

    async def disconnect(self):
        if self.sio.connected:
            await self.sio.disconnect()

    async def send_message(self, number: str, message: str):
        try:
            # Asegurar conexión antes de enviar
            if not await self.ensure_connected():
                print("\n❌ Error: No se pudo establecer conexión con el servidor")
                return

            # Validar y formatear el número
            number = number.replace('+', '').replace(' ', '').replace('-', '')
            if not number.isdigit() or len(number) < 10:
                print("\n❌ Error: Número inválido. Debe contener solo dígitos y tener al menos 10 números")
                return

            print(f"\n📤 Enviando mensaje a {number}...")
            
            try:
                # Intentar enviar el mensaje con timeout
                response = await asyncio.wait_for(
                    self.sio.call('send_message', {
                        'number': number,
                        'message': message
                    }),
                    timeout=10.0
                )
                
                if response and response.get('success'):
                    print(f"✅ Mensaje enviado exitosamente a {number}")
                else:
                    error_msg = response.get('error') if response else 'No se recibió respuesta del servidor'
                    print(f"❌ Error al enviar mensaje: {error_msg}")
                
            except asyncio.TimeoutError:
                print("\n❌ Error: Tiempo de espera agotado al enviar el mensaje")
                
        except Exception as e:
            print(f"\n❌ Error al enviar mensaje: {str(e)}")
            print("📋 Detalles técnicos:", e.__class__.__name__)

    async def check_connection(self):
        """Verificar el estado de la conexión con WhatsApp"""
        try:
            # Primero verificar la conexión del socket
            if not await self.ensure_connected():
                return False

            # Luego verificar el estado de WhatsApp
            try:
                status = await asyncio.wait_for(
                    self.sio.call('check_status'),
                    timeout=5.0
                )
                return status.get('connected', False)
            except asyncio.TimeoutError:
                print("\n❌ Tiempo de espera agotado al verificar estado")
                return False
        except Exception as e:
            print(f"\n❌ Error al verificar conexión: {e}")
            return False

    async def show_menu(self):
        while True:
            print("\n🔷 Menú del Monitor 🔷")
            print("1. Enviar mensaje")
            print("2. Verificar conexión")
            print("3. Salir")
            
            try:
                opcion = input("\nSeleccione una opción: ").strip()
                
                if opcion == "1":
                    # Verificar conexión antes de enviar
                    if not await self.check_connection():
                        print("\n❌ Error: No hay conexión con WhatsApp. Verifique que el servidor esté funcionando.")
                        continue

                    numero = input("\nNúmero (ej: 573143604303): ").strip()
                    if not numero:
                        print("❌ Debe ingresar un número")
                        continue
                        
                    mensaje = input("Mensaje: ").strip()
                    if not mensaje:
                        print("❌ Debe ingresar un mensaje")
                        continue
                        
                    await self.send_message(numero, mensaje)
                    await asyncio.sleep(1)  # Esperar un momento antes de volver al monitor
                    print("\nVolviendo al modo monitor... (Ctrl+C para menú)")
                
                elif opcion == "2":
                    connected = await self.check_connection()
                    if connected:
                        print("\n✅ Conexión activa con WhatsApp")
                    else:
                        print("\n❌ No hay conexión con WhatsApp")
                    await asyncio.sleep(1)  # Esperar antes de mostrar el menú nuevamente
                    
                elif opcion == "3":
                    self.running = False
                    break
                    
                else:
                    print("\n❌ Opción no válida")
                
            except Exception as e:
                print(f"\n❌ Error en el menú: {e}")
                print("Intente nuevamente...")
                await asyncio.sleep(1)

async def main():
    # Crear instancia del monitor
    monitor = MonitorWhatsApp()
    
    # Manejar señal de interrupción (Ctrl+C)
    def signal_handler(sig, frame):
        print("\n\nMostrando menú...")
        asyncio.create_task(monitor.show_menu())
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Conectar al servidor
        await monitor.connect()
        
        # Mantener el programa corriendo
        while monitor.running:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        await monitor.disconnect()
        print("\n👋 ¡Hasta luego!")

if __name__ == "__main__":
    print("\n🤖 Iniciando Monitor de WhatsApp...")
    asyncio.run(main()) 