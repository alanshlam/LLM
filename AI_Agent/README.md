# 📂 Personal AI Agent Study Folder – Overview  

This folder is a **study hub for personal AI agents** – a place to explore, build, and experiment with privacy‑first, zero‑cloud assistants such as the **Sovereign Agent** and the **Private Video Agent**.  

| 🤖 Agent | ✨ What it does | 🛠️ Tech stack | 🔐 Why it matters |
|----------|----------------|---------------|-------------------|
| [**Sovereign Agent**](sovereign) [![Watch the tutorial on YouTube](https://img.shields.io/badge/Watch_on-YouTube-red?logo=youtube)](https://youtu.be/McFIOla9jq4) | Reads local `.mbox` emails, `.csv` finances, `.md` schedules, live weather, traffic‑camera snapshots, and a daily news podcast; compiles a concise briefing and pushes it to a private Telegram bot. | Python 3.8+, **Gemma‑4 31B** (Ollama), **LLaVA/qwen3‑vl** (vision), **Whisper** (audio). | **100 % local privacy** – no data ever leaves your computer. |
| [**Private Video Agent**](v_agent)[![Watch the tutorial on YouTube](https://img.shields.io/badge/Watch_on-YouTube-red?logo=youtube)](https://youtu.be/eXZuwvE-lDI)
| Extracts frames, transcribes audio, and performs deterministic “needle‑in‑a‑haystack” searches across video files, all on‑premise. | **Gemma‑4 31B** (or Gemma‑431B) via Ollama, **Claude‑Code CLI**, **ffprobe/ffmpeg**, **Whisper**. | **Zero data leakage** – the model, video files, and tooling stay behind your firewall. |
| [**Claude Code CLI + Ollama**](../cccli) [![Watch the tutorial on YouTube](https://img.shields.io/badge/Watch_on-YouTube-red?logo=youtube)](https://youtu.be/mKXO0ZvdW6E) | Routes Anthropic’s Claude Code CLI to a locally‑hosted LLM, allowing fully offline automation of system tasks, code debugging, web‑server setup, cybersecurity log analysis, and other sensitive operations. | Claude Code CLI, Ollama (e.g., `qwen3‑coder‑next:q8_0` or other recommended models), environment‑variable routing, standard OS tools (apache,nginx,lsof -Pi,ss -tulpn, etc.) | Delivers a **completely private, sandboxable AI assistant** that never contacts external APIs, protecting credentials and confidential data while still offering powerful tool‑use capabilities.|

## ✨ Key Features (at a glance)  
**🔒 Local‑only processing** for all  agents.  

### 🤖 [Sovereign Agent](sovereign) [![Watch the tutorial on YouTube](https://img.shields.io/badge/Watch_on-YouTube-red?logo=youtube)](https://youtu.be/McFIOla9jq4)
🔒 **100 % Local Privacy** – processes .mbox, .csv, and .md files on‑device only.   
🧠 **Contextual Reasoning** – (Gemma4) instead of simple retrieval, the LLM reasons about weather, finance, and schedule (e.g., suggests moving an outdoor lunch indoors if rain is forecast).     
👁️ **Vision AI** (LLaVA/gemma4:e4b/qwen3‑vl:32) for analyzing live CCTV snapshots;  
👂 **Audio AI** – Whisper transcribes daily news podcasts locally and summarize it.  
📱 **Secure Push Delivery** – HTML‑styled briefing sent via a private Telegram bot. 

### 🤖 [Private AI Video Agent](v_agent) [![Watch the tutorial on YouTube](https://img.shields.io/badge/Watch_on-YouTube-red?logo=youtube)](https://youtu.be/eXZuwvE-lDI)
📸 **Frame Extraction & Visual Analysis** – ffprobe/ffmpeg sample key frames, then image analysis by Gemma4:32b.   
🔊 **Audio‑to‑Text** – Whisper transcribes video audio for multimodal sync.   
🎞️ **Video analysis** - Video frame and transcript analysis by Gemma4:32b  
🕵️‍♀️ Needle‑in‑a‑Haystack Search – deterministic matching of frames or spoken terms across many videos.   
🚫 Zero Data Leakage – everything runs on an air‑gapped workstation (no external API calls).   
📈 256 K‑token Context Window – lets the model keep the full transcript + visual cues in memory. 

### 🤖 [Claude Code CLI + Ollama agent](../cccli)  [![Watch the tutorial on YouTube](https://img.shields.io/badge/Watch_on-YouTube-red?logo=youtube)](https://youtu.be/mKXO0ZvdW6E) 
✅ **100 % offline, private AI assistant** – all reasoning, tool‑use, and data processing stay on the local machine; no data is sent to the cloud [3].  
🛠️ **Claude Code CLI routed to a local LLM via Ollama** – the CLI is tricked into using a locally hosted model (e.g., `qwen3‑coder‑next:q8_0`) instead of Anthropic’s cloud endpoint [3].  
📂 **Automates system‑level tasks** – file management, code debugging, web‑server setup, service monitoring, and more, all driven by natural‑language prompts [3].  
🔐 **Secure by design** – includes a critical security advisory about a known source‑leak version and step‑by‑step checks for compromised NPM packages, Linux malware artifacts, and poisoned dependencies.  
🤖 **Broad capability set** (demo prompts)  
  - Private file organization & indexing  
  - Automatic code debugging & fixing  
  - Web‑server provisioning & troubleshooting (Apache/Nginx)  
  - Service‑health monitoring with Telegram alerts  
  - Cyber‑security log analysis and honeypot reporting  
  - Malware hash submission to VirusTotal.
       
🧠 **Recommended local LLMs** for different workloads (coding, architecture, DevOps, refactoring, prototypes).     
🛡️ **Safety recommendations** – run inside a sandbox/VM, always review generated shell commands, and be aware of occasional tool‑use syntax mismatches with local models.  


---

# [🤖 The Sovereign Agent | Zero-Cloud Personal AI Dashboard](sovereign)
🚀📂✨ **The Sovereign Agent** – a privacy‑first, zero‑cloud personal AI dashboard that **🔒 processes your local 📧 .mbox emails, 📊 expenses.csv finances, 📅 schedule.md calendars, ☁️ live weather APIs, 🚦 traffic‑camera snapshots, and 🎙️ news podcasts** entirely on‑device, then compiles a concise, mobile‑friendly briefing and delivers it straight to your 📲 Telegram inbox — all while keeping your data 100 % local and never sending anything to external services.

--- 

# [🛡️ Private AI Agent – Secure Video Analysis & Search with Gemma‑4 31B & Claude Code CLI](v_agent)  
This study demonstrates how to turn **Gemma‑4 31B** into a fully **air‑gapped, private AI agent** powered by the **Claude Code CLI** 🚀. By running the entire stack locally (via Ollama) you can analyze sensitive video and technical data with **zero data leakage** 🚫☁️, keeping everything behind your firewall 🏠. The agent leverages native tool‑use proficiency (ffprobe, ffmpeg, Whisper) 🛠️, deep “Thinking Mode” chain‑of‑thought verification 🧠, and a massive 256 K‑token context window 📚 to perform multimodal video reasoning and needle‑in‑a‑haystack searches 🕵️‍♀️—all at $0 API cost 💰.  

---

# [🚀 Private Local AI Agent (Claude Code + Ollama)](../cccli)
Stop leaking your sensitive data, source code, and security logs to the cloud. I've built a complete workflow that integrates the Claude Code CLI with local Ollama models to create a powerful, 100% offline AI assistant. This project demonstrates how to securely automate DevOps tasks, debug complex code, organize private files, and perform advanced cybersecurity threat intel (like honeypot and malware analysis) right on your local machine.

---  

## 📂 Repository Layout  

```
AI_Agent/
├── README.md
├── sovereign/
│   ├── README.md
│   └── code/
│       ├── ai_agent_dds.py
│       ├── AI_agent_infograph.jpg
│       ├── ai_agent.py
│       ├── .env_sample
│       ├── expenses.csv
│       ├── inbox.mbox
│       ├── output_sample.jpg
│       ├── README.md
│       ├── schedule.md
│       ├── tasks.md
│       └── TC001F.JPG
└── v_agent/
    ├── README.md
    ├── infograph/
    │   ├── AI_vagent_infograph04.jpg
    │   ├── ai_video_agent_case_study.jpg
    │   ├── Gemma4_model_com2.png
    │   └── README.md
    ├── vanalysis/
    │   ├── ch1_analysis.md
    │   ├── frame_0003.jpg
    │   ├── lena_analysis3.md
    │   ├── lisa_analysis.md
    │   ├── README.md
    │   ├── scarf.md
    │   └── video_analysis_prompt.txt
    └── vsearch/
        ├── frame_ch10_001.jpg
        ├── frame_ch20_001.jpg
        ├── frame_ch20_002.jpg
        ├── README.md
        ├── unknown.jpg
        ├── Video_identification_process.md
        └── video_search_walkthrough.txt

```
--- 

Infographic : Privacy-First AI Agents: Zero-Cloud Study
<div style="height: 200px; overflow-y: scroll;">
  <img src="../screenshot/private_AI.png" width="100%"><br>
 
</div>


---

## 📞 Contact  

For questions, issues, or collaboration proposals, please open an issue or contact the maintainer at `alanlam28@gmail.com`.  


---

