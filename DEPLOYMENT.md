# Deployment Guide - Release 1

This guide covers deploying the Slack SQL Cockpit Release 1 to production.

## Pre-Deployment Checklist

### ✅ **Prerequisites**
- [ ] Python 3.8+ installed
- [ ] Slack app configured with bot token
- [ ] Ollama running with your chosen model
- [ ] SQLite database accessible
- [ ] Environment variables configured
- [ ] Tests passing: `python run_tests.py`

### ✅ **Required Environment Variables**
```env
# Required
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SQLITE_PATH=/path/to/your/database.db

# Optional (with defaults)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=granite4
SCHEMA_YAML_PATH=./schema.yaml
```

## Deployment Options

### 🚀 **Option 1: Direct Python Deployment**

#### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
# Copy and edit configuration
cp .env.example .env
# Edit .env with your actual values
```

#### 3. Validate Setup
```bash
# Run tests
python run_tests.py

# Test configuration
python -c "from config.settings import config; config.validate(); print('✅ Config OK')"
```

#### 4. Start Application
```bash
# Production mode
python app.py
```

#### 5. Process Management (Recommended)
```bash
# Using systemd (Linux)
sudo nano /etc/systemd/system/data-distillery.service
```

**systemd service file:**
```ini
[Unit]
Description=Data Distillery Slack SQL Cockpit
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/data-distillery
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable data-distillery
sudo systemctl start data-distillery
sudo systemctl status data-distillery
```

### 🐳 **Option 2: Docker Deployment**

#### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["python", "app.py"]
```

#### 2. Build and Run
```bash
# Build image
docker build -t data-distillery:1.0 .

# Run container
docker run -d \
  --name data-distillery \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /path/to/database:/app/data \
  -e SLACK_BOT_TOKEN=your-token \
  -e SQLITE_PATH=/app/data/chinook.db \
  data-distillery:1.0
```

#### 3. Docker Compose
```yaml
version: '3.8'

services:
  data-distillery:
    build: .
    container_name: data-distillery
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports
    environment:
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SQLITE_PATH=/app/data/chinook.db
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama
    container_name: ollama
    restart: unless-stopped
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"

volumes:
  ollama-data:
```

### ☁️ **Option 3: Cloud Deployment**

#### AWS EC2
```bash
# 1. Launch EC2 instance (t3.medium or larger)
# 2. Install Docker and Docker Compose
# 3. Clone repository
# 4. Configure environment variables
# 5. Run with Docker Compose
# 6. Configure security groups (port 5000)
# 7. Setup load balancer if needed
```

#### Heroku
```bash
# 1. Install Heroku CLI
# 2. Create Heroku app
heroku create your-app-name

# 3. Set environment variables
heroku config:set SLACK_BOT_TOKEN=your-token
heroku config:set OLLAMA_BASE_URL=your-ollama-url

# 4. Deploy
git push heroku main
```

## Production Configuration

### 🔧 **Environment Variables**
```env
# Production settings
FLASK_ENV=production
DEBUG=False

# Security
SLACK_BOT_TOKEN=xoxb-production-token
SQLITE_PATH=/secure/path/to/production.db

# Performance
DEFAULT_LIMIT=500
ROWS_PER_PAGE=12
LLM_TIMEOUT=120

# Monitoring
LOG_LEVEL=INFO
```

### 🔒 **Security Considerations**
- [ ] Use HTTPS (reverse proxy with SSL)
- [ ] Restrict database file permissions (read-only)
- [ ] Use environment variables for secrets
- [ ] Enable proper logging
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

### 📊 **Monitoring Setup**

#### Basic Health Check Endpoint
Add to `routes/slack_routes.py`:
```python
@slack_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }), 200
```

#### Log Monitoring
```bash
# Monitor application logs
tail -f /path/to/app/logs/app.log

# Monitor system resources
htop
iostat 1
```

### 🚨 **Backup and Recovery**

#### Database Backup
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /path/to/database.db /backup/database_$DATE.db
find /backup -name "database_*.db" -mtime +30 -delete
```

#### Configuration Backup
```bash
# Backup configuration and environment
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env schema.yaml
```

## Performance Optimization

### 🚀 **Production Tuning**
```python
# In config/settings.py for production
class ProductionConfig(Config):
    DEBUG = False
    LLM_TIMEOUT = 60
    DEFAULT_LIMIT = 100
    ROWS_PER_PAGE = 10
```

### 📈 **Scaling Considerations**
- **Database**: Consider read replicas for high query volume
- **LLM Service**: Scale Ollama horizontally if needed
- **Application**: Use multiple instances behind load balancer
- **Caching**: Add Redis for session management in multi-instance setup

## Troubleshooting

### 🐛 **Common Issues**

#### Application Won't Start
```bash
# Check configuration
python -c "from config.settings import config; config.validate()"

# Check dependencies
pip list | grep -E "flask|requests|pandas"

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

#### Slack Integration Issues
```bash
# Test Slack token
curl -X POST -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  https://slack.com/api/auth.test
```

#### Database Connection Issues
```bash
# Test database access
python -c "from services.database import DatabaseService; print(DatabaseService.get_database_schema()[:100])"
```

#### LLM Service Issues
```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Test model availability
curl http://localhost:11434/api/chat -d '{
  "model": "granite4",
  "messages": [{"role": "user", "content": "test"}]
}'
```

### 📞 **Support and Monitoring**

#### Log Analysis
```bash
# Application logs
grep ERROR /path/to/app/logs/*.log

# Security events
grep "WARNING" /path/to/app/logs/*.log | grep -E "SQL|security|forbidden"
```

#### Performance Monitoring
```bash
# Monitor response times
grep "Processing time" /path/to/app/logs/*.log

# Monitor resource usage
ps aux | grep python
netstat -tlnp | grep :5000
```

---

## Post-Deployment Verification

### ✅ **Final Checklist**
- [ ] Application starts successfully
- [ ] Health check endpoint responds
- [ ] Slack commands work (`/dd`, `/help`)
- [ ] Database queries execute
- [ ] CSV export functions
- [ ] Plotting works
- [ ] Error handling is graceful
- [ ] Logs are being written
- [ ] Monitoring is active

### 🎉 **Success!**
Your Data Distillery Slack SQL Cockpit Release 1 is now deployed and ready for production use!

---

**For additional support, check the troubleshooting section or review the logs for detailed error information.**