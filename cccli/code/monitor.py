#!/usr/bin/env python3
"""Service monitoring script with Telegram alerts."""

import os
import socket
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


def load_config():
    """Load configuration from .env file."""
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    return {
        "telegram_token": os.getenv("TELEGRAM_TOKEN"),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "hosts": os.getenv("HOSTS", "localhost").split(","),
    }


def check_port(host: str, port: int, timeout: float = 5.0) -> bool:
    """Check if a port is open on the given host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except (socket.timeout, socket.error):
        return False


def check_services():
    """Check if web and mail services are up."""
    results = {
        "web_service": False,
        "mail_service": False,
        "details": {},
    }

    hosts = os.getenv("HOSTS", "localhost").split(",")

    # Web service: ports 80, 443
    for host in hosts:
        for port in [80, 443]:
            key = f"{host}:{port}"
            results["details"][key] = check_port(host.strip(), port)

    web_ports_open = any(
        check_port(host.strip(), port)
        for host in hosts
        for port in [80, 443]
    )
    results["web_service"] = web_ports_open

    # Mail service: port 25
    for host in hosts:
        key = f"{host}:25"
        results["details"][key] = check_port(host.strip(), 25)

    mail_port_open = any(
        check_port(host.strip(), 25)
        for host in hosts
    )
    results["mail_service"] = mail_port_open

    return results


def send_telegram_alert(message: str, token: str, chat_id: str) -> bool:
    """Send a message to Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Failed to send Telegram alert: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    config = load_config()

    token = config["telegram_token"]
    chat_id = config["chat_id"]

    if not token or not chat_id:
        print("Error: TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set in .env", file=sys.stderr)
        sys.exit(1)

    print("Checking services...")
    results = check_services()

    alerts = []

    # Check each port individually
    port_25_down = not results["details"].get("localhost:25", True)
    port_80_down = not results["details"].get("localhost:80", True)
    port_443_down = not results["details"].get("localhost:443", True)

    if port_25_down:
        alerts.append("❌ <b>Mail Service</b> is DOWN (port 25)")
    if port_80_down:
        alerts.append("❌ <b>Web Service</b> port 80 is DOWN")
    if port_443_down:
        alerts.append("❌ <b>Web Service</b> port 443 is DOWN")

    if alerts:
        message = "<b>🚨 Service Alert</b>\n\n" + "\n".join(alerts)
        message += "\n\n<code>" + "\n".join(f"{k}: {'UP' if v else 'DOWN'}" for k, v in results["details"].items()) + "</code>"

        print("Services are down. Sending alert...")
        success = send_telegram_alert(message, token, chat_id)
        if success:
            print("Alert sent successfully.")
        else:
            print("Failed to send alert.", file=sys.stderr)
            sys.exit(1)
    else:
        print("All services are UP.")
        print("\nPort status:")
        for k, v in results["details"].items():
            status = "UP" if v else "DOWN"
            print(f"  {k}: {status}")


if __name__ == "__main__":
    main()
