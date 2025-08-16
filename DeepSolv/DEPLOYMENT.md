# 🚀 Deployment Guide - Shopify Store Insights Fetcher

This guide covers different deployment scenarios for the Shopify Store Insights Fetcher API.

## 📋 Prerequisites

- Python 3.8+ installed
- MySQL database (optional but recommended for production)
- OpenAI API key (optional, for AI features)

## 🖥️ Local Development Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd shopify-insights-fetcher

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/shopify_insights
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
LOG_LEVEL=INFO
```

### 3. Database Setup (Optional)
```sql
-- Connect to MySQL and run:
CREATE DATABASE shopify_insights CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'shopify_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON shopify_insights.* TO 'shopify_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Run Application
```bash
# Development mode
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use VS Code task: "Run Shopify Insights API"
```

### 5. Verify Installation
```bash
# Run quick test
python quick_test.py

# Run full demo
python demo.py

# Run unit tests
pytest tests/ -v
```

## 🐳 Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://root:password@db:3306/shopify_insights
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=False
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=shopify_insights
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

### 3. Build and Run
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
- **Instance Type**: t3.medium or higher
- **OS**: Ubuntu 22.04 LTS
- **Security Groups**: Open ports 22 (SSH), 80 (HTTP), 8000 (API)

#### 2. Server Setup
```bash
# Connect to EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server

# Clone repository
git clone <your-repository-url>
cd shopify-insights-fetcher

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. MySQL Configuration
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```
```sql
CREATE DATABASE shopify_insights CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'shopify_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON shopify_insights.* TO 'shopify_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 4. Environment Configuration
```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=mysql+pymysql://shopify_user:secure_password@localhost:3306/shopify_insights
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=False
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=45
EOF
```

#### 5. Systemd Service
```bash
# Create service file
sudo tee /etc/systemd/system/shopify-insights.service > /dev/null <<EOF
[Unit]
Description=Shopify Insights Fetcher API
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=exec
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/shopify-insights-fetcher
Environment=PATH=/home/ubuntu/shopify-insights-fetcher/venv/bin
ExecStart=/home/ubuntu/shopify-insights-fetcher/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable shopify-insights
sudo systemctl start shopify-insights

# Check status
sudo systemctl status shopify-insights
```

#### 6. Nginx Reverse Proxy
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/shopify-insights > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/shopify-insights /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Heroku Deployment

#### 1. Prepare for Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt
```

#### 2. Deploy to Heroku
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set OPENAI_API_KEY=your_api_key_here
heroku config:set DEBUG=False

# Add MySQL addon (optional)
heroku addons:create cleardb:ignite

# Get database URL
heroku config:get CLEARDB_DATABASE_URL
# Set as DATABASE_URL
heroku config:set DATABASE_URL=mysql+pymysql://username:password@hostname/database_name

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open app
heroku open
```

## 🔧 Production Configuration

### Performance Optimization
```python
# In main.py, update for production
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        workers=4,  # Adjust based on CPU cores
        loop="uvloop",  # For better performance
        log_level="info"
    )
```

### Environment Variables for Production
```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/shopify_insights
OPENAI_API_KEY=your_production_api_key
DEBUG=False
LOG_LEVEL=WARNING
MAX_CONCURRENT_REQUESTS=20
REQUEST_TIMEOUT=60
REQUESTS_PER_MINUTE=120
```

### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_store_url ON store_analyses(website_url);
CREATE INDEX idx_product_store ON products(store_id);
CREATE INDEX idx_analysis_date ON store_analyses(created_at);

-- Optimize MySQL configuration
# Add to /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
query_cache_size = 64M
```

## 🔐 Security Considerations

### 1. Environment Security
```bash
# Ensure .env file permissions
chmod 600 .env

# Never commit .env to version control
echo ".env" >> .gitignore
```

### 2. Database Security
```sql
-- Create read-only user for analytics
CREATE USER 'analytics_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT SELECT ON shopify_insights.* TO 'analytics_user'@'localhost';

-- Regular backups
# Add to crontab
0 2 * * * mysqldump -u root -p shopify_insights > /backups/shopify_insights_$(date +\%Y\%m\%d).sql
```

### 3. API Security
```python
# Add rate limiting (install slowapi)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add to endpoints
@limiter.limit("10/minute")
@app.post("/analyze-store")
async def analyze_store(request: Request, ...):
    ...
```

## 📊 Monitoring and Logging

### 1. Application Logging
```python
# Enhanced logging configuration
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 2. Health Monitoring
```bash
# Create monitoring script
cat > monitor.sh << EOF
#!/bin/bash
while true; do
    response=\$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ \$response != "200" ]; then
        echo "API is down! Status code: \$response"
        # Send alert (email, Slack, etc.)
    fi
    sleep 30
done
EOF

chmod +x monitor.sh
nohup ./monitor.sh &
```

## 🚀 Scaling Considerations

### Horizontal Scaling
- Use load balancer (AWS ALB, Nginx)
- Deploy multiple instances
- Shared database across instances
- Redis for caching (optional)

### Vertical Scaling
- Increase server CPU/RAM
- Optimize database queries
- Use connection pooling
- Implement caching strategies

## 📝 Maintenance

### Regular Tasks
```bash
# Database maintenance
mysqldump shopify_insights > backup.sql

# Log rotation
logrotate /etc/logrotate.d/shopify-insights

# Security updates
sudo apt update && sudo apt upgrade -y

# Application updates
git pull origin main
pip install -r requirements.txt
sudo systemctl restart shopify-insights
```

### Monitoring Commands
```bash
# Check service status
sudo systemctl status shopify-insights

# View logs
sudo journalctl -u shopify-insights -f

# Monitor resource usage
htop
df -h
free -h

# Database status
mysql -u root -p -e "SHOW PROCESSLIST;"
```

---

**🎉 Your Shopify Store Insights Fetcher API is now production-ready!**

For additional support or questions, refer to the [main documentation](DOCUMENTATION.md) or create an issue in the repository.
