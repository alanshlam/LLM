\# Nginx Debugging Lab Manual



\## Problem Description

Nginx failed to start up with the error "Address already in use" on port 80.



\## Debugging Steps



\### Step 1: Check Nginx Service Status

```bash

sudo systemctl status nginx

```

This reveals the error message: `bind() to 0.0.0.0:80 failed (98: Address already in use)`



\### Step 2: Check What's Using Port 80

```bash

sudo ss -tlnp | grep :80

```

Or alternatively:

```bash

sudo netstat -tlnp | grep :80

```



\### Step 3: Identify the Conflicting Process

The output shows Apache2 is listening on port 80:

```

LISTEN 0      511  \*:80  \*:\*  users:(("apache2",pid=4110,fd=4))

```



\### Step 4: Resolution Strategy

Decide which server should use which port. In this case:

\- Nginx should listen on port 80 (default HTTP port)

\- Apache2 should listen on port 8080



\### Step 5: Reconfigure Apache2

Modify Apache's port configuration:



```bash

\# Change Apache to listen on port 8080

sudo sed -i 's/^Listen 80$/Listen 8080/' /etc/apache2/ports.conf

sudo sed -i 's/<VirtualHost \\\*:80>/<VirtualHost \*:8080>/' /etc/apache2/sites-enabled/000-default.conf

```



\### Step 6: Restart Services

```bash

\# Restart Apache with new configuration

sudo systemctl restart apache2



\# Start Nginx

sudo systemctl start nginx

```



\### Step 7: Verify Configuration

```bash

\# Check ports are correctly assigned

sudo ss -tlnp | grep -E ':80|:8080'



\# Test both servers

curl http://localhost        # Should return Nginx response

curl http://localhost:8080   # Should return Apache response

```



\## Common Issues and Solutions



| Error | Cause | Solution |

|-------|-------|----------|

| `bind() failed (98: Address already in use)` | Port already occupied by another process | Stop conflicting service or reconfigure to use different port |

| Service fails to start after config change | Syntax error in config | Run `nginx -t` or `apachectl configtest` to validate |

| Port not visible after restart | Service didn't restart properly | Check status with `systemctl status <service>` |



\## Key Commands Reference



```bash

\# Check service status

systemctl status nginx

systemctl status apache2



\# Check listening ports

ss -tlnp

netstat -tlnp



\# Test configuration

nginx -t

apachectl configtest



\# Restart services

systemctl restart nginx

systemctl restart apache2



\# View logs

journalctl -u nginx

tail -f /var/log/nginx/error.log



