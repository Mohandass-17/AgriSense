# 🌱 AgriSense: AI-Powered Farm Management OS

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)
![Google Gemini](https://img.shields.io/badge/AI-Google_Gemini_2.5-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**AgriSense** is an AI-powered agricultural management platform. It acts as a centralized dashboard that synthesizes real-time field telemetry, environmental sensor data, and visual inputs into actionable agronomic commands. 

Instead of a standard CRUD application, this project utilizes a **multi-agent LLM architecture** where isolated AI agents handle specific farm management domains (Irrigation, Disease, Pests, and Yield) while sharing an entity-centric data bus.

---

## 📑 Table of Contents
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#-tech-stack)
- [🚀 Getting Started](#-getting-started)
- [🧠 Architecture Notes](#-architecture-notes)
- [📄 License](#-license)

---

## ✨ Key Features

<div align="center">
  <img width="100%" alt="AgriSense Fleet Overview" src="https://github.com/user-attachments/assets/f1874f05-81ed-4879-80f6-5bd2ecebb583" />
</div>

### 🤖 Multi-Agent Logic Engine
Specialized micro-agents process data for specific agricultural domains:

* 💧 **Irrigation Agent:** Calculates plant available water (PAW) and generates precise watering durations based on soil capacity profiles.
<div align="center">
  <img width="100%" alt="Irrigation Agent Dashboard" src="https://github.com/user-attachments/assets/2ae92447-1b86-4ca6-b5ec-e19c1b58d224" />
</div>

* 🦠 **Disease & Vision Agent:** Analyzes canopy temperature, VPD (Vapor Pressure Deficit), and user-uploaded plant imagery to diagnose fungal and bacterial threats.
<div align="center">
  <img width="100%" alt="Disease & Vision Agent" src="https://github.com/user-attachments/assets/ad884465-67af-4d38-9b40-f609e9f7e608" />
</div>

* 🐛 **Pest Radar:** Cross-references land type, weather patterns, and crop species to assess immediate pest population risks using exponential synergy models.

* 📈 **Yield Forecaster:** Projects base yield vs. potential yield based on applied agronomic recommendations using Liebig's Law of the Minimum.
<div align="center">
  <img width="100%" alt="Yield Forecaster" src="https://github.com/user-attachments/assets/6e31145e-26fd-4a6c-9204-8baffcf82c44" />
</div>

### 📡 Live Story Composer
A background synthesis engine that translates raw sensor arrays across the entire node fleet into a readable, real-time farm narrative.
<div align="center">
  <img width="100%" alt="Live Story Composer" src="https://github.com/user-attachments/assets/f718edfe-3220-4a0c-b07b-f170578d7892" />
</div>

### ⚡ CQRS Pattern
Implements Command Query Responsibility Segregation (CQRS) to separate the read-only global telemetry dashboard from the isolated agent command centers, ensuring a snappy, non-blocking user experience.

---

## 🛠️ Tech Stack

**Frontend (Progressive Web App)**
* **Vanilla JavaScript:** Built without heavy frameworks, utilizing a custom-built, Redux-style Pub/Sub state management engine (`Store.subscribe()`) for lightning-fast DOM updates.
* **Tailwind CSS:** For highly responsive, modern UI styling.
* **HTML5 / FontAwesome:** Lightweight, semantic markup.

**Backend & AI**
* **Python / FastAPI:** High-performance asynchronous REST API routing.
* **Uvicorn:** ASGI web server.
* **Google Gemini 2.5 API:** Powers the LLM reasoning and Vision-Language Model (VLM) image analysis. Includes custom exponential backoff logic to elegantly handle API rate limits (HTTP 429) and server overloads (HTTP 503).

---

## 🚀 Getting Started

Follow these steps to run the AgriSense OS locally on your machine.

**1. Clone the repository**
bash
git clone [https://github.com/Mohandass-17/AgriSense.git](https://github.com/Mohandass-17/AgriSense.git)
cd AgriSense

**2. Create a virtual environment**
Bash
python -m venv .venv
# On Windows: .\.venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate

**3. Install dependencies**

Bash
pip install -r requirements.txt

**4. Set your API Key**
Copy the provided template file to create your local environment variables:

Bash
cp .env.example .env
Open the .env file and replace your_api_key_here with your actual Google Gemini API key.

**5. Run the server**

Bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
Open the Dashboard: Navigate to http://127.0.0.1:8000/ui/agents in your browser.

(Note: If running on a strict institutional network, you may need to apply --trusted-host flags to pip and verify=False to HTTPX configurations).

🧠 Architecture Notes
This project deliberately bypasses standard multi-page HTML routing in favor of a Single-File Micro-Frontend. The entire application is mounted to a single DOM element, allowing the custom JavaScript state engine to render isolated agent tools without ever reloading the browser, mimicking the fast, seamless feel of a native desktop application.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
