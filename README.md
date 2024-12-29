# PyWebPlayback - 网页版 Windows 媒体控制器

## 项目简介

PyWebPlayback 是一个基于 Flask 的 Web 应用程序，它允许用户通过网页界面远程控制 Windows 系统的音量和媒体播放。该项目采用现代化的 Apple 风格界面设计，提供了直观、响应式的用户体验。

## 功能特点

- 🎵 实时音量控制
- ⏯️ 媒体播放控制（播放/暂停、上一曲、下一曲）
- 🖥️ 跨设备控制支持
- 🎨 现代化 UI 设计
- 📱 移动端适配
- 🔄 实时响应
- 🔒 本地安全运行

## 技术栈

- **后端框架**: Flask
- **前端技术**: HTML5, CSS3, JavaScript
- **系统接口**: 
  - pycaw (音频控制)
  - win32api (媒体按键模拟)
  - comtypes (COM 组件交互)
- **设计理念**: Apple 风格 UI

## 安装要求

### 系统要求

- Windows 操作系统
- Python 3.6+
- 网络浏览器（推荐 Chrome/Edge/Firefox 最新版本）

### 依赖包

```bash
pip install flask
pip install pycaw
pip install comtypes
pip install pywin32
```

## 使用说明

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **运行程序**
   ```bash
   python PyWebPlayback.py
   ```

3. **访问控制面板**
   - 程序启动后会自动打开默认浏览器
   - 默认访问地址：http://localhost:80/
   - 同一局域网内其他设备可通过主机 IP 访问

## 详细功能说明

### 1. 音量控制

音量控制功能通过 pycaw 库实现对 Windows 系统音量的精确控制：

- 滑动条范围：0-100%
- 实时响应
- 具有视觉反馈
- 支持精确调节

代码实现核心：
```python
@app.route('/volume', methods=['POST'])
def set_volume():
    # 获取音量值（0-100）
    volume = request.json.get('volume', 0)
    
    # 初始化 COM 库
    pythoncom.CoInitialize()
    try:
        # 获取默认音频设备
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
        
        # 设置音量（值在 0.0 到 1.0 之间）
        volume_interface.SetMasterVolumeLevelScalar(volume/100, None)
        
        return jsonify({'status': 'success'})
    finally:
        # 释放 COM 库
        pythoncom.CoUninitialize()
```

### 2. 媒体控制

媒体控制功能通过模拟媒体键实现，支持以下操作：

- ⏯️ 播放/暂停
- ⏮️ 上一曲
- ⏭️ 下一曲

代码实现核心：
```python
@app.route('/playback', methods=['POST'])
def control_playback():
    action = request.json.get('action', '')
    
    # 媒体控制键代码
    VK_MEDIA_PLAY_PAUSE = 0xB3
    VK_MEDIA_NEXT_TRACK = 0xB0
    VK_MEDIA_PREV_TRACK = 0xB1
    
    try:
        if action == 'playpause':
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
        # ... 其他媒体控制代码
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
```

### 3. 用户界面

界面设计特点：

- 响应式布局
- 深色主题
- 毛玻璃效果
- 流畅动画
- 触摸优化

CSS 核心特性：
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

## 开发说明

### 项目结构

```
PyWebPlayback/
│
├── PyWebPlayback.py     # 主程序
├── requirements.txt     # 依赖配置
└── README.md           # 项目文档
```

### 核心类

1. **Flask 应用**
   - 处理 HTTP 请求
   - 提供 Web 界面
   - 管理路由

2. **音频控制**
   - 使用 pycaw 接口
   - 系统音量管理
   - COM 组件交互

3. **媒体控制**
   - 按键模拟
   - 事件处理
   - 状态反馈

### 扩展开发

1. **添加新功能**
   ```python
   @app.route('/new_feature', methods=['POST'])
   def new_feature():
       # 实现新功能
       return jsonify({'status': 'success'})
   ```

2. **自定义界面**
   - 修改 HTML_TEMPLATE 变量
   - 添加新的样式
   - 扩展 JavaScript 功能

## 常见问题

### 1. 无法控制音量

可能原因：
- 未以管理员权限运行
- pycaw 库安装错误
- 系统音频设备异常

解决方案：
```bash
# 重新安装依赖
pip uninstall pycaw
pip install pycaw
```

### 2. 媒体控制无响应

可能原因：
- win32api 权限问题
- 媒体播放器不支持
- 系统快捷键冲突

解决方案：
- 检查 pywin32 安装
- 验证媒体播放器兼容性
- 检查系统快捷键设置

### 3. 网页无法访问

可能原因：
- 端口被占用
- 防火墙限制
- 网络配置问题

解决方案：
```python
# 修改端口号
baseport = 8080  # 或其他可用端口
```

## 贡献指南

欢迎提供改进建议和代码贡献：

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

代码风格要求：
- 遵循 PEP 8
- 添加注释
- 编写测试
- 保持简洁

## 许可证

本项目采用 MIT 许可证。详细信息请参阅 LICENSE 文件。

## 作者

Gitee Volkath@amazoncloud

## 致谢

感谢以下开源项目：
- Flask
- pycaw
- pywin32
- comtypes

## 更新日志

### v1.0.0
- 初始版本发布
- 基础音量控制
- 媒体播放控制
- 响应式界面

---

**注意**：本项目仅用于学习和个人使用，请勿用于商业用途。