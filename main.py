# Author: Gitee Volkath@amazoncloud
# Program: PyWebPlayback ver 1.0.1 Build 2024.12.29
# Repository: https://gitee.com/amazoncloud/py-web-playback.git

from flask import Flask, request, jsonify, render_template_string
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pythoncom
import win32api
import win32con
import webbrowser
from os import _exit as quit_completely, makedirs, path
import threading
import time
import json
from os.path import expanduser
import logging
from logging.handlers import RotatingFileHandler
import queue

app = Flask(__name__)

# Set up logging
log_dir = path.join(expanduser('~'), 'documents', 'logs')
makedirs(log_dir, exist_ok=True)

# Access log
access_log = path.join(log_dir, 'access.log')
access_handler = RotatingFileHandler(access_log, maxBytes=100*1024*1024, backupCount=5)  # 100MB limit
access_handler.setLevel(logging.INFO)
access_formatter = logging.Formatter('%(asctime)s - %(message)s')
access_handler.setFormatter(access_formatter)

# Error log  
error_log = path.join(log_dir, 'error.log')
error_handler = RotatingFileHandler(error_log, maxBytes=100*1024*1024, backupCount=5)  # 100MB limit
error_handler.setLevel(logging.WARNING)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)

app.logger.addHandler(access_handler)
app.logger.addHandler(error_handler)
app.logger.setLevel(logging.INFO)

# Queue for real-time logs
log_queue = queue.Queue(maxsize=100)

# Load config from JSON
config_dir = path.join(expanduser('~'), 'documents', 'config')
config_file = path.join(config_dir, 'PyWebPlayback.json')

# Create config directory if not exists
makedirs(config_dir, exist_ok=True)

# Default config
default_config = {
    "baseport": 80,
    "listenaddress": "0.0.0.0",
    "debug": False
}

# Load or create config file
if path.exists(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
else:
    config = default_config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

baseport = config['baseport']
version = 'PyWebPlayback ver 1.0.1 Build 2024.12.30'
service_link = f"http://localhost:{baseport}/"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyWebPlayback Control Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: rgba(82, 108, 235, 0.9);
            --accent-color: rgba(255, 255, 255, 0.9);
            --text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Noto Sans', sans-serif;
            min-height: 100vh;
            background: linear-gradient(45deg, #ff0000, #00ff00);
            background-size: 400% 400%;
            color: white;
            transition: background 2s ease;
            animation: gradientAnimation 10s ease infinite;
        }

        @keyframes gradientAnimation {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(10px);
        }

        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .title {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: var(--text-shadow);
            color: var(--accent-color);
        }

        .version {
            font-size: 1rem;
            color: #aaa;
        }

        .control-panel {
            background: rgba(0, 0, 0, 0.5);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        .playback-controls {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .control-button {
            background: var(--primary-color);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            color: white;
            font-size: 1.5rem;
            transition: all 0.3s ease;
        }

        .control-button:hover {
            transform: scale(1.1);
            background: rgba(82, 108, 235, 1);
        }

        .volume-control {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .volume-slider {
            flex: 1;
            -webkit-appearance: none;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            outline: none;
        }

        .volume-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            background: var(--primary-color);
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .volume-slider::-webkit-slider-thumb:hover {
            transform: scale(1.2);
        }

        .volume-value {
            min-width: 60px;
            text-align: center;
            font-size: 1.2rem;
            color: var(--accent-color);
        }

        .log-container {
            margin-top: 2rem;
            background: rgba(0, 0, 0, 0.3);
            padding: 1rem;
            border-radius: 10px;
            height: 300px;
            overflow-y: auto;
        }

        .log-entry {
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            border-radius: 5px;
            font-family: monospace;
        }

        .log-info {
            background: rgba(82, 108, 235, 0.2);
        }

        .log-error {
            background: rgba(235, 82, 82, 0.2);
        }

        .shortcut-controls {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin: 2rem 0;
        }

        .shortcut-button {
            background: var(--primary-color);
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .shortcut-button:hover {
            transform: scale(1.05);
            background: rgba(82, 108, 235, 1);
        }

        .system-controls {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
        }

        .system-button {
            background: #dc3545;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .system-button:hover {
            transform: scale(1.05);
            background: #c82333;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">PyWebPlayback for WindowsControl Panel</h1>
            <div class="version">{{ version }}</div>
        </div>

        <div class="control-panel">
            <div class="playback-controls">
                <button class="control-button" id="prevButton">⏮</button>
                <button class="control-button" id="playPauseButton">⏯</button>
                <button class="control-button" id="nextButton">⏭</button>
            </div>
            <div class="volume-control">
                <button class="control-button" id="muteButton">🔊</button>
                <input type="range" class="volume-slider" min="0" max="100" value="50">
                <div class="volume-value">50%</div>
            </div>

            <div class="shortcut-controls">
                <button class="shortcut-button" id="alt1Button">Alt+1</button>
                <button class="shortcut-button" id="alt2Button">Alt+2</button>
                <button class="shortcut-button" id="alt3Button">Alt+3</button>
                <button class="shortcut-button" id="ctrlAltLButton">Ctrl+Alt+L</button>
                <button class="shortcut-button" id="altQButton">Alt+Q</button>
            </div>

            <div class="system-controls">
                <button class="system-button" id="shutdownButton">Shutdown Service</button>
            </div>

            <div class="log-container"></div>
        </div>
    </div>

    <script>
        // Dynamic color background
        function getRandomColor() {
            return `#${Math.floor(Math.random()*16777215).toString(16)}`;
        }

        function updateBackground() {
            const color1 = getRandomColor();
            const color2 = getRandomColor();
            const color3 = getRandomColor();
            const angle = Math.floor(Math.random() * 360);
            document.body.style.background = `linear-gradient(${angle}deg, ${color1}, ${color2}, ${color3})`;
        }

        // Initial background
        updateBackground();
        // Change background every 10 seconds
        setInterval(updateBackground, 10000);

        // Playback controls
        const playPauseButton = document.getElementById('playPauseButton');
        const prevButton = document.getElementById('prevButton');
        const nextButton = document.getElementById('nextButton');
        const muteButton = document.getElementById('muteButton');
        const volumeSlider = document.querySelector('.volume-slider');
        const volumeValue = document.querySelector('.volume-value');
        const logContainer = document.querySelector('.log-container');

        // Shortcut buttons
        const alt1Button = document.getElementById('alt1Button');
        const alt2Button = document.getElementById('alt2Button');
        const alt3Button = document.getElementById('alt3Button');
        const ctrlAltLButton = document.getElementById('ctrlAltLButton');
        const altQButton = document.getElementById('altQButton');
        const shutdownButton = document.getElementById('shutdownButton');

        let isPlaying = false;
        let isMuted = false;

        // Shortcut handlers
        async function sendShortcut(shortcut) {
            try {
                const response = await fetch('/shortcut', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({shortcut: shortcut})
                });
                const data = await response.json();
                if (data.status !== 'success') {
                    console.error('Error sending shortcut:', data.message);
                }
            } catch (error) {
                console.error('Error sending shortcut:', error);
            }
        }

        alt1Button.addEventListener('click', () => sendShortcut('alt1'));
        alt2Button.addEventListener('click', () => sendShortcut('alt2'));
        alt3Button.addEventListener('click', () => sendShortcut('alt3'));
        ctrlAltLButton.addEventListener('click', () => sendShortcut('ctrlaltl'));
        altQButton.addEventListener('click', () => sendShortcut('altq'));

        shutdownButton.addEventListener('click', async () => {
            if (confirm('Are you sure you want to shutdown the service?')) {
                try {
                    await fetch('/shutdown', { method: 'POST' });
                } catch (error) {
                    console.error('Error shutting down service:', error);
                }
            }
        });

        playPauseButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/playback', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({action: 'playpause'})
                });
                const data = await response.json();
                if (data.status === 'success') {
                    isPlaying = !isPlaying;
                    playPauseButton.textContent = isPlaying ? '⏸' : '▶';
                }
            } catch (error) {
                console.error('Error toggling playback:', error);
            }
        });

        prevButton.addEventListener('click', async () => {
            try {
                await fetch('/playback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({action: 'previous'})
                });
            } catch (error) {
                console.error('Error changing to previous track:', error);
            }
        });

        nextButton.addEventListener('click', async () => {
            try {
                await fetch('/playback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({action: 'next'})
                });
            } catch (error) {
                console.error('Error changing to next track:', error);
            }
        });

        muteButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/volume', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({volume: isMuted ? volumeSlider.value : 0})
                });

                const data = await response.json();
                if (data.status === 'success') {
                    isMuted = !isMuted;
                    muteButton.textContent = isMuted ? '🔇' : '🔊';
                }
            } catch (error) {
                console.error('Error toggling mute:', error);
            }
        });

        async function updateVolume() {
            try {
                const response = await fetch('/get_volume');
                const data = await response.json();
                if (data.status === 'success') {
                    volumeSlider.value = data.volume;
                    volumeValue.textContent = `${data.volume}%`;
                }
            } catch (error) {
                console.error('Error fetching volume:', error);
            }
        }

        // Update volume display
        volumeSlider.addEventListener('input', async () => {
            volumeValue.textContent = `${volumeSlider.value}%`;
            try {
                await fetch('/volume', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ volume: parseInt(volumeSlider.value) })
                });
            } catch (error) {
                console.error('Error setting volume:', error);
            }
        });

        // Real-time logs
        async function fetchLogs() {
            try {
                const response = await fetch('/logs');
                const logs = await response.json();
                
                logs.forEach(log => {
                    const logEntry = document.createElement('div');
                    logEntry.className = `log-entry log-${log.type}`;
                    logEntry.textContent = log.message;
                    logContainer.appendChild(logEntry);
                    
                    // Auto-scroll to bottom
                    logContainer.scrollTop = logContainer.scrollHeight;
                    
                    // Keep only last 100 entries
                    while (logContainer.children.length > 100) {
                        logContainer.removeChild(logContainer.firstChild);
                    }
                });
            } catch (error) {
                console.error('Error fetching logs:', error);
            }
        }

        // Initial volume
        updateVolume();
        // Update volume every 2 seconds
        setInterval(updateVolume, 2000);
        // Fetch logs every second
        setInterval(fetchLogs, 1000);
    </script>
</body>
</html>
'''

@app.route('/logs')
def get_logs():
    logs = []
    while not log_queue.empty():
        try:
            logs.append(log_queue.get_nowait())
        except queue.Empty:
            break
    return jsonify(logs)

class QueueHandler(logging.Handler):
    def emit(self, record):
        client_ip = request.remote_addr if request else 'Unknown IP'
        user_agent = request.headers.get('User-Agent', 'Unknown UA') if request else 'Unknown UA'
        log_entry = {
            'message': f'[{client_ip}] [{user_agent}] {self.format(record)}',
            'type': record.levelname.lower()
        }
        try:
            log_queue.put_nowait(log_entry)
        except queue.Full:
            pass

queue_handler = QueueHandler()
queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
app.logger.addHandler(queue_handler)

@app.route('/')
def home():
    app.logger.info('Home page accessed')
    return render_template_string(HTML_TEMPLATE, version=version)

@app.route('/get_volume')
def get_volume():
    app.logger.info('Volume requested')
    pythoncom.CoInitialize()
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = round(volume_interface.GetMasterVolumeLevelScalar() * 100)
        return jsonify({'status': 'success', 'volume': current_volume})
    except Exception as e:
        app.logger.error(f'Error getting volume: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        pythoncom.CoUninitialize()

@app.route('/volume', methods=['POST'])
def set_volume():
    data = request.json
    volume = data.get('volume', 0)
    app.logger.info(f'Volume set to {volume}')
    
    pythoncom.CoInitialize()
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        volume_interface.SetMasterVolumeLevelScalar(volume/100, None)
        return jsonify({'status': 'success'})
    except Exception as e:
        app.logger.error(f'Error setting volume: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        pythoncom.CoUninitialize()

@app.route('/playback', methods=['POST'])
def control_playback():
    data = request.json
    action = data.get('action', '')
    app.logger.info(f'Playback control: {action}')
    
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    
    try:
        if action == 'playpause':
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif action == 'next':
            win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0)
            win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif action == 'previous':
            win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, 0, 0)
            win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)
            
        return jsonify({'status': 'success'})
    except Exception as e:
        app.logger.error(f'Error controlling playback: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/shortcut', methods=['POST'])
def send_shortcut():
    data = request.json
    shortcut = data.get('shortcut', '')
    app.logger.info(f'Shortcut requested: {shortcut}')
    
    try:
        if shortcut == 'alt1':
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # Alt down
            win32api.keybd_event(ord('1'), 0, 0, 0)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif shortcut == 'alt2':
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32api.keybd_event(ord('2'), 0, 0, 0)
            win32api.keybd_event(ord('2'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif shortcut == 'alt3':
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32api.keybd_event(ord('3'), 0, 0, 0)
            win32api.keybd_event(ord('3'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif shortcut == 'ctrlaltl':
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Ctrl down
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)     # Alt down
            win32api.keybd_event(ord('L'), 0, 0, 0)
            win32api.keybd_event(ord('L'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif shortcut == 'altq':
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32api.keybd_event(ord('Q'), 0, 0, 0)
            win32api.keybd_event(ord('Q'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            
        return jsonify({'status': 'success'})
    except Exception as e:
        app.logger.error(f'Error sending shortcut: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/shutdown', methods=['POST'])
def shutdown():
    app.logger.info('Shutdown requested')
    def shutdown_server():
        time.sleep(1)
        app.logger.info('Server shutting down')
        quit_completely(0)
    
    thread = threading.Thread(target=shutdown_server)
    thread.start()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.logger.info(f'Starting server at {service_link}')
    webbrowser.open(service_link)
    app.run(host=config['listenaddress'], port=baseport, debug=config['debug'])
    quit_completely(0)