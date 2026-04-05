# Nginx and Apache Setup Lab Manual

## Overview
This guide covers setting up Nginx as a web server on port 80 and Apache on port 8080.

## Prerequisites
- Ubuntu/Debian-based Linux system
- Root or sudo access

## Installation Steps

### Step 1: Install Nginx
```bash
sudo apt-get update
sudo apt-get install -y nginx
```

### Step 2: Install Apache (if not already installed)
```bash
sudo apt-get install -y apache2
```

## Configuration Steps

### Step 3: Configure Apache to use port 8080

1. Edit the Apache ports configuration:
```bash
sudo sed -i 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf
```

2. Update the default virtual host:
```bash
sudo sed -i 's/<VirtualHost \*:80>/<VirtualHost *:8080>/' /etc/apache2/sites-enabled/000-default.conf
```

3. Verify Apache configuration:
```bash
sudo apache2ctl -t
```

### Step 4: Configure Nginx to use port 80

The default Nginx configuration already listens on port 80. Verify:
```bash
sudo cat /etc/nginx/sites-available/default
```

Ensure the configuration contains:
```nginx
listen 80 default_server;
listen [::]:80 default_server;
```

If changes are needed:
```bash
sudo sed -i 's/listen 8080 default_server;/listen 80 default_server;/g' /etc/nginx/sites-available/default
sudo sed -i 's/\[::]:8080 default_server;/\[::]:80 default_server;/g' /etc/nginx/sites-available/default
```

4. Verify Nginx configuration:
```bash
sudo nginx -t
```

## Service Management

### Step 5: Restart both services
```bash
# Stop Nginx first
sudo systemctl stop nginx

# Restart Apache
sudo systemctl restart apache2

# Start Nginx
sudo systemctl start nginx

# Enable Nginx on boot
sudo systemctl enable nginx
```

### Step 6: Verify port assignments
```bash
sudo ss -tlnp | grep -E ':(80|8080)'
```

Expected output:
```
LISTEN 0  511  0.0.0.0:80    0.0.0.0:*  users:(("nginx",...))
LISTEN 0  511  *:8080        *:*        users:(("apache2",...))
```

## Testing

### Test Nginx on port 80
```bash
curl http://localhost
```

### Test Apache on port 8080
```bash
curl http://localhost:8080
```

### Test with verbose headers
```bash
# For Nginx
curl -I http://localhost

# For Apache
curl -I http://localhost:8080
```

## Troubleshooting

### Check service status
```bash
sudo systemctl status nginx
sudo systemctl status apache2
```

### View error logs
```bash
# Nginx error log
sudo tail -f /var/log/nginx/error.log

# Apache error log
sudo tail -f /var/log/apache2/error.log
```

### Fix configuration errors
```bash
# Test Nginx config
sudo nginx -t

# Test Apache config
sudo apache2ctl -t
```

### Kill processes on specific ports
```bash
# Find what's using a port
sudo ss -tlnp | grep :80
sudo lsof -i :80

# Kill process (replace PID)
sudo kill <PID>
```

## Configuration Files Reference

| Service | Config Directory | Default Site |
|---------|------------------|--------------|
| Nginx   | `/etc/nginx/`    | `/etc/nginx/sites-available/default` |
| Apache  | `/etc/apache2/`  | `/etc/apache2/sites-enabled/000-default.conf` |

| Service | Main Config | Ports Config | Document Root |
|---------|-------------|--------------|---------------|
| Nginx   | `/etc/nginx/nginx.conf` | N/A (in site config) | `/var/www/html` |
| Apache  | `/etc/apache2/apache2.conf` | `/etc/apache2/ports.conf` | `/var/www/html` |

## Common Commands

| Action | Command |
|--------|---------|
| Start Nginx | `sudo systemctl start nginx` |
| Stop Nginx | `sudo systemctl stop nginx` |
| Restart Nginx | `sudo systemctl restart nginx` |
| Reload Nginx config | `sudo systemctl reload nginx` |
| Start Apache | `sudo systemctl start apache2` |
| Stop Apache | `sudo systemctl stop apache2` |
| Restart Apache | `sudo systemctl restart apache2` |
| Test Nginx config | `sudo nginx -t` |
| Test Apache config | `sudo apache2ctl -t` |
