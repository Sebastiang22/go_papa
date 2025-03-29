/**
 * @fileoverview Servidor de WhatsApp con envío automático de PDF solo en evento send_message
 * @version 1.1.0
 */

require('dotenv').config();
const { default: makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const express = require('express');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const fs = require('fs');
const path = require('path');
const mysql = require('mysql2/promise');

// Configuración del servidor Express y Socket.IO
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    },
    pingTimeout: 60000,
    pingInterval: 25000,
    connectTimeout: 30000
});

// Variables globales
let globalSocket = null;
let dbPool = null;

// Ruta al archivo PDF (en la raíz del proyecto)
const pdfFilePath = path.join(__dirname, 'menu_go_papa.pdf');

/**
 * Inicializa la conexión a la base de datos
 */

/**
 * Maneja las conexiones de Socket.IO
 */
io.on('connection', (socket) => {
    console.log('🔌 Cliente conectado a Socket.IO:', socket.id);
    console.log('📊 Total clientes conectados:', io.engine.clientsCount);

    // Debug de eventos del socket
    socket.conn.on('packet', (packet) => {
        if (packet.type === 'ping') return;
        console.log(`📡 [${socket.id}] Paquete ${packet.type}:`, packet.data || '');
    });

    socket.conn.on('error', (error) => {
        console.error(`❌ [${socket.id}] Error de conexión:`, error);
    });

    // Evento para enviar mensajes de WhatsApp
    socket.on('send_message', async (data, callback) => {
        console.log(`📤 [${socket.id}] Intento de envío de mensaje:`, data);
        try {
            if (!globalSocket) {
                console.error(`❌ [${socket.id}] WhatsApp no está conectado`);
                callback({ success: false, error: 'WhatsApp no está conectado' });
                return;
            }

            const { number, message } = data;
            const formattedNumber = number.replace(/[^\d]/g, '') + '@s.whatsapp.net';
            
            console.log(`📱 [${socket.id}] Enviando mensaje a ${formattedNumber}`);
            

            // Enviar un ping antes del envío para mantener la conexión viva
            socket.emit('keep_alive');
            
            try {
                await Promise.race([
                    globalSocket.sendMessage(formattedNumber, { text: message }),
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Timeout al enviar mensaje')), 25000)
                    )
                ]);

                console.log(`✅ [${socket.id}] Mensaje enviado correctamente`);
                
                // Enviar otro ping después del envío
                socket.emit('keep_alive');
                
                callback({ success: true, message: 'Mensaje enviado correctamente' });
            } catch (error) {
                console.error(`❌ [${socket.id}] Error al enviar mensaje:`, error);
                callback({ success: false, error: error.message || 'Error al enviar mensaje' });
            }
        } catch (error) {
            console.error(`❌ [${socket.id}] Error general:`, error);
            callback({ success: false, error: error.message || 'Error general al procesar el mensaje' });
        }
    });

    // Evento para verificar estado de WhatsApp
    socket.on('check_status', (callback) => {
        console.log(`🔍 [${socket.id}] Verificando estado de WhatsApp`);
        callback({ 
            connected: !!globalSocket,
            status: globalSocket ? 'connected' : 'disconnected'
        });
    });

    // Nuevo evento para enviar PDF
    socket.on('send_pdf', async (data, callback) => {
        console.log(`📤 [${socket.id}] Intento de envío de PDF:`, data);
        try {
            if (!globalSocket) {
                console.error(`❌ [${socket.id}] WhatsApp no está conectado`);
                callback({ success: false, error: 'WhatsApp no está conectado' });
                return;
            }

            const { number } = data;
            // Corregir el formateo del número para asegurar que se incluya el número antes del dominio
            const formattedNumber = number.replace(/[^\d]/g, '') + '@s.whatsapp.net';
            
            console.log(`📱 [${socket.id}] Enviando PDF a ${formattedNumber}`);
            
            // Verificar si el archivo PDF existe
            if (!fs.existsSync(pdfFilePath)) {
                console.error(`❌ [${socket.id}] El archivo PDF no existe en la ruta: ${pdfFilePath}`);
                callback({ success: false, error: 'El archivo PDF no existe' });
                return;
            }

            // Enviar un ping antes del envío para mantener la conexión viva
            socket.emit('keep_alive');
            
            try {
                await Promise.race([
                    globalSocket.sendMessage(formattedNumber, {
                        document: { url: pdfFilePath },
                        mimetype: 'application/pdf',
                        fileName: 'menu go papa.pdf'
                    }),
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Timeout al enviar PDF')), 25000)
                    )
                ]);

                console.log(`✅ [${socket.id}] PDF enviado correctamente`);
                
                // Enviar otro ping después del envío
                socket.emit('keep_alive');
                
                callback({ success: true, message: 'PDF enviado correctamente' });
            } catch (error) {
                console.error(`❌ [${socket.id}] Error al enviar PDF:`, error);
                callback({ success: false, error: error.message || 'Error al enviar PDF' });
            }
        } catch (error) {
            console.error(`❌ [${socket.id}] Error general:`, error);
            callback({ success: false, error: error.message || 'Error general al procesar el envío de PDF' });
        }
    });

    socket.on('disconnect', (reason) => {
        console.log(`❌ [${socket.id}] Cliente desconectado. Razón:`, reason);
        console.log('📊 Total clientes conectados:', io.engine.clientsCount);
    });
});

/**
 * Conecta con WhatsApp y configura los eventos
 * @async
 */
async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    
    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,
        connectTimeoutMs: 60000,
        maxRetries: 5,
        retryDelayMs: 1000
    });

    globalSocket = sock;

    // Eventos de conexión
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        console.log('📡 Estado de conexión WhatsApp:', update);
        
        if (qr) {
            console.log('🔄 Nuevo código QR generado');
            io.emit('qr', qr);
        }

        if(connection === 'close') {
            const shouldReconnect = (lastDisconnect.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('❌ Conexión cerrada debido a:', lastDisconnect.error, 'Reconectando:', shouldReconnect);
            
            if(shouldReconnect) {
                connectToWhatsApp();
            }
            io.emit('connection_status', { status: 'disconnected' });
        } else if(connection === 'open') {
            console.log('✅ Conexión WhatsApp establecida');
            io.emit('connection_status', { status: 'connected' });
        }
    });

    // Manejo de mensajes entrantes
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        console.log('📨 Mensaje recibido:', type, messages.length);
        
        for (const message of messages) {
            if (!message.message) continue;
            if (message.key.fromMe) continue;

            // Formatear mensaje
            const newMessage = {
                from: message.key.remoteJid,
                sender: message.pushName || message.key.remoteJid.split('@')[0],
                message: message.message?.conversation || 
                        message.message?.extendedTextMessage?.text || 
                        message.message?.imageMessage?.caption ||
                        'Mensaje multimedia',
                timestamp: message.messageTimestamp * 1000 || Date.now(),
                type: Object.keys(message.message)[0]
            };
            
            console.log('📩 Nuevo mensaje:', newMessage);
            
            // Emitir evento de mensaje nuevo
            io.emit('new_message', newMessage);
        }
    });

    // Guardar credenciales 
    sock.ev.on('creds.update', saveCreds);
}

// Iniciar servidor
const PORT = process.env.PORT || 3001;
server.listen(PORT, async () => {
    console.log(`🚀 Servidor WhatsApp escuchando en http://localhost:${PORT}`);
    
    // Iniciar conexión con WhatsApp
    connectToWhatsApp();
});