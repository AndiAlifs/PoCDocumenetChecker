# 🌟 DigitalOcean Lighthouse Deployment Guide

Quick deployment guide specifically for **DigitalOcean Lighthouse** instances.

## 🪶 Lighthouse Setup

### 1. Create Lighthouse Instance

1. **Go to DigitalOcean Lighthouse**
2. **Choose configuration:**
   - **OS:** Ubuntu 22.04 LTS
   - **Plan:** $6/month (1 GB RAM, 25 GB SSD) - minimum recommended
   - **Plan:** $12/month (2 GB RAM, 50 GB SSD) - better performance
3. **Create instance** and note the IP address

### 2. Connect to Lighthouse

```bash
# SSH into your Lighthouse instance
ssh root@your-lighthouse-ip

# Or if using a regular user
ssh username@your-lighthouse-ip
```

### 3. Deploy Application

**Option 1: One-command deployment**
```bash
# Upload your project
scp -r c:\projects\PoCDocumenetChecker root@your-lighthouse-ip:/root/

# SSH and deploy
ssh root@your-lighthouse-ip
cd /root/PoCDocumenetChecker
chmod +x deploy.sh
./deploy.sh
```

**Option 2: Docker deployment**
```bash
# Upload project
scp -r c:\projects\PoCDocumenetChecker root@your-lighthouse-ip:/root/

# SSH and run
ssh root@your-lighthouse-ip
cd /root/PoCDocumenetChecker

# Create environment file
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env

# Deploy with Docker
sudo docker-compose up -d
```

### 4. Configure Environment

```bash
# Edit environment variables
nano /opt/document-checker/.env

# Add your actual API key
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 5. Start the Service

```bash
# Start the application service
sudo systemctl start document-checker

# Enable auto-start on boot
sudo systemctl enable document-checker

# Check status
sudo systemctl status document-checker
```

## 🌐 Access Your Application

Your app will be available at:
- **Direct access:** `http://YOUR_LIGHTHOUSE_IP:8501`
- **With domain:** `http://your-domain.com` (if using Nginx)

Find your Lighthouse IP:
```bash
curl http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address
```

## 🔧 Lighthouse-Specific Features

### Automatic Firewall Configuration
The deploy script automatically configures UFW firewall for:
- Port 22 (SSH)
- Port 8501 (Streamlit)  
- Port 80 (HTTP)
- Port 443 (HTTPS)

### Networking Information
```bash
# Check external IP
curl http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address

# Check internal IP  
curl http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address

# Check all network interfaces
ip addr show
```

### Resource Monitoring
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check CPU usage
top

# Check system resources
htop  # install with: sudo apt install htop
```

## 🛠️ Management Commands

### Service Management
```bash
# View live logs
sudo journalctl -u document-checker -f

# Restart service
sudo systemctl restart document-checker

# Stop service  
sudo systemctl stop document-checker

# Check service status
sudo systemctl status document-checker
```

### Docker Management (if using Docker)
```bash
# Check running containers
docker ps

# View logs
docker-compose logs -f

# Restart containers
docker-compose restart

# Update and restart
docker-compose down
docker-compose up -d
```

### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update application
cd /opt/document-checker
git pull  # if using git
sudo systemctl restart document-checker
```

## 🔒 Security Best Practices

### 1. Secure SSH (recommended)
```bash
# Change default SSH port (optional)
sudo nano /etc/ssh/sshd_config
# Change: Port 2222

# Disable root login (after creating user)
# Change: PermitRootLogin no

sudo systemctl restart ssh
```

### 2. Firewall Status
```bash
# Check firewall rules
sudo ufw status verbose

# Add specific rules if needed
sudo ufw allow from specific-ip to any port 8501
```

### 3. SSL/HTTPS Setup
```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (if using domain)
sudo certbot --nginx -d your-domain.com
```

## 🚨 Troubleshooting

### Common Lighthouse Issues

**1. Permission denied:**
```bash
sudo chown -R $USER:$USER /opt/document-checker
```

**2. Port not accessible:**
```bash
# Check if service is running
sudo systemctl status document-checker

# Check if port is open
sudo netstat -tlnp | grep 8501

# Check firewall
sudo ufw status
```

**3. Out of memory:**
```bash
# Check memory usage
free -h

# Restart service to free memory
sudo systemctl restart document-checker
```

**4. Docker issues:**
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Clean up Docker
docker system prune -a
```

## 💰 Lighthouse Pricing

### Recommended Plans:
- **$6/month:** 1 GB RAM, 1 vCPU, 25 GB SSD - Basic usage
- **$12/month:** 2 GB RAM, 1 vCPU, 50 GB SSD - **Recommended**
- **$24/month:** 4 GB RAM, 2 vCPUs, 80 GB SSD - Heavy usage

### Bandwidth:
- All plans include 1 TB transfer
- Additional transfer: $0.01/GB

## 📞 Support

### DigitalOcean Lighthouse Resources:
- **Documentation:** https://docs.digitalocean.com/products/lighthouse/
- **Community:** https://www.digitalocean.com/community/
- **Support:** Available through DigitalOcean dashboard

### Application Logs Location:
- **Service logs:** `sudo journalctl -u document-checker -f`
- **Application logs:** `/opt/document-checker/logs/`
- **Nginx logs:** `/var/log/nginx/`

Your Document Checker app should now be running smoothly on Lighthouse! 🚀