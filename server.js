#!/usr/bin/env node
/**
 * Gaming Day Network Monitor - Express Server
 * Features:
 * - Static file serving
 * - WebSocket for real-time updates
 * - Auto-reload on network_data.json changes
 * - REST API endpoints
 */

const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const chokidar = require('chokidar');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const PORT = process.env.PORT || 3000;
const SCAN_INTERVAL = process.env.SCAN_INTERVAL || 30000; // 30 seconds

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Store connected clients
const clients = new Set();

// WebSocket connection handling
wss.on('connection', (ws) => {
    console.log('📱 New client connected');
    clients.add(ws);
    
    // Send current data immediately
    sendNetworkData(ws);
    
    ws.on('close', () => {
        console.log('👋 Client disconnected');
        clients.delete(ws);
    });
    
    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        clients.delete(ws);
    });
});

// Broadcast to all connected clients
function broadcast(data) {
    const message = JSON.stringify(data);
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

// Send network data to client(s)
function sendNetworkData(target = null) {
    try {
        const dataPath = path.join(__dirname, 'network_data.json');
        if (fs.existsSync(dataPath)) {
            const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
            const message = {
                type: 'network_update',
                data: data,
                timestamp: new Date().toISOString()
            };
            
            if (target) {
                target.send(JSON.stringify(message));
            } else {
                broadcast(message);
            }
        }
    } catch (error) {
        console.error('Error reading network data:', error.message);
    }
}

// Watch network_data.json for changes
const watcher = chokidar.watch('network_data.json', {
    ignoreInitial: true
});

watcher.on('change', (filepath) => {
    console.log('🔄 Network data updated, broadcasting to clients...');
    sendNetworkData();
});

// REST API Endpoints

// Get current network data
app.get('/api/network', (req, res) => {
    try {
        const dataPath = path.join(__dirname, 'network_data.json');
        if (fs.existsSync(dataPath)) {
            const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
            res.json(data);
        } else {
            res.status(404).json({ error: 'Network data not found. Run scan first.' });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Trigger a new scan
app.post('/api/scan', (req, res) => {
    console.log('🔍 Manual scan triggered...');
    
    const scanProcess = spawn('python3', ['network_scanner.py']);
    
    let output = '';
    let errorOutput = '';
    
    scanProcess.stdout.on('data', (data) => {
        output += data.toString();
    });
    
    scanProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
    });
    
    scanProcess.on('close', (code) => {
        if (code === 0) {
            console.log('✅ Scan completed successfully');
            res.json({ 
                success: true, 
                message: 'Scan completed',
                output: output
            });
            // Broadcast updated data
            setTimeout(() => sendNetworkData(), 500);
        } else {
            console.error('❌ Scan failed:', errorOutput);
            res.status(500).json({ 
                success: false, 
                error: errorOutput || 'Scan failed'
            });
        }
    });
});

// Get device by IP
app.get('/api/device/:ip', (req, res) => {
    try {
        const dataPath = path.join(__dirname, 'network_data.json');
        if (fs.existsSync(dataPath)) {
            const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
            const device = data.devices[req.params.ip];
            
            if (device) {
                res.json(device);
            } else {
                res.status(404).json({ error: 'Device not found' });
            }
        } else {
            res.status(404).json({ error: 'Network data not found' });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get summary statistics
app.get('/api/stats', (req, res) => {
    try {
        const dataPath = path.join(__dirname, 'network_data.json');
        if (fs.existsSync(dataPath)) {
            const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
            res.json({
                total_devices: data.total_devices,
                summary: data.summary,
                last_scan: data.timestamp
            });
        } else {
            res.status(404).json({ error: 'Network data not found' });
        }
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        uptime: process.uptime(),
        connected_clients: clients.size,
        timestamp: new Date().toISOString()
    });
});

// Auto-scan function
let scanTimer = null;

function startAutoScan() {
    console.log(`⏱️  Auto-scan enabled: every ${SCAN_INTERVAL/1000}s`);
    
    // Initial scan
    runScan();
    
    // Periodic scans
    scanTimer = setInterval(runScan, SCAN_INTERVAL);
}

function runScan() {
    console.log('🔍 Running automated scan...');
    
    const scanProcess = spawn('python3', ['network_scanner.py']);
    
    scanProcess.on('close', (code) => {
        if (code === 0) {
            console.log('✅ Auto-scan completed');
        } else {
            console.error('❌ Auto-scan failed');
        }
    });
}

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('👋 Shutting down gracefully...');
    if (scanTimer) clearInterval(scanTimer);
    watcher.close();
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

// Start server
server.listen(PORT, () => {
    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║   🎮 GAMING DAY NETWORK MONITOR - Server Started      ║');
    console.log('╚════════════════════════════════════════════════════════╝');
    console.log('');
    console.log(`📊 Dashboard:  http://localhost:${PORT}`);
    console.log(`🔌 WebSocket:  ws://localhost:${PORT}`);
    console.log(`🌐 API:        http://localhost:${PORT}/api/`);
    console.log('');
    console.log('📡 API Endpoints:');
    console.log('   GET  /api/network     - Get all network data');
    console.log('   GET  /api/device/:ip  - Get specific device');
    console.log('   GET  /api/stats       - Get summary statistics');
    console.log('   POST /api/scan        - Trigger manual scan');
    console.log('   GET  /api/health      - Server health check');
    console.log('');
    console.log(`👥 Connected clients: ${clients.size}`);
    console.log('');
    console.log('Press Ctrl+C to stop');
    console.log('');
    
    // Start auto-scanning if enabled
    if (process.env.AUTO_SCAN !== 'false') {
        startAutoScan();
    } else {
        console.log('ℹ️  Auto-scan disabled. Use POST /api/scan to scan manually.');
    }
});
