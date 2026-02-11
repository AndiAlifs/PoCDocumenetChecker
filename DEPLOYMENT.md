# 🏦 Mandiri AI Auditor Pro - VPS Deployment Guide

Trade Finance Document Auditor powered by Streamlit and Google Gemini AI.

## 📋 Prerequisites

- VPS with Ubuntu 20.04+ or Debian 11+
- Domain name (optional, for HTTPS)
- Google Gemini API Key

## 🚀 Deployment Options

### Option 1: Docker Deployment (Recommended)

1. **Upload files to VPS:**
```bash
scp -r . user@your-vps-ip:/home/user/document-checker
```

2. **SSH into VPS and deploy:**
```bash
ssh user@your-vps-ip
cd document-checker

# Set your API key
echo "GEMINI_API_KEY=your_actual_api_key" > .env

# Deploy with Docker
sudo docker-compose up -d
```

3. **Access your app:** `http://your-vps-ip:8501`

### Option 2: Direct Python Deployment

1. **Upload and run deployment script:**
```bash
scp -r . user@your-vps-ip:/home/user/document-checker
ssh user@your-vps-ip
cd document-checker
chmod +x deploy.sh
./deploy.sh
```

2. **Configure environment:**
```bash
sudo nano /opt/document-checker/.env
# Add: GEMINI_API_KEY=your_actual_api_key
```

3. **Start the service:**
```bash
sudo systemctl start document-checker
sudo systemctl status document-checker
```

### Option 3: Manual Deployment

1. **Install dependencies:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip nginx
```

2. **Setup application:**
```bash
sudo mkdir -p /opt/document-checker
sudo chown $USER:$USER /opt/document-checker
cp -r * /opt/document-checker/
cd /opt/document-checker

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
echo "GEMINI_API_KEY=your_api_key" > .env
```

4. **Run the app:**
```bash
streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
```

## 🔧 Production Configuration

### Nginx Reverse Proxy (Recommended)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### SSL/HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Monitoring & Logs

### Check service status:
```bash
sudo systemctl status document-checker
```

### View logs:
```bash
sudo journalctl -u document-checker -f
```

### Docker logs:
```bash
docker-compose logs -f
```

## 🛡️ Security Recommendations

1. **Firewall setup:**
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. **Regular updates:**
```bash
sudo apt update && sudo apt upgrade -y
```

3. **Secure .env file:**
```bash
chmod 600 .env
```

## 🔄 Updates & Maintenance

### Update application:
```bash
# Stop service
sudo systemctl stop document-checker

# Upload new files
cd /opt/document-checker
git pull  # if using git

# Restart service
sudo systemctl start document-checker
```

### Docker updates:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🚨 Troubleshooting

### Common issues:

1. **Port already in use:**
```bash
sudo lsof -i :8501
sudo kill -9 PID
```

2. **Permission denied:**
```bash
sudo chown -R $USER:$USER /opt/document-checker
```

3. **Module not found:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 🌐 Access URLs

- **Direct access:** `http://your-vps-ip:8501`
- **With domain:** `http://your-domain.com`
- **With SSL:** `https://your-domain.com`

## 💰 VPS Recommendations

### Budget options:
- DigitalOcean Droplet: $6/month (1GB RAM)
- Linode: $5/month (1GB RAM)
- Vultr: $6/month (1GB RAM)

### Performance options:
- DigitalOcean: $12/month (2GB RAM)
- AWS EC2 t3.small: ~$17/month
- Google Cloud: ~$15/month

**Minimum requirements:** 1GB RAM, 1 CPU, 25GB storage