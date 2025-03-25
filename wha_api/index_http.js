require('dotenv').config();
const { default: makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const axios = require('axios'); // Se utiliza para hacer solicitudes HTTP
const http = require('http');
const { Server } = require('socket.io');

// Configuración de Express y middleware
const app = express();
app.use(cors());
app.use(express.json());

// Crear servidor HTTP y configurar Socket.IO
const PORT = process.env.PORT || 3000;
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

let globalSocket = null;
const pdfFilePath = path.join(__dirname, 'menu_go_papa.pdf');

// Array global para almacenar mensajes entrantes (opcional)
let newMessages = [];

/**
 * Función para conectar a WhatsApp usando baileys
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

    // Manejo de actualización de conexión
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        console.log('📡 Estado de conexión WhatsApp:', update);

        if (qr) {
            console.log('🔄 Se generó un nuevo código QR');
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('❌ Conexión cerrada:', lastDisconnect.error, 'Reconectando:', shouldReconnect);
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('✅ Conexión WhatsApp establecida');
        }
    });

    // Guarda las credenciales cuando se actualicen
    sock.ev.on('creds.update', saveCreds);

    // Evento para recibir mensajes entrantes
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        console.log('📨 Mensaje recibido:', type, messages.length);
    
        for (const message of messages) {
            if (!message.message) continue;
            if (message.key.fromMe) continue; // Omitir mensajes enviados por este cliente

            // Extraer el texto del mensaje (puede provenir de distintas propiedades)
            const queryText = message.message.conversation || 
                              message.message.extendedTextMessage?.text || 
                              message.message.imageMessage?.caption ||
                              'Mensaje multimedia';

            // Formatear el mensaje recibido
            const newMessage = {
                from: message.key.remoteJid,
                sender: message.pushName || message.key.remoteJid.split('@')[0],
                message: queryText,
                timestamp: (message.messageTimestamp * 1000) || Date.now(),
                type: Object.keys(message.message)[0]
            };
            
            console.log('📩 Nuevo mensaje:', newMessage);
            
            // Almacenar el mensaje en un array global (opcional)
            newMessages.push(newMessage);
            
            // Preparar el payload para la solicitud HTTP
            const payload = {
                user_id: message.key.remoteJid.split('@')[0],
                conversation_id: message.key.remoteJid,
                conversation_name: message.pushName || message.key.remoteJid.split('@')[0],
                query: queryText,
                restaurant_name: "go_papa"
            };

            // Realizar la solicitud POST a http://localhost:8000/api/agent/chat/message
            try {
                // const response = await axios.post('http://localhost:8000/api/agent/chat/message', payload);
                const response = await axios.post('https://ca-gopapa-backend.blueriver-8537145c.westus2.azurecontainerapps.io/api/agent/chat/message', payload);
                console.log('✅ Respuesta de API agent/chat/message:', response.data);
                // Asumimos que la respuesta contiene un campo 'text' con la respuesta a enviar
                const replyText = (response.data.text || 'Estamos experimentando problemas, por favor intente más tarde').replace(/\*\*/g, '*');
                // Enviar la respuesta de vuelta al mismo número de WhatsApp
                await globalSocket.sendMessage(message.key.remoteJid, { text: replyText });
                console.log(`📤 Respuesta enviada a ${message.key.remoteJid}`);
            } catch (error) {
                console.error('❌ Error al realizar POST a /api/agent/chat/message:', error.message);
            }
        }
    });
}

/**
 * Manejo de conexiones Socket.IO
 */
io.on('connection', (socket) => {
    console.log(`🔌 Cliente conectado a Socket.IO: ${socket.id}`);

    // Evento para enviar PDF vía socket, manteniendo la misma lógica original
    socket.on('send_pdf', async (data, callback) => {
        console.log(`📤 [${socket.id}] Intento de envío de PDF:`, data);
        try {
            if (!globalSocket) {
                console.error(`❌ [${socket.id}] WhatsApp no está conectado`);
                callback({ success: false, error: 'WhatsApp no está conectado' });
                return;
            }

            const { number } = data;
            // Formatear el número para incluir el dominio de WhatsApp
            const formattedNumber = number.replace(/[^\d]/g, '') + '@s.whatsapp.net';
            console.log(`📱 [${socket.id}] Enviando PDF a ${formattedNumber}`);

            // Verificar si el archivo PDF existe
            if (!fs.existsSync(pdfFilePath)) {
                console.error(`❌ [${socket.id}] El archivo PDF no existe en la ruta: ${pdfFilePath}`);
                callback({ success: false, error: 'El archivo PDF no existe' });
                return;
            }

            // Enviar un "ping" para mantener la conexión (emulado con socket.emit)
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
                // Enviar otro "ping" después del envío
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
});

/**
 * Endpoint para enviar mensaje de texto vía WhatsApp
 * (Este endpoint se conserva para otros usos, pero el envío de PDF se maneja vía socket)
 */
app.post('/api/send-message', async (req, res) => {
    try {
        const { number, message } = req.body;
        if (!globalSocket) {
            return res.status(500).json({ success: false, error: 'WhatsApp no está conectado' });
        }
        if (!number || !message) {
            return res.status(400).json({ success: false, error: 'Faltan datos: number o message' });
        }
        const formattedNumber = number.replace(/[^\d]/g, '') + '@s.whatsapp.net';
        console.log(`📱 Enviando mensaje a ${formattedNumber}`);

        try {
            await Promise.race([
                globalSocket.sendMessage(formattedNumber, { text: message }),
                new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout al enviar mensaje')), 25000))
            ]);
            return res.json({ success: true, message: 'Mensaje enviado correctamente' });
        } catch (error) {
            return res.status(500).json({ success: false, error: error.message || 'Error al enviar mensaje' });
        }
    } catch (error) {
        return res.status(500).json({ success: false, error: error.message || 'Error general' });
    }
});

/**
 * Endpoint para consultar el estado de conexión de WhatsApp
 */
app.get('/api/status', (req, res) => {
    const connected = !!globalSocket;
    res.json({ connected, status: connected ? 'connected' : 'disconnected' });
});

/**
 * Endpoint para obtener los mensajes entrantes de WhatsApp (opcional)
 */
app.get('/api/messages', (req, res) => {
    res.json({ messages: newMessages });
});

// Inicia el servidor y conecta a WhatsApp
server.listen(PORT, async () => {
    console.log(`🚀 Servidor escuchando en http://localhost:${PORT}`);
    await connectToWhatsApp();
});
