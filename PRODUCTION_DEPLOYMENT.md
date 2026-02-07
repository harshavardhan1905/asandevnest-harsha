# 🌐 Professional Production Deployment Guide

This guide details the steps to deploy **Asan DevNest** on a production-grade infrastructure (e.g., DigitalOcean, AWS, Linode) using **Ubuntu, Nginx, Gunicorn, and PostgreSQL**.

---

## 🏗️ 1. Server Preparation (Ubuntu 22.04+)

### **Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

### **Install Dependencies**
```bash
sudo apt install python3-pip python3-dev python3-venv libpq-dev postgresql postgresql-contrib nginx curl -y
```

---

## 🐘 2. Production Database (PostgreSQL)

SQLite is not recommended for production. We will use PostgreSQL.

### **Create Database & User**
```bash
sudo -u postgres psql
```
Inside the SQL prompt:
```sql
CREATE DATABASE asan_prod;
CREATE USER asan_user WITH PASSWORD 'your_strong_password';
ALTER ROLE asan_user SET client_encoding TO 'utf8';
ALTER ROLE asan_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asan_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE asan_prod TO asan_user;
\q
```

---

## 📂 3. Application Setup

### **Clone and Virtual Environment**
```bash
cd /var/www
sudo git clone https://github.com/your-username/asan_devnest.git
sudo chown -R $USER:$USER asan_devnest
cd asan_devnest
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### **Configure Environment Variables**
Create a `.env` file:
```bash
nano .env
```
Add production values:
```bash
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=y0ur_v3ry_str0ng_r4nd0m_k3y
DATABASE_URL=postgresql://asan_user:your_strong_password@localhost/asan_prod
UPLOAD_FOLDER=/var/www/asan_devnest/uploads
```

---

## ⚙️ 4. Gunicorn & Systemd Service

Create a systemd service to keep the app running in the background.

```bash
sudo nano /etc/systemd/system/asan.service
```

Paste the following:
```ini
[Unit]
Description=Gunicorn instance to serve Asan DevNest
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/asan_devnest
Environment="PATH=/var/www/asan_devnest/venv/bin"
EnvironmentFile=/var/www/asan_devnest/.env
ExecStart=/var/www/asan_devnest/venv/bin/gunicorn --workers 3 --bind unix:asan.sock -m 007 run:app

[Install]
WantedBy=multi-user.target
```

### **Start the Service**
```bash
sudo systemctl start asan
sudo systemctl enable asan
```

---

## 🌐 5. Nginx Configuration

Nginx acts as the reverse proxy, handling SSL and static files.

```bash
sudo nano /etc/nginx/sites-available/asan
```

Paste the following:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/asan_devnest/asan.sock;
    }

    location /static {
        alias /var/www/asan_devnest/app/static;
    }

    location /uploads {
        alias /var/www/asan_devnest/uploads;
    }
}
```

### **Enable Config**
```bash
sudo ln -s /etc/nginx/sites-available/asan /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 6. SSL Security (HTTPS)

Use Let's Encrypt for free, automatic SSL.

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🛠️ 7. Initializing the App

Now that the infrastructure is ready, create the admin and tables:
```bash
export FLASK_APP=run.py
source venv/bin/activate
flask init-db
flask create-admin
```

---

## ✅ Summary Checklist
- [ ] PostgreSQL Database Configured
- [ ] Gunicorn Systemd Service Active
- [ ] Nginx Reverse Proxy Configured
- [ ] SSL (HTTPS) Enabled
- [ ] Debug Mode OFF
- [ ] Logs Monitored (`sudo journalctl -u asan`)

---

**🎉 Your application is now running at a professional production level!**
