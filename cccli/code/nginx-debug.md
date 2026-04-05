# Nginx Debug and Fix

## Problem
Nginx failed to start up.

## Debug Steps

1. **Test configuration syntax**
   ```
   nginx -t
   ```
   Result: Configuration syntax is ok, but permission error on `/run/nginx.pid`

2. **Test with sudo**
   ```
   sudo nginx -t
   ```
   Result: Configuration is valid

3. **Attempt to start nginx**
   ```
   sudo nginx
   ```
   Result: Error - `bind() to 0.0.0.0:80 failed (98: Address already in use)`

4. **Check what's using port 80**
   ```
   sudo ss -tlnp | grep :80
   ```
   Result: Apache2 is already running (pids: 7528-7532, 5956)

## Fix
```
sudo systemctl stop apache2
sudo systemctl start nginx
```

## Result
Nginx is now active (running).

## Root Cause
Port 80 was already bound by Apache2, preventing nginx from binding to the same port.
