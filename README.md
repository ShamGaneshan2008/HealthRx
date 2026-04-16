<div align="center">

<img src="docs/hero.png" alt="HealthRx AI Hero" width="100%"/>

<br/>

# ⚕ HealthRx AI

### AI-Powered Health Guidance Platform

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-00d4ff?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-00ff9d?style=for-the-badge)]()

> **Describe your symptoms. Get instant, AI-powered health guidance.**
> Not a doctor — but the next best thing at 2 AM.

</div>

---

## ✨ What is HealthRx AI?

**HealthRx AI** is a full-stack AI health assistant that lets users describe symptoms in plain language and receive immediate, structured health guidance. Built on a **FastAPI** backend powered by **Groq's ultra-fast LLaMA 3.3** inference, it delivers real-time responses through a sleek, dark-themed chat interface.

> ⚠️ **Disclaimer:** HealthRx AI is an educational tool and does not replace professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.

---

## 🖥️ Screenshots

<div align="center">

### 🏠 Landing Page — Hero Section
<img src="docs/hero.png" alt="HealthRx AI Landing Page" width="90%" style="border-radius: 12px; margin: 16px 0;"/>

*Futuristic dark UI with animated orbs, phone mockup, and live stats*

<br/>

### 💬 AI Symptom Checker — Live Chat
<img src="docs/checker.png" alt="HealthRx AI Symptom Checker" width="90%" style="border-radius: 12px; margin: 16px 0;"/>

*Real-time AI responses via Groq API — routed securely through your FastAPI backend*

</div>

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🤖 **AI Symptom Analysis** | Powered by LLaMA 3.3 70B via Groq for near-instant responses |
| 🔒 **Secure API Routing** | All AI calls go through FastAPI — your API key never touches the browser |
| 💬 **Conversational UI** | Clean chat interface with typing indicators and quick prompts |
| 🚨 **Severity Triage** | Responses classify urgency: mild, moderate, or urgent |
| 📱 **Fully Responsive** | Works on desktop, tablet, and mobile |
| ⚡ **Static File Serving** | FastAPI serves the entire frontend — one server for everything |
| 🌐 **CORS Configured** | Ready for local dev and production deployments |

---

## 🏗️ Project Structure

```
HealthRx/
├── app/
│   ├── core/
│   │   └── config.py          # Settings & environment variables
│   ├── ml/
│   │   ├── model.py           # ML model logic
│   │   └── preprocess.py      # Data preprocessing
│   ├── services/
│   │   ├── drug_service.py    # Drug information service
│   │   └── safety.py          # Safety checks
│   ├── utils/
│   │   └── logger.py          # Logging configuration
│   ├── main.py                # FastAPI app factory & entry point
│   ├── routes.py              # API route definitions (incl. /api/chat)
│   └── schemas.py             # Pydantic request/response models
├── data/
│   ├── drugs.json             # Drug reference data
│   └── symptoms.csv           # Symptom dataset
├── frontend/
│   ├── index.html             # Main UI (served by FastAPI at /)
│   ├── app.js                 # Frontend JavaScript
│   └── style.css              # Styles
├── logs/                      # Application logs
├── .env                       # 🔐 API keys (never commit this!)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com) (free tier available)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/HealthRx.git
cd HealthRx
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

> 🔑 Get your free Groq API key at [console.groq.com](https://console.groq.com)

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

### 6. Open the App

Navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser. That's it!

---

## 🔌 API Reference

### `POST /api/chat`

Send a symptom description and receive AI health guidance.

**Request Body**
```json
{
  "message": "I have a throbbing headache on the right side for the past 3 hours."
}
```

**Response**
```json
{
  "reply": "I'm sorry to hear you're experiencing a headache. Based on your description..."
}
```

**Try it in the browser at:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) *(FastAPI Swagger UI)*

---

## 🧠 How It Works

```
User types symptoms
        ↓
  Browser sends POST /api/chat
        ↓
  FastAPI receives request
        ↓
  Groq API called server-side
  (LLaMA 3.3 70B model)
        ↓
  Structured response returned
        ↓
  Chat UI renders the reply
```

The key design decision: **the Groq API is never called from the browser.** Your API key lives only in `.env` on the server, keeping it completely private.

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — High-performance async Python web framework
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [Groq Python SDK](https://github.com/groq/groq-python) — Ultra-fast LLM inference
- [Pydantic](https://docs.pydantic.dev/) — Data validation & settings management

**Frontend**
- Vanilla HTML/CSS/JavaScript — Zero framework dependencies
- [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) + [Bebas Neue](https://fonts.google.com/specimen/Bebas+Neue) — Typography
- CSS custom properties + animations — Full dark theme with aurora effects

**AI Model**
- `llama-3.3-70b-versatile` via Groq — Selected for speed, accuracy, and free tier availability

---

## 🔐 Security Notes

- ✅ API key stored server-side in `.env` only
- ✅ `.env` should be in `.gitignore` — never commit secrets
- ✅ CORS configured — restrict `allow_origins` for production
- ✅ Input passed directly to AI — consider adding rate limiting for production use

---

## 📦 Requirements

```txt
fastapi
uvicorn[standard]
groq
pydantic-settings
python-dotenv
```

Install everything with:
```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ and a lot of debugging

**[⬆ Back to top](#-healthrx-ai)**

</div>
