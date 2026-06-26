# Deploy to Server - Deployment Guide

## Server Requirements

- Linux (Ubuntu 20.04+ recommended)
- Python 3.9+
- GPU (NVIDIA CUDA 11.8+) - Recommended
- 8GB+ RAM
- 5GB+ disk space (for model)
- 20GB+ disk space (for logs/audio)

## Step 1: Upload Files to Server

```bash
scp -r Farsi_to_Text/ user@server_ip:/home/user/
ssh user@server_ip
cd /home/user/Farsi_to_Text
```

## Step 2: Install Dependencies

```bash
pip install -r backend/requirements.txt

# If GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Step 3: Create Systemd Service

Create `/etc/systemd/system/voice-bot.service`:

```ini
[Unit]
Description=Farsi Voice Bot API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/Farsi_to_Text/backend
Environment="PATH=/usr/local/bin:/usr/bin"
Environment="KMP_DUPLICATE_LIB_OK=TRUE"
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable voice-bot
sudo systemctl start voice-bot
```

## Step 4: Nginx Reverse Proxy

Create `/etc/nginx/sites-available/voice-bot`:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /home/user/Farsi_to_Text/frontend;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/voice-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 5: SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## Step 6: Update Frontend URL

Change in `frontend/index.html`:
```javascript
// From:
const res = await fetch(`http://localhost:9999/transcribe/file${langParam}`, {

// To:
const res = await fetch(`https://your_domain.com/api/transcribe/file${langParam}`, {
```

## Step 7: Monitor

```bash
# View logs
sudo journalctl -u voice-bot -f

# Check status
sudo systemctl status voice-bot

# Restart
sudo systemctl restart voice-bot
```

## Performance Tips

- Use GPU for speed
- Set worker count: `--workers 4`
- Enable caching
- Monitor disk space for Audios/logs

## Security

- Use firewall rules
- Keep only ports 80/443 open
- Use HTTPS always
- Validate user inputs
- Rate limiting recommended

## Scaling

For multiple users:
- Use load balancer (AWS ELB, HAProxy)
- Database instead of CSV
- Redis cache
- Multiple GPU servers
