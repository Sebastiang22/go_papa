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
const pdfFilePath = path.join(__dirname, 'plantilla_creditos.pdf');

/**
 * Inicializa la conexión a la base de datos
 */
async function initializeDatabase() {
    try {
        dbPool = await mysql.createPool({
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            password: process.env.DB_PASSWORD,
            database: process.env.DB_DATABASE,
            waitForConnections: true,
            connectionLimit: 10,
            queueLimit: 0,
            ssl: {
                rejectUnauthorized: true
            }
        });
        
        console.log('✅ Conexión a la base de datos establecida');
    } catch (error) {
        console.error('❌ Error al conectar con la base de datos:', error);
        process.exit(1);
    }
}

/**
 * Obtiene la última conversación de un usuario
 * @param {string} userId - ID del usuario (número de teléfono)
 * @returns {Object|null} - Última conversación o null si no existe
 */
async function getLastConversation(userId) {
    try {
        const [rows] = await dbPool.execute(
            'SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
            [userId]
        );
        
        return rows.length > 0 ? rows[0] : null;
    } catch (error) {
        console.error('❌ Error al consultar la última conversación:', error);
        return null;
    }
}

/**
 * Verifica si debe enviarse el PDF automáticamente
 * @param {string} userId - ID del usuario (número de teléfono)
 * @returns {boolean} - true si debe enviarse el PDF
 */
async function shouldSendPdf(userId) {
    const lastConversation = await getLastConversation(userId);
    console.log(`📊 Última conversación para ${userId}:`, lastConversation);
    // Si no hay conversación previa, enviar PDF
    if (!lastConversation) {
        console.log(`📊 No hay conversaciones previas para ${userId}, enviando PDF`);
        return true;
    }
    
    // Verificar si ha pasado más de un día desde la última conversación
    const lastUpdated = new Date(lastConversation.updated_at);
    const currentDate = new Date();
    const diffTime = Math.abs(currentDate - lastUpdated);
    const diffDays = diffTime / (1000 * 60 * 60 * 24);
    
    console.log(`📊 Días desde última conversación con ${userId}: ${diffDays.toFixed(2)}`);
    
    return diffDays >= 1;
}

/**
 * Envía un PDF al usuario
 * @param {string} userId - ID del usuario con formato @s.whatsapp.net
 * @returns {Promise<boolean>} - true si se envió correctamente
 */
async function sendPdfToUser(userId) {
    try {
        if (!globalSocket) {
            console.error('❌ WhatsApp no está conectado para enviar PDF');
            return false;
        }
        
        // Verificar que el archivo exista
        if (!fs.existsSync(pdfFilePath)) {
            console.error('❌ El archivo PDF no existe en:', pdfFilePath);
            return false;
        }
        
        // Leer el archivo PDF
        const pdfBuffer = fs.readFileSync(pdfFilePath);
        
        // Enviar el documento
        await globalSocket.sendMessage(userId, {
            document: pdfBuffer,
            fileName: 'menu.pdf',
            mimetype: 'application/pdf',
            caption: 'MENU.'
        });
        
        console.log(`✅ PDF enviado correctamente a ${userId}`);
        return true;
    } catch (error) {
        console.error('❌ Error al enviar PDF:', error);
        return false;
    }
}

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
            
            // Verificar si se debe enviar el PDF automáticamente
            const shouldSendPdfToUser = await shouldSendPdf(number);
            console.log(`🚀 Enviando PDF automático para ${number}: ${shouldSendPdfToUser}`);
            // Solo enviar el PDF en el evento send_message
            if (shouldSendPdfToUser) {
                console.log(`📎 [${socket.id}] Enviando PDF automático a ${formattedNumber}`);
                try {
                    // Primero enviar el PDF
                    await sendPdfToUser(formattedNumber);
                    console.log(`✅ [${socket.id}] PDF enviado correctamente, procediendo con mensaje de texto`);
                } catch (pdfError) {
                    console.error(`❌ [${socket.id}] Error al enviar PDF:`, pdfError);
                    // Continuar con el envío del mensaje de texto aunque falle el PDF
                }
            }
            
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
const PORT = process.env.PORT || 3000;
server.listen(PORT, async () => {
    console.log(`🚀 Servidor WhatsApp escuchando en http://localhost:${PORT}`);
    
    // Inicializar la base de datos
    await initializeDatabase();
    
    // Iniciar conexión con WhatsApp
    connectToWhatsApp();
});