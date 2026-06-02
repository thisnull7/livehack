<p align="center"><img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=35&duration=3000&pause=1000&color=4285F4&center=true&vCenter=true&width=600&lines=LIVECAM;Live+Video+%26+Microphone+Capture;Auto+Camera+%2B+Audio+Via+Link" alt="LIVECAM" /></p>
<p align="center"><img src="https://img.shields.io/badge/version-1.0-blue?style=for-the-badge" /> <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python" /> <img src="https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos%20%7C%20termux-lightgrey?style=for-the-badge" /> <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" /> <img src="https://img.shields.io/github/stars/thisnull7/livehack?style=social" /> <img src="https://img.shields.io/github/forks/thisnull7/livehack?style=social" /></p>

# LIVECAM

**LIVECAM** is a live video and microphone capture framework designed for educational security research. It generates a convincing Google Meet device check page that requests camera and microphone access from visitors. Once permission is granted, the tool captures photos every 2 seconds and records 3-second audio clips every 5 seconds in real-time. All media is saved locally with timestamped filenames. A multi-tunnel system (Cloudflared, Serveo, localhost.run) exposes your local server publicly without port forwarding. **DISCLAIMER**: This tool is intended for educational purposes and authorized security testing only. The developer assumes no liability for misuse. Always obtain explicit consent before capturing any individual's video or audio.

## Preview

<p align="center"><img src="https://raw.githubusercontent.com/thisnull7/livehack/refs/heads/main/live.png" alt="LIVECAM Terminal Preview" width="600" /></p>

## Features
Simultaneous camera and microphone access via a single browser permission prompt. Photos are automatically captured every 2 seconds and saved as JPEG files. Audio is recorded in 3-second clips every 5 seconds and saved as WebM files. The landing page mimics Google Meet's device check with a blue header, camera/microphone status cards, and a live video preview. Device fingerprinting collects user agent, platform, language, screen size, and timezone. All media is stored locally in a dedicated folder with detailed metadata logging. Multi-tunnel system uses Cloudflared as primary (auto-download, no account), with Serveo SSH and localhost.run as fallbacks. The terminal interface features ASCII art, spinner animations, color-coded output, and real-time capture alerts. Cross-platform support for Windows, Kali Linux, macOS, and Termux. Automatic port conflict detection and resolution. Auto-download of the correct Cloudflared binary for the system architecture.

## Prerequisites
Python 3.8 or higher must be installed on your system (python.org). Git is optional for cloning. SSH client is optional for Serveo/localhost.run fallback tunnels. On Windows 10/11 enable OpenSSH Client in Settings → Apps → Optional Features. On Termux, ensure storage permission is granted. Internet connection is required for tunnel creation.

## Installation
Clone the repository: `git clone https://github.com/thisnull7/livehack.git` then `cd livehack`. Install dependencies: `pip install -r requirements.txt` (the requirements file contains requests, colorama, pyfiglet). If colorama or pyfiglet fail, the tool runs without colors in plain text. Run the tool: `python livecam.py` (on Termux you may need `python3 livecam.py`).

## Usage
Execute `python livecam.py` and the tool will initialize. Startup automatically starts the HTTP server on port 8080, loads video/audio capture modules, prepares tunnel methods, then attempts connections in order. Tunnel methods tried: Cloudflare Tunnel first (URL https://xxxxx.trycloudflare.com, no account needed, binary auto-downloads), Serveo SSH second (https://xxxxx.serveo.net, requires SSH), localhost.run third (https://xxxxx.lhr.life, requires SSH). Once a tunnel is established, copy the displayed public URL and send it to the target. When the target opens the link and clicks "Test Camera & Microphone", their browser requests camera and microphone permission. After permission is granted, live preview appears, and captures begin automatically. Photos are captured every 2 seconds, audio clips (3 seconds) every 5 seconds. All files are saved to the `livecam_captures` folder. Press `Ctrl+C` to stop the tool gracefully; all data is preserved.

## Configuration
Edit the variables at the top of `livecam.py` to change the default port (`PORT = 8080`) or the capture directory (`CAPTURE_DIR = "livecam_captures"`). The tools directory for Cloudflared is auto-created at `~/.livecam`.

## Captured Data
Photos are saved as `photo_YYYYMMDD_HHMMSS_N.jpg` and audio as `audio_YYYYMMDD_HHMMSS_N.webm`. A `metadata.json` file logs each capture with type (photo/audio), timestamp, filename, target IP, and device info (user agent, platform, language, screen size, timezone). This allows easy correlation of media files with the target.

## Landing Page Details
The phishing page is a replica of Google Meet's device check with a blue gradient header and Meet icon, status cards showing "Camera" and "Microphone" readiness, a live preview box that activates after permission, "Test Camera & Microphone" button, loading spinner, success checkmark, error messages with retry, and a footer with "Google Meet ©2024 • Device Check". Animated background orbs enhance visual appeal. The page requests both video and audio permissions simultaneously to appear legitimate.

## Tunnel Methods
Three fallback methods ensure connectivity. Cloudflare Tunnel downloads the binary automatically for the correct architecture (amd64, arm64, arm). Serveo creates a temporary subdomain via SSH reverse proxy. localhost.run provides a `*.lhr.life` URL, also via SSH. If one method fails, the next is tried automatically.

## File Structure
livehack/
├── live.py # Main tool script
├── requirements.txt # Python dependencies
├── README.md # This documentation
├── LICENSE # MIT License
└── livecam_captures/ # Auto-generated folder with photos, audio, metadata.json

## Troubleshooting
If the port is already in use, the tool automatically kills the conflicting process or switches to the next available port. If Cloudflared download fails, download it manually from the Cloudflared releases page and place the binary in `~/.livecam/`. If SSH is not found, install OpenSSH (Linux: `sudo apt install openssh-client`, Termux: `pkg install openssh`, Windows: Optional Features). If no colors appear, install colorama with `pip install colorama`. If the target denies camera/microphone, the page displays an error with a retry button. If photos or audio are blank, ensure the target's device has a functioning camera and microphone. For Termux, make sure storage permission is granted (`termux-setup-storage`) if you need to access the captures folder easily.

## Author
**null7** — GitHub: [thisnull7](https://github.com/thisnull7). If you find this project useful, give it a star. For issues or feature requests, open an issue on the repository.

## License
MIT License — see LICENSE file for details. Made for educational purposes only. Created by null7.

<p align="center"><img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=18&duration=2000&pause=1000&color=4285F4&center=true&vCenter=true&width=400&lines=Made+for+educational+purposes+only;Created+by+null7" /></p>
