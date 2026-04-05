



# 🕵️‍♂️ Claude Code CLI + Ollama: Private Local AI Agent
**A complete guide, security protocol, and prompt library for building a 100% offline, private AI assistant.**

[![Watch the tutorial on YouTube](https://img.shields.io/badge/Watch_on-YouTube-red?logo=youtube)](https://youtu.be/mKXO0ZvdW6E)

Welcome to the companion repository for my YouTube tutorial! In this project, I demonstrate how to use Anthropic's Claude Code CLI safely routed to a **Local LLM via Ollama**. This allows you to completely automate system tasks, analyze cybersecurity logs, and debug code without sending sensitive data to the cloud.

---

## ⚠️ CRITICAL SECURITY ADVISORY: Claude Code Source Leak
**DO NOT install Version 2.1.88 (The "Leaked" Version).** 

If you suspect your host is compromised by the recent Claude Code source leak, follow these steps immediately to check for the remote access trojan (RAT) and malicious dependencies.

### 1. Check Global NPM Packages
Check for compromised Axios versions or malicious injected dependencies:
```bash
# Check for compromised Axios versions
npm list -g axios

# Check for the malicious injected dependency
npm list -g plain-crypto-js
```

### 2. Check for the Linux Malware Artifact (RAT)
```bash
# Check if the specific malicious payload file exists
ls -la /tmp/ld.py

# Check if the RAT is currently actively running in memory
ps aux | grep ld.py
```

### 3. Check Local Project Directories
If you installed the CLI locally instead of globally, navigate to that directory and search your lockfile for poisoned packages:
```bash
grep -E "axios@1\.14\.1|axios@0\.30\.4|plain-crypto-js@4\.2" package-lock.json
```

🚨 **What to do if you find ANY of these indicators:**
*   **Disconnect immediately:** Take the machine completely offline to sever the RAT's connection to its Command & Control (C2) servers.
*   **Rotate Secrets:** Assume any SSH keys, AWS credentials, environment variables (like `ANTHROPIC_AUTH_TOKEN`, OpenAI API keys), and local passwords have been exfiltrated. Rotate them immediately from a different, clean device.
*   **Wipe and Rebuild:** Because the malware establishes persistence, the safest path forward is to completely format the machine and reinstall your OS.

---

## ⚙️ Installation & Configuration Guide

### 1. Install Claude Code CLI
```bash
curl -fsSL https://claude.ai/install.sh | bash

# Verify installation
claude --version
```

### 2. Verify Ollama Connection
Ensure your local Ollama instance is running:
```bash
curl http://127.0.0.1:11434
```

### 3. Route Claude CLI to Local Ollama
Set the following environment variables to trick the CLI into using your local model instead of the cloud. *(Note: I used `qwen3-coder-next:q8_0` for this demo).*

```bash
export ANTHROPIC_BASE_URL="http://127.0.0.1:11434"
export ANTHROPIC_AUTH_TOKEN="ollama"
export ANTHROPIC_MODEL="qwen3-coder-next:q8_0"
export ANTHROPIC_DEFAULT_SONNET_MODEL="qwen3-coder-next:q8_0"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="qwen3-coder-next:q8_0"
```

---

## 🧠 Recommended Local LLMs

While I used `qwen3-coder-next:q8_0` for the demo, you can use other local LLMs depending on your hardware.

| Use Case | Recommended Model | Strength | VRAM Usage |
| :--- | :--- | :--- | :--- |
| **Primary Coding/Logic** | `qwen2.5-coder:32b` | High speed, high accuracy | Low (~20GB) |
| **Complex Architecture** | `deepseek-coder-v2` | State-of-the-art coding | Medium/High |
| **System Setup/DevOps** | `llama3.1:70b` | Tool use & OS knowledge | High (~40-50GB) |
| **"Impossible" Bugs** | `deepseek-r1:70b` | Deep reasoning / CoT | High (~40-50GB) |
| **Quick Refactors** | `codestral` | Speed and conciseness | Low (~15GB) |

---

## 🚀 Tested Capabilities & Demo Prompts

In this project, the AI agent successfully automated the following tasks locally. Below are the actual prompts used in the demo.

### 📁 1. Private File Management
✅ Organize personal emails, translate, and summarize highly sensitive private data without internet exposure.  

> 💬 `"please extract all email from bob in the demo.mbox and save it to bob.mbox"`  
> 💬 `"please re-organize @mess/ folder by moving different type files into organized folders"`  
> 💬 `"please build a file index of the @mess folder and save it to a file. The index file lists all files with their file size in the folder and sort the largest file size at the top."`  

### 💻 2. Coding & Debugging
✅ Debug and fix code automatically with corrective comments.

> 💬 `"please debug the program @task_manager.py and fix the bug in this program, save the new version of the program into a file"`  

📄 *[Link to the bug program](code/task_manager.py)*    
📄 *[Link to the fixed program](code/task_manager_fixed.py)*    

### 🌐 3. Web Server Setup & Debugging
✅ Set up Apache/Nginx, resolve port conflicts, find root causes, and deploy.  

> 💬 `"please setup apache web server at this host"`  
> 💬 `"please setup nginx server at this host"`  
> 💬 `"please make apache start up with taking up 8080 port"`  
> 💬 `"please make apache2 to listen 443 port as well"`  
> 💬 `"please save the setup steps and tune up steps in a file as lab manual for students"`  
> 💬 `"nginx cannot start up now, please debug it"`  
> 💬 `"Please save how you debug and fix it in a file as lab manual for students"`

📄 *[Link to the Web server setup Lab Manual Document](code/web_setup.md)*    
📄 *[Link to the Web server debuge Lab Manual Document](code/nginx_debug.md)*    


### 🚨 4. Automated Alerting
✅ Build a critical service monitor that triggers a Telegram bot if a service crashes.

> 💬 `"Create a Python monitoring script called monitor.py. It needs to do three things:
> 1. Load configuration variables from a .env file.  
> 2. Check if the web service and mail service are up by examining if the 80, 443, and 25 ports are open.  
> 3. If either service fails or times out, trigger a function that sends a POST request to the Telegram Bot API (https://api.telegram.org/bot<TOKEN>/sendMessage) to alert me."`  

📄 *[Link to the Monitoring Script](code/monitor.py)*  

### 🕵️‍♂️ 5. Cybersecurity & Honeypot Analysis
✅ Analyze hacker keystrokes and get actionable security recommendations.

> 💬 `"you are the security expert, please analyse the keystroke log file s1 and give your recommendation of your findings"`
> 💬 `"please save your findings to a file"`

📄 *[Link to the Findings Report](code/security_analysis.md)*

### 🦠 6. Malware Tracking
✅ Track Antivirus (AV) vendor detections for malware downloaded to the honeypot.

> 💬 `"please read readme.md to understand what this folder for"`
> 💬 `"please submit the hash of the file b12ba38dd1de68e22e910873be32aa13661f43fcc4ba3b1521695c107edd201e to VirusTotal with the VirusTotal API key and compare the return result in vt_reports/ to see if there is any updating"`
> 💬 `"please save your findings to a file"`

📄 *[Link to the Malware Report](code/VT_Report_Comparison_2026-04-01.md)*

---

## 🛡️ Recommendations for Safe Usage

*   **Use a Sandbox:** Never run an AI agent (local or cloud) directly on your primary OS with full admin privileges. Use a Docker container, a Virtual Machine (VM), or a dedicated development environment (like VS Code Dev Containers).
*   **Review Commands:** Never set the tool to "auto-approve" commands. Always read the shell command the AI wants to run before hitting `Enter`.
*   **Model Capability Constraints:** Be aware that local models via Ollama may occasionally struggle with the complex "tool-use" (function calling) syntax that Claude Code expects. This may lead to more errors or unpredictable behavior compared to using the official cloud API.
```
