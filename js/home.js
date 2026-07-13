const API_BASE = "";

const endpoints = {
  health: "/health",
  agents: "/agents/status",
  devices: "/memory/devices",
  llmChat: "/llm/chat",
};

const chatFallbackText = "Ask the LLM anything about your field, and it will respond like a human planner.";
const chatState = { sessionId: null };

async function safeFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Request failed (${response.status}): ${errorBody}`);
  }
  return response.json();
}

function updateStatus(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function updateHealthStatus(value) {
  updateStatus("health-status-value", value);
  updateStatus("badge-health-value", value);
}

function updateAgentStatus(value) {
  updateStatus("agent-status-value", value);
  updateStatus("badge-agent-value", value);
}

function updateDeviceStatus(value) {
  updateStatus("badge-device-value", value);
}

function renderAgentsPreview(list) {
  const container = document.getElementById("agents-preview");
  if (!container) return;
  container.innerHTML = "";
  (list || []).slice(0, 6).forEach((agent) => {
    const li = document.createElement("li");
    li.textContent = agent.name;
    container.appendChild(li);
  });
  if (!list.length) container.innerHTML = "<li>No agents registered yet.</li>";
}

function renderDevicesPreview(list) {
  const container = document.getElementById("devices-preview");
  if (!container) return;
  container.innerHTML = "";
  (list || []).slice(0, 6).forEach((device) => {
    const li = document.createElement("li");
    li.textContent = device;
    container.appendChild(li);
  });
  if (!list.length) container.innerHTML = "<li>No devices tracked yet.</li>";
}

function appendChatMessage(role, text) {
  const chatWindow = document.getElementById("llm-chat-window");
  if (!chatWindow || !text) return;
  const fallback = chatWindow.querySelector(".fallback");
  if (fallback) fallback.remove();
  
  const bubble = document.createElement("div");
  bubble.className = `chat-message ${role}`;
  bubble.innerHTML = role === "user" ? `<strong>You:</strong> ${text}` : `<strong>AgriSense:</strong> ${text}`;
  
  // Accessibility: Mark error bubbles as alerts for screen readers
  if (text.includes("System Error") || text.includes("Oops")) {
     bubble.setAttribute("role", "alert");
  }
  
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function resetChatWindow() {
  const chatWindow = document.getElementById("llm-chat-window");
  if (!chatWindow) return;
  chatWindow.innerHTML = `<p class="fallback">${chatFallbackText}</p>`;
  chatState.sessionId = null;
}

async function bootstrapStatus() {
  try {
    const [health, agents, devices] = await Promise.all([
      safeFetch(endpoints.health),
      safeFetch(endpoints.agents),
      safeFetch(endpoints.devices),
    ]);

    updateHealthStatus(health.status || "Ready");
    updateAgentStatus(agents.total_agents?.toString() || agents.agents?.length?.toString() || "0");
    updateDeviceStatus(devices.devices?.length?.toString() || "0");
    renderAgentsPreview(agents.agents || []);
    renderDevicesPreview(devices.devices || []);
    resetChatWindow();
  } catch (error) {
    updateHealthStatus("Offline");
    console.error(error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  bootstrapStatus();

  const llmForm = document.getElementById("llm-form");
  const chatWindow = document.getElementById("llm-chat-window");
  
  if (chatWindow) {
      // Accessibility: Make the chat window announce new messages dynamically
      chatWindow.setAttribute("aria-live", "polite");
      chatWindow.setAttribute("aria-relevant", "additions");
  }

  if (!llmForm) return;

  llmForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(llmForm);
    const questionInput = llmForm.querySelector('textarea[name="question"]');
    const submitBtn = llmForm.querySelector('button[type="submit"]');
    
    const question = formData.get("question")?.toString().trim();
    if (!question) return;

    // 1. Instantly clear input and disable form elements
    if (questionInput) {
        questionInput.value = '';
        questionInput.disabled = true;
    }
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Thinking...';
        submitBtn.setAttribute("aria-busy", "true");
    }

    const payload = { question };
    const crop = formData.get("crop_type")?.toString().trim();
    const location = formData.get("location")?.toString().trim();
    if (crop) payload.crop_type = crop;
    if (location) payload.location = location;
    if (chatState.sessionId) payload.session_id = chatState.sessionId;

    // 2. Append user message
    appendChatMessage("user", question);

    // 3. Show Accessible Thinking indicator
    const thinkingId = "thinking-" + Date.now();
    const thinkingBubble = document.createElement("div");
    thinkingBubble.className = "chat-message assistant";
    thinkingBubble.id = thinkingId;
    thinkingBubble.innerHTML = "<em style='color: #666;'>AgriSense is thinking...</em>";
    chatWindow.appendChild(thinkingBubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
      const response = await safeFetch(endpoints.llmChat, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      document.getElementById(thinkingId)?.remove();
      chatState.sessionId = response.session_id;
      // Adjust property check based on normalisation output
      appendChatMessage("assistant", response.text || response.reply || JSON.stringify(response));
      
    } catch (error) {
      document.getElementById(thinkingId)?.remove();
      appendChatMessage("assistant", `<span style="color: red;">System Error: ${error.message}</span>`);
    } finally {
        // 4. Accessibility: Re-enable the inputs and return focus to the text area
        if (questionInput) {
            questionInput.disabled = false;
            questionInput.focus();
        }
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Ask LLM';
            submitBtn.removeAttribute("aria-busy");
        }
    }
  });

  const resetButton = document.getElementById("chat-reset");
  if (resetButton) {
    resetButton.addEventListener("click", () => {
      resetChatWindow();
      llmForm.reset();
    });
  }
});