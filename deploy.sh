#!/bin/bash

# Deployment script for DigitalOcean Lighthouse Ubuntu instances
set -e

echo "🚀 Starting deployment of Document Checker App on Lighthouse..."

# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall for Lighthouse
echo "🔥 Configuring UFW firewall..."
sudo ufw allow ssh
sudo ufw allow 8501/tcp  # Streamlit
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw --force enable

# Install Python 3.11 and pip
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install Docker (optimized for Lighthouse)
if ! command -v docker &> /dev/null; then
    echo "Installing Docker for Lighthouse..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    
    # Install docker-compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    echo "⚠️  You may need to logout and login again for Docker permissions to take effect"
fi

# Create application directory (Lighthouse-optimized path)
APP_DIR="/opt/document-checker"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy files to production directory (excluding hidden files safely)
echo "📁 Copying application files..."
find . -maxdepth 1 -not -name '.' -not -name '.git' -exec cp -r {} $APP_DIR/ \;
cd $APP_DIR

# Set proper permissions
chmod +x deploy.sh || true

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
echo "GEMINI_API_KEY=your_api_key_here" > .env
echo "⚠️  Please edit /opt/document-checker/.env with your actual GEMINI_API_KEY"

# Create systemd service
sudo tee /etc/systemd/system/document-checker.service > /dev/null <<EOF
[Unit]
Description=Document Checker Streamlit App
After=network.target

[Service]
Type=exec
User=$USER
WorkingDirectory=/opt/document-checker
Environment=PATH=/opt/document-checker/venv/bin
ExecStart=/opt/document-checker/venv/bin/streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable document-checker.service

# Install and configure Nginx (optional reverse proxy)
read -p "Do you want to install Nginx as reverse proxy? (y/n): " install_nginx
if [[ $install_nginx == "y" ]]; then
    sudo apt install -y nginx
    
    sudo tee /etc/nginx/sites-available/document-checker > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Change this to your domain
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
    
    sudo ln -s /etc/nginx/sites-available/document-checker /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
fi

echo "✅ Deployment completed on Lighthouse!"
echo ""
echo "🌐 Lighthouse Instance Information:"
echo "External IP: $(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address)"
echo "Internal IP: $(curl -s http://169.254.169.254/metadata/v1/interfaces/private/0/ipv4/address)"
echo ""
echo "📝 Next steps:"
echo "1. Edit /opt/document-checker/.env with your GEMINI_API_KEY:"
echo "   nano /opt/document-checker/.env"
echo "2. Start the service:"
echo "   sudo systemctl start document-checker"
echo "3. Check status:"
echo "   sudo systemctl status document-checker"
echo "4. Access your app at:"
echo "   http://$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address):8501"
if [[ $install_nginx == "y" ]]; then
    echo "5. Or via Nginx: http://your-domain.com (after configuring DNS)"
fi
echo ""
echo "🔧 Useful commands:"
echo "   View logs: sudo journalctl -u document-checker -f"
echo "   Restart: sudo systemctl restart document-checker"
echo "   Stop: sudo systemctl stop document-checker"
echo ""
echo "🛡️  Firewall is configured to allow ports 22, 80, 443, and 8501"
echo "   Check firewall: sudo ufw status"