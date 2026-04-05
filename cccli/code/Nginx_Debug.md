# Web Server Debugging Lab Manual

## Common Issues and Solutions

### Issue 1: Port Already in Use

**Error:**
```
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
```

**Cause:** Another service (Apache) is already bound to the port Nginx wants to use.

**Solution:**
```bash
# Check what's using the port
sudo ss -tlnp | grep :80
# or
sudo netstat -tlnp | grep :80

# Fix the conflicting service (e.g., change Apache's port)
sudo sed -i 's/^Listen 80$/Listen 8080/' /etc/apache2/ports.conf

# Restart the conflicting service
sudo systemctl restart apache2

# Now start Nginx
sudo systemctl start nginx
```

---

### Issue 2: Service Won't Start

**Error:**
```
Job for nginx.service failed because the control process exited with error code.
```

**Debug Steps:**

1. **Check service status:**
```bash
sudo systemctl status nginx
```

2. **View detailed logs:**
```bash
sudo journalctl -xeu nginx.service
# or
sudo cat /var/log/nginx/error.log
```

3. **Test configuration syntax:**
```bash
# Apache
sudo apachectl configtest

# Nginx
sudo nginx -t
```

4. **Check all listening ports:**
```bash
sudo ss -tlnp
```

---

### Issue 3: Configuration Changes Not Applied

**Symptom:** Service appears to be running but not using updated configuration.

**Cause:** Service needs to be restarted (not just reloaded) after certain configuration changes.

**Solution:**
```bash
# Reload configuration (for minor changes)
sudo systemctl reload apache2

# Full restart (required for port changes)
sudo systemctl restart apache2
```

---

## Debugging Commands Reference

| Command | Purpose |
|---------|---------|
| `sudo systemctl status [service]` | Check if service is running |
| `sudo systemctl start [service]` | Start a service |
| `sudo systemctl stop [service]` | Stop a service |
| `sudo systemctl restart [service]` | Restart a service |
| `sudo systemctl reload [service]` | Reload configuration |
| `sudo ss -tlnp` | List all listening TCP ports |
| `sudo netstat -tlnp` | Alternative to ss (may need net-tools) |
| `sudo apachectl configtest` | Test Apache config syntax |
| `sudo nginx -t` | Test Nginx config syntax |
| `tail -f /var/log/apache2/error.log` | Watch Apache errors |
| `tail -f /var/log/nginx/error.log` | Watch Nginx errors |

---

## Troubleshooting Scenarios

### Scenario A: Cannot access web server

1. Check if service is running: `sudo systemctl status apache2`
2. Check if port is open: `sudo ss -tlnp | grep :8080`
3. Test locally: `curl http://localhost:8080`
4. Check firewall: `sudo ufw status`
5. View error logs: `tail -f /var/log/apache2/error.log`

### Scenario B: Multiple web servers installed

**Problem:** Unpredictable behavior when starting services.

**Solution:** Uninstall the unwanted server:
```bash
# Remove Nginx
sudo apt-get remove --purge nginx

# Or remove Apache
sudo apt-get remove --purge apache2
```

### Scenario C: Port configuration not taking effect

1. Verify the config file was edited:
```bash
cat /etc/apache2/ports.conf
```

2. Check for duplicate Listen directives:
```bash
grep -r "Listen 80" /etc/apache2/
```

3. Restart the service (not reload):
```bash
sudo systemctl restart apache2
```

---

## Lab Exercises

1. **Exercise 1:** Both Apache and Nginx are installed. Apache is on port 8080, Nginx on port 80. What commands would you use to switch them?

2. **Exercise 2:** After editing Apache's ports.conf, the service still doesn't listen on the new port. What steps would you take to debug?

3. **Exercise 3:** A student reports "Connection refused" when trying to access http://localhost. List all possible causes and debugging steps.