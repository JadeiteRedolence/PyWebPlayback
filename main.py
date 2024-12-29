# Author: Gitee Volkath@amazoncloud
# Program: PyWebPlayback ver 1.0.0 Build 2024.12.29

from flask import Flask, request, jsonify, render_template_string
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pythoncom
import win32api
import win32con
import webbrowser


app = Flask(__name__)

baseport = 80
version = 'PyWebPlayback ver 1.0.0 Build 2024.12.29'
service_link = f"http://localhost:{baseport}/"

# HTML template with a modern Apple-style UI
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>'''+version+'''</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            min-height: 100vh;
            margin: 0;
            background: #0d1117;
            color: #c9d1d9;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        #background-gradient {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.8;
        }

        .container {
            position: relative;
            z-index: 1;
            width: min(90%, 450px);
            padding: clamp(1rem, 5vw, 3rem);
            background: #161b22;
            border-radius: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid #30363d;
        }

        h1 {
            font-size: clamp(1.5rem, 5vw, 2rem);
            font-weight: 700;
            text-align: center;
            margin-bottom: 2rem;
            color: #c9d1d9;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        .slider-container {
            margin: 2rem 0;
        }

        .slider {
            -webkit-appearance: none;
            width: 100%;
            height: 6px;
            background: #30363d;
            border-radius: 3px;
            outline: none;
        }

        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 28px;
            height: 28px;
            background: #58a6ff;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }

        .slider::-webkit-slider-thumb:hover {
            transform: scale(1.1);
        }

        .volume-value {
            text-align: center;
            font-size: 1.1rem;
            color: #c9d1d9;
            margin: 1rem 0;
            font-weight: 500;
        }

        .controls {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: clamp(0.5rem, 3vw, 1.5rem);
            margin-top: 2rem;
        }

        button {
            background: #21262d;
            border: 1px solid #30363d;
            color: #c9d1d9;
            padding: clamp(0.8rem, 3vw, 1.2rem);
            border-radius: 20px;
            font-size: clamp(0.9rem, 2.5vw, 1rem);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
        }

        button:hover {
            background: #30363d;
            transform: translateY(-2px);
        }

        button:active {
            transform: translateY(1px);
        }

        .notification {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(-100%);
            background: #161b22;
            color: #c9d1d9;
            padding: 1rem 2rem;
            border-radius: 12px;
            opacity: 0;
            transition: all 0.3s;
            z-index: 1000;
            border: 1px solid #30363d;
        }

        .notification.show {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }

        @media (max-width: 480px) {
            .container {
                width: 95%;
                padding: 1.5rem;
            }
            
            .controls {
                gap: 0.5rem;
            }
            
            button {
                padding: 0.8rem;
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Media Control</h1>
        <div class="slider-container">
            <input type="range" min="0" max="100" value="50" class="slider" id="volumeSlider">
            <div class="volume-value">Volume: <span id="volumeValue">50</span>%</div>
        </div>
        
        <div class="controls">
            <button id="previousBtn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
                </svg>
            </button>
            <button id="playPauseBtn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                </svg>
            </button>
            <button id="nextBtn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
                </svg>
            </button>
        </div>
    </div>

    <div class="notification" id="notification"></div>

    <script>
        const slider = document.getElementById('volumeSlider');
        const volumeValue = document.getElementById('volumeValue');
        const notification = document.getElementById('notification');
        let volumeTimeout;

        function showNotification(message) {
            notification.textContent = message;
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
            }, 2000);
        }

        slider.addEventListener('input', (e) => {
            volumeValue.textContent = e.target.value;
            clearTimeout(volumeTimeout);
            volumeTimeout = setTimeout(() => {
                fetch('/volume', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({volume: parseInt(e.target.value)})
                })
                .then(response => response.json())
                .then(data => {
                    if(data.status === 'success') {
                        showNotification('Volume updated');
                    }
                })
                .catch(() => showNotification('Failed to update volume'));
            }, 100);
        });

        document.getElementById('previousBtn').addEventListener('click', () => {
            controlPlayback('previous');
        });
        
        document.getElementById('playPauseBtn').addEventListener('click', () => {
            controlPlayback('playpause');
        });
        
        document.getElementById('nextBtn').addEventListener('click', () => {
            controlPlayback('next');
        });

        function controlPlayback(action) {
            fetch('/playback', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action})
            })
            .then(response => response.json())
            .then(data => {
                if(data.status === 'success') {
                    showNotification(action.charAt(0).toUpperCase() + action.slice(1));
                }
            })
            .catch(() => showNotification('Failed to control playback'));
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/volume', methods=['POST'])
def set_volume():
    data = request.json
    volume = data.get('volume', 0)
    
    # Initialize COM library
    pythoncom.CoInitialize()
    try:
        # Get default audio device using pycaw
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Set volume (value between 0.0 and 1.0)
        volume_interface.SetMasterVolumeLevelScalar(volume/100, None)
        
        return jsonify({'status': 'success'})
    finally:
        # Uninitialize COM library
        pythoncom.CoUninitialize()

@app.route('/playback', methods=['POST'])
def control_playback():
    data = request.json
    action = data.get('action', '')
    
    # Media control key codes
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
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    webbrowser.open(service_link)
    app.run(host='0.0.0.0', port=baseport, debug=False)