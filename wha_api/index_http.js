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
const PORT = process.env.PORT || 3001;
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

let globalSocket = null;
const pdfFilePath = path.join(__dirname, 'MenuGopapa.pdf');

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
                const response = await axios.post('http://127.0.0.1:8000/agent/chat/message', payload);
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
 * Envía las 5 imágenes de la carpeta @common al número proporcionado
 * @param {Object} req - Objeto de solicitud HTTP
 * @param {Object} res - Objeto de respuesta HTTP
 */
app.post('/api/send-images', async (req, res) => {
    try {
        const { phone } = req.body;
        
        if (!phone) {
            return res.status(400).json({ 
                status: false, 
                message: 'El número de teléfono es obligatorio' 
            });
        }
        
        // Ruta a la carpeta @common
        const commonFolderPath = path.join(__dirname, 'common');
        
        // Verificar si la carpeta existe
        if (!fs.existsSync(commonFolderPath)) {
            return res.status(404).json({ 
                status: false, 
                message: 'La carpeta common no existe' 
            });
        }
        
        // Obtener todas las imágenes de la carpeta
        const files = fs.readdirSync(commonFolderPath)
            .filter(file => {
                const ext = path.extname(file).toLowerCase();
                return ['.jpg', '.jpeg', '.png', '.gif'].includes(ext);
            });
        
        // Verificar si hay imágenes
        if (files.length === 0) {
            return res.status(404).json({ 
                status: false, 
                message: 'No se encontraron imágenes en la carpeta common' 
            });
        }
        
        // Limitar a 5 imágenes
        const imagesToSend = files.slice(0, 5);
        const results = [];
        
        // Enviar cada imagen
        for (const file of imagesToSend) {
            const filePath = path.join(commonFolderPath, file);
            const result = await globalSocket.sendMessage(phone + '@c.us', {
                image: { url: filePath },
                caption: '' // Quitado el mensaje con el nombre del archivo
            });
            results.push(result);
            
            // Pequeña pausa entre envíos para evitar problemas
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        res.status(200).json({
            status: true,
            message: `Se enviaron ${imagesToSend.length} imágenes correctamente`,
            data: {
                images_sent: imagesToSend,
                results: results
            }
        });
    } catch (error) {
        console.error('Error al enviar imágenes:', error);
        res.status(500).json({
            status: false,
            message: 'Error al enviar imágenes',
            error: error.message
        });
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
