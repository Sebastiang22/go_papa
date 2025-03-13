#!/usr/bin/env python3
import asyncio
from cliente_whatsapp import ClienteWhatsApp
import signal
import sys

async def main():
    cliente = None  # Initialize cliente variable outside try block
    while True:  # Bucle principal para reiniciar el servicio
        try:
            cliente = ClienteWhatsApp()

            if not await cliente.conectar():
                print("No se pudo conectar al servidor, reintentando en 5 segundos...")
                await asyncio.sleep(5)
                continue


            print("Esperando mensajes entrantes. Presiona Ctrl+C para salir...")
            while True:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\nCerrando conexión...")
            if cliente:  # Check if cliente exists before calling desconectar
                await cliente.desconectar()
            break  # Salir completamente del programa
        except Exception as e:
            print(f"Error inesperado: {e}")
            print("Reiniciando el servicio en 5 segundos...")
            await asyncio.sleep(5)
        finally:
            if cliente:  # Check if cliente exists before calling desconectar
                try:
                    await cliente.desconectar()
                except:
                    pass

def signal_handler(signum, frame):
    print("\nSeñal recibida, cerrando el servicio...")
    sys.exit(0)

if __name__ == "__main__":
    # Registrar manejadores de señales
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Ejecutar el loop principal
    asyncio.run(main())
