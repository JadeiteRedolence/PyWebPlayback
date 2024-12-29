# PyWebPlayback - Web-based Windows Media Controller

## Introduction

PyWebPlayback is a Flask-based web application that enables users to remotely control Windows system volume and media playback through a web interface. The project features a modern Apple-style UI design, providing an intuitive and responsive user experience.

## Features

- 🎵 Real-time volume control
- ⏯️ Media playback control (play/pause, previous, next)
- 🖥️ Cross-device control support
- 🎨 Modern UI design
- 📱 Mobile-friendly
- 🔄 Real-time response
- 🔒 Local secure operation

## Tech Stack

- **Backend**: Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **System Interface**: 
  - pycaw (audio control)
  - win32api (media key simulation)
  - comtypes (COM component interaction)
- **Design Philosophy**: Apple-style UI

## Requirements

### System Requirements

- Windows OS
- Python 3.6+
- Web browser (Chrome/Edge/Firefox latest versions recommended)

### Dependencies

```bash
pip install flask
pip install pycaw
pip install comtypes
pip install pywin32
```

## Usage

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Program**
   ```bash
   python PyWebPlayback.py
   ```

3. **Access Control Panel**
   - Default browser opens automatically on startup
   - Default address: http://localhost:80/
   - Other devices on the same network can access via host IP

## Detailed Features

### 1. Volume Control

Volume control is implemented through pycaw library for precise Windows system volume control:

- Slider range: 0-100%
- Real-time response
- Visual feedback
- Precise adjustment

Core implementation:
```python
@app.route('/volume', methods=['POST'])
def set_volume():
    # Get volume value (0-100)
    volume = request.json.get('volume', 0)
    
    # Initialize COM library
    pythoncom.CoInitialize()
    try:
        # Get default audio device
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Set volume (value between 0.0 and 1.0)
        volume_interface.SetMasterVolumeLevelScalar(volume/100, None)
        
        return jsonify({'status': 'success'})
    finally:
        # Release COM library
        pythoncom.CoUninitialize()
```

### 2. Media Control

Media control features through media key simulation:

- ⏯️ Play/Pause
- ⏮️ Previous Track
- ⏭️ Next Track

Core implementation:
```python
@app.route('/playback', methods=['POST'])
def control_playback():
    action = request.json.get('action', '')
    
    # Media control key codes
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    
    try:
        if action == 'playpause':
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
        # ... other media control code
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
```

### 3. User Interface

Design features:

- Responsive layout
- Dark theme
- Glassmorphism effect
- Smooth animations
- Touch-optimized

CSS core features:
```css
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
```

## Development Guide

### Project Structure

```
PyWebPlayback/
│
├── PyWebPlayback.py     # Main program
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

### Core Classes

1. **Flask Application**
   - Handle HTTP requests
   - Serve web interface
   - Manage routes

2. **Audio Control**
   - pycaw interface
   - System volume management
   - COM component interaction

3. **Media Control**
   - Key simulation
   - Event handling
   - Status feedback

### Extension Development

1. **Adding New Features**
   ```python
   @app.route('/new_feature', methods=['POST'])
   def new_feature():
       # Implement new feature
       return jsonify({'status': 'success'})
   ```

2. **Customizing Interface**
   - Modify HTML_TEMPLATE variable
   - Add new styles
   - Extend JavaScript functionality

## Troubleshooting

### 1. Volume Control Issues

Possible causes:
- Not running as administrator
- pycaw library installation error
- System audio device issues

Solution:
```bash
# Reinstall dependencies
pip uninstall pycaw
pip install pycaw
```

### 2. Media Control Not Responding

Possible causes:
- win32api permission issues
- Media player incompatibility
- System hotkey conflicts

Solutions:
- Check pywin32 installation
- Verify media player compatibility
- Check system hotkey settings

### 3. Web Page Inaccessible

Possible causes:
- Port in use
- Firewall restrictions
- Network configuration issues

Solution:
```python
# Change port number
baseport = 8080  # or other available port
```

## Contributing

Contributions welcome:

1. Fork project
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

Code style requirements:
- Follow PEP 8
- Add comments
- Write tests
- Keep it simple

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Author

Gitee Volkath@amazoncloud

## Acknowledgments

Thanks to these open source projects:
- Flask
- pycaw
- pywin32
- comtypes

## Changelog

### v1.0.0
- Initial release
- Basic volume control
- Media playback control
- Responsive interface

---