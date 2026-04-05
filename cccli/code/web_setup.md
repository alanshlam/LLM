# Web Server Setup Lab Manual

## Overview

This lab demonstrates how to set up and configure Apache2 and Nginx web servers on Ubuntu. Students will learn to:
- Install and configure Apache2
- Configure Apache to listen on multiple ports (8080, 443)
- Enable SSL/TLS encryption
- Install and configure Nginx

---

## Part 1: Apache2 Web Server Setup

### Step 1: Install Apache2

```bash
sudo apt-get update
sudo apt-get install -y apache2
```

### Step 2: Start Apache Service

```bash
sudo systemctl start apache2
sudo systemctl enable apache2
sudo systemctl status apache2
```

### Step 3: Verify Installation

```bash
curl http://localhost
# or test HTTP status
curl -s -o /dev/null -w "%{http_code}" http://localhost
```

**Default locations:**
- Document root: `/var/www/html`
- Main config: `/etc/apache2/apache2.conf`
- Port config: `/etc/apache2/ports.conf`
- Available sites: `/etc/apache2/sites-available/`
- Enabled sites: `/etc/apache2/sites-enabled/`

---

## Part 2: Apache Port Configuration

### Change Default Port (80 → 8080)

```bash
# Edit ports.conf to change Listen directive
sudo sed -i 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf

# Restart Apache to apply changes
sudo systemctl restart apache2
```

### Test on Port 8080

```bash
curl http://localhost:8080
```

---

## Part 3: SSL/TLS Configuration

### Enable SSL Module

```bash
sudo a2enmod ssl
```

### Enable Default SSL Site

```bash
sudo a2ensite default-ssl
sudo systemctl restart apache2
```

### Verify SSL is Working

```bash
curl -k https://localhost:443
# or test HTTPS status
curl -s -k -o /dev/null -w "%{http_code}" https://localhost:443
```

### SSL Certificate Information

- Default self-signed certificate: `/etc/ssl/certs/ssl-cert-snakeoil.pem`
- Private key: `/etc/ssl/private/ssl-cert-snakeoil.key`

---

## Part 4: Nginx Web Server Setup

### Install Nginx

```bash
sudo apt-get install -y nginx
```

### Start Nginx Service

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

**Default locations:**
- Document root: `/var/www/html`
- Main config: `/etc/nginx/nginx.conf`
- Site configs: `/etc/nginx/sites-available/`
- Enabled sites: `/etc/nginx/sites-enabled/`

### Test Nginx

```bash
curl http://localhost
```

---

## Part 5: Port Conflict Resolution

**Note:** Only one web server can listen on port 80 at a time.

To switch from Nginx to Apache on port 80:
```bash
sudo systemctl stop nginx
sudo systemctl start apache2
```

To switch from Apache to Nginx on port 80:
```bash
sudo systemctl stop apache2
sudo systemctl start nginx
```

---

## Common Apache Commands

| Command | Description |
|---------|-------------|
| `sudo systemctl start apache2` | Start Apache |
| `sudo systemctl stop apache2` | Stop Apache |
| `sudo systemctl restart apache2` | Restart Apache |
| `sudo systemctl reload apache2` | Reload configuration |
| `sudo systemctl status apache2` | Check status |
| `sudo a2enmod [module]` | Enable module |
| `sudo a2dismod [module]` | Disable module |
| `sudo a2ensite [site]` | Enable site |
| `sudo a2dissite [site]` | Disable site |

---

## Common Nginx Commands

| Command | Description |
|---------|-------------|
| `sudo systemctl start nginx` | Start Nginx |
| `sudo systemctl stop nginx` | Stop Nginx |
| `sudo systemctl restart nginx` | Restart Nginx |
| `sudo systemctl reload nginx` | Reload configuration |
| `sudo nginx -t` | Test configuration syntax |

---

## Lab Questions

1. What is the default document root for Apache and Nginx?
2. How do you check which ports a web server is listening on?
3. What command enables SSL in Apache?
4. Why can't Apache and Nginx run simultaneously on the same port?
5. Where are Apache modules stored?

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 80
sudo lsof -i :80
# or
sudo ss -tlnp | grep :80
```

### Apache Configuration Test

```bash
sudo apachectl configtest
```

### Nginx Configuration Test

```bash
sudo nginx -t
```

### View Logs

```bash
# Apache access log
tail -f /var/log/apache2/access.log

# Apache error log
tail -f /var/log/apache2/error.log

# Nginx access log
tail -f /var/log/nginx/access.log

# Nginx error log
tail -f /var/log/nginx/error.log
```
