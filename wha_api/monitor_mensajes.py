#!/usr/bin/env python3
"""
Monitor simple de mensajes de WhatsApp
Solo muestra los mensajes entrantes en tiempo real
"""

import socketio
import asyncio
from datetime import datetime
import signal
import sys

class MonitorMensajes:
    def __init__(self, server_url="http://localhost:3000"):
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.running = True
        
    def setup_events(self):
        @self.sio.on('connect')
        def on_connect():
            print("\n✅ Conectado al servidor de WhatsApp")
            print("Monitoreando mensajes entrantes...")
            print("\nPresiona Ctrl+C para salir")

        @self.sio.on('disconnect')
        def on_disconnect():
            print("\n❌ Desconectado del servidor de WhatsApp")

        @self.sio.on('new_message')
        def on_message(data):
            timestamp = datetime.fromtimestamp(data['timestamp']/1000).strftime('%H:%M:%S')
            print(f"\n{'='*50}")
            print(f"📱 [{timestamp}] Mensaje de {data['sender']}")
            print(f"📞 Número: {data['from'].split('@')[0]}")
            print(f"💬 Mensaje: {data['message']}")
            print(f"{'='*50}")

    async def start(self):
        self.setup_events()
        try:
            await self.sio.connect(self.server_url)
            while self.running:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            if self.sio.connected:
                await self.sio.disconnect()

def main():
    monitor = MonitorMensajes()
    
    def signal_handler(sig, frame):
        print("\n\nDeteniendo monitor...")
        monitor.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n🤖 Iniciando Monitor de Mensajes WhatsApp...")
    asyncio.run(monitor.start())
    print("\n👋 ¡Hasta luego!")

if __name__ == "__main__":
    main() 