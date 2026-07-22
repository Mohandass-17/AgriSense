# AgriSense 🌱

**AgriSense** is an AI-powered agricultural management platform. It acts as a centralized dashboard that synthesizes real-time field telemetry, environmental sensor data, and visual inputs into actionable agronomic commands. 

Instead of a standard CRUD application, this project utilizes a **multi-agent LLM architecture** where isolated AI agents handle specific farm management domains (Irrigation, Disease, Pests, and Yield) while sharing an entity-centric data bus.

## ✨ Key Features

<img width="1912" height="930" alt="Screenshot 2026-07-21 145942" src="https://github.com/user-attachments/assets/f1874f05-81ed-4879-80f6-5bd2ecebb583" />

* **Multi-Agent Logic Engine:** Specialized micro-agents process data for specific domains:
  * 💧 **Irrigation Agent:** Calculates plant available water (PAW) and generates precise watering durations.

<img width="1919" height="942" alt="Screenshot 2026-07-21 150659" src="https://github.com/user-attachments/assets/2ae92447-1b86-4ca6-b5ec-e19c1b58d224" />

  * 🦠 **Disease & Vision Agent:** Analyzes canopy temperature, VPD (Vapor Pressure Deficit), and user-uploaded plant imagery to diagnose fungal and bacterial threats.

<img width="1919" height="941" alt="Screenshot 2026-07-21 150628" src="https://github.com/user-attachments/assets/ad884465-67af-4d38-9b40-f609e9f7e608" />

  * 🐛 **Pest Radar:** Cross-references land type, weather mood, and crop type to assess immediate pest risks.
  * 📈 **Yield Forecaster:** Projects base yield vs. potential yield based on applied agronomic recommendations.

<img width="1919" height="944" alt="Screenshot 2026-07-21 150605" src="https://github.com/user-attachments/assets/6e31145e-26fd-4a6c-9204-8baffcf82c44" />

* **Live Story Composer:** A background synthesis engine that translates raw sensor arrays across the entire node fleet into a readable, real-time farm narrative.

<img width="1919" height="946" alt="Screenshot 2026-07-21 145907" src="https://github.com/user-attachments/assets/f718edfe-3220-4a0c-b07b-f170578d7892" />

* **Command Query Responsibility Segregation (CQRS) Pattern:** Separates the read-only global telemetry dashboard from the isolated agent command centers, ensuring a snappy, non-blocking user experience.

## 🛠️ Tech Stack

### Frontend (Progressive Web App)
* **Vanilla JavaScript:** Built without heavy frameworks, utilizing a custom-built, Redux-style Pub/Sub state management engine (`Store.subscribe()`) for lightning-fast DOM updates.
* **Tailwind CSS:** For highly responsive, modern UI styling.
* **HTML5 / FontAwesome:** Lightweight, semantic markup.

### Backend & AI
* **Python / FastAPI:** High-performance asynchronous REST API routing.
* **Uvicorn:** ASGI web server.
* **Google Gemini 2.5 API:** Powers the LLM reasoning and Vision-Language Model (VLM) image analysis. Includes custom exponential backoff logic to elegantly handle API rate limits (HTTP 429) and server overloads (HTTP 503).

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/agrisense.git](https://github.com/yourusername/agrisense.git)
   cd agrisense

 2. **Install dependencies:**

  Bash
   pip install fastapi uvicorn google-generativeai

 3. **Set your API Key:**
  Ensure you have your Google Gemini API key configured in your environment variables.
  Bash
   export GEMINI_API_KEY="your_api_key_here"
 
 4. **Run the server:**

  Bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   
Open the Dashboard: Navigate to http://127.0.0.1:8000/agents in your browser.

🧠 **Architecture Notes**

   This project deliberately bypasses standard multi-page HTML routing in favor of a Single-File Micro-Frontend. The entire application is mounted to a single, allowing the custom JavaScript state engine to render isolated agent tools without ever reloading the browser, mimicking the feel of a native desktop application.

Add this section to the bottom of your README.mdl

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


