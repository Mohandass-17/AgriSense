/**
 * AgriSense Pro - Progressive Web App Client
 * Architecture: Central State Store -> UI Components -> API Gateway
 */

const API_BASE = "";

// ==========================================
// 1. CENTRAL STATE MANAGEMENT (The "Brain")
// ==========================================
const API_BASE = "";

// ==========================================
// 1. CENTRAL STATE MANAGEMENT
// ==========================================
const Store = {
    state: {
        activeTab: 'overview',
        syncStatus: 'Cloud Sync Active',
        metrics: { moisture: 38, temp: 26, humidity: 65, vpd: 1.4, crop: 'Wheat', health: 'Optimal' },
        chatHistory: [{ role: 'ai', text: 'System online. Edge connectivity established.' }],
        isProcessing: false
    },
    listeners: [],
    getState() { return this.state; },
    setState(newState) { this.state = { ...this.state, ...newState }; this.notify(); },
    updateMetric(key, value) { this.state.metrics[key] = value; this.notify(); },
    subscribe(listener) { this.listeners.push(listener); },
    notify() { this.listeners.forEach(listener => listener(this.state)); }
};

// FORCE the store to be globally visible to the HTML buttons
window.Store = Store;

// ==========================================
// 2. API SERVICE LAYER
// ==========================================
class APIService {
    static async post(endpoint, payload) {
        Store.setState({ isProcessing: true, syncStatus: 'Syncing...' });
        try {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            Store.setState({ syncStatus: 'Cloud Sync Active' });
            return await res.json();
        } catch (error) {
            Store.setState({ syncStatus: 'Offline / Error' });
            throw error;
        } finally {
            Store.setState({ isProcessing: false });
        }
    }
}

// ==========================================
// 3. UI COMPONENTS
// ==========================================

function Sidebar(state) {
    const tabs = [
        { id: 'overview', icon: 'fa-chart-pie', label: 'Overview' },
        { id: 'irrigation', icon: 'fa-droplet', label: 'Irrigation' },
        { id: 'ai', icon: 'fa-robot', label: 'AI Assistant' }
    ];

    const navItems = tabs.map(tab => `
        <button onclick="Store.setState({activeTab: '${tab.id}'})" 
                class="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${state.activeTab === tab.id ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'}">
            <i class="fa-solid ${tab.icon} w-5"></i>
            <span class="hidden md:block">${tab.label}</span>
        </button>
    `).join('');

    return `
        <aside class="hidden md:flex flex-col w-64 bg-white border-r border-slate-200 h-full p-4 z-20 shadow-sm">
            <div class="flex items-center gap-2 mb-8 px-2 text-emerald-700">
                <i class="fa-solid fa-leaf text-2xl"></i>
                <h1 class="text-xl font-black tracking-tight">AgriSense<span class="font-light">OS</span></h1>
            </div>
            <nav class="flex-1 flex flex-col gap-2">
                ${navItems}
            </nav>
            <div class="mt-auto px-2 py-4 border-t border-slate-100 flex items-center gap-2 text-xs font-semibold ${state.syncStatus.includes('Error') ? 'text-red-500' : 'text-slate-400'}">
                <div class="w-2 h-2 rounded-full ${state.syncStatus.includes('Error') ? 'bg-red-500' : 'bg-emerald-500 animate-pulse'}"></div>
                ${state.syncStatus}
            </div>
        </aside>

        <nav class="md:hidden fixed bottom-0 w-full bg-white border-t border-slate-200 flex justify-around pb-6 pt-2 px-2 z-50 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
            ${tabs.map(tab => `
                <button onclick="Store.setState({activeTab: '${tab.id}'})" 
                        class="flex flex-col items-center gap-1 p-2 w-20 transition-colors ${state.activeTab === tab.id ? 'text-emerald-600' : 'text-slate-400'}">
                    <i class="fa-solid ${tab.icon} text-xl mb-1 ${state.activeTab === tab.id ? 'transform scale-110 transition-transform' : ''}"></i>
                    <span class="text-[10px] font-bold uppercase tracking-wider">${tab.label}</span>
                </button>
            `).join('')}
        </nav>
    `;
}

function OverviewTab(state) {
    const m = state.metrics;
    return `
        <div class="max-w-5xl mx-auto animate-[fadeIn_0.3s_ease-out]">
            <header class="mb-8">
                <h2 class="text-2xl font-bold text-slate-800">Farm Overview</h2>
                <p class="text-slate-500 text-sm mt-1">Real-time metrics for ${m.crop} sectors.</p>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 relative overflow-hidden">
                    <div class="absolute top-0 right-0 p-4 opacity-10"><i class="fa-solid fa-droplet text-6xl"></i></div>
                    <h3 class="text-slate-500 text-sm font-bold uppercase tracking-wider mb-2">Soil Moisture</h3>
                    <div class="text-4xl font-black text-slate-800 mb-2">${m.moisture}<span class="text-xl text-slate-400">%</span></div>
                    <div class="text-sm font-semibold ${m.moisture < 40 ? 'text-amber-500' : 'text-emerald-500'}">
                        ${m.moisture < 40 ? 'Action Recommended' : 'Optimal Level'}
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 relative overflow-hidden">
                    <div class="absolute top-0 right-0 p-4 opacity-10"><i class="fa-solid fa-temperature-half text-6xl"></i></div>
                    <h3 class="text-slate-500 text-sm font-bold uppercase tracking-wider mb-2">Temperature</h3>
                    <div class="text-4xl font-black text-slate-800 mb-2">${m.temp}<span class="text-xl text-slate-400">°C</span></div>
                    <div class="text-sm font-semibold text-slate-400">Stable</div>
                </div>

                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 relative overflow-hidden">
                    <div class="absolute top-0 right-0 p-4 opacity-10"><i class="fa-solid fa-seedling text-6xl"></i></div>
                    <h3 class="text-slate-500 text-sm font-bold uppercase tracking-wider mb-2">Crop Health</h3>
                    <div class="text-3xl font-black text-slate-800 mb-2 mt-1">${m.health}</div>
                    <div class="text-sm font-semibold text-emerald-500">VPD: ${m.vpd} kPa</div>
                </div>
            </div>
        </div>
    `;
}

function IrrigationTab(state) {
    return `
        <div class="max-w-2xl mx-auto animate-[fadeIn_0.3s_ease-out]">
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div class="bg-slate-50 px-6 py-4 border-b border-slate-200">
                    <h2 class="text-lg font-bold text-slate-800"><i class="fa-solid fa-sliders text-emerald-600 mr-2"></i> Irrigation Controls</h2>
                </div>
                <div class="p-6">
                    <form id="irrigation-form" onsubmit="handleIrrigationSubmit(event)">
                        <div class="grid grid-cols-2 gap-4 mb-6">
                            <div class="col-span-2 md:col-span-1">
                                <label class="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Device ID</label>
                                <input type="text" name="device_id" value="field-001" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all" required>
                            </div>
                            <div class="col-span-2 md:col-span-1">
                                <label class="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Crop Type</label>
                                <input type="text" name="crop_type" value="${state.metrics.crop}" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all" required>
                            </div>
                            <div class="col-span-2">
                                <label class="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">Live Soil Moisture (%)</label>
                                <input type="number" name="moisture" value="${state.metrics.moisture}" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all" required>
                            </div>
                        </div>
                        <button type="submit" disabled="${state.isProcessing}" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-4 px-6 rounded-xl shadow-md transition-colors disabled:opacity-50">
                            ${state.isProcessing ? '<i class="fa-solid fa-circle-notch fa-spin mr-2"></i> Processing...' : 'Analyze & Update Network'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;
}

function AssistantTab(state) {
    const historyHtml = state.chatHistory.map(msg => `
        <div class="flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'} mb-4">
            <div class="max-w-[85%] md:max-w-[70%] rounded-2xl px-5 py-3 ${msg.role === 'user' ? 'bg-emerald-600 text-white rounded-br-sm shadow-sm' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-sm shadow-sm'}">
                <p class="leading-relaxed text-[15px]">${msg.text}</p>
            </div>
        </div>
    `).join('');

    return `
        <div class="max-w-3xl mx-auto h-full flex flex-col animate-[fadeIn_0.3s_ease-out]">
            <div class="flex-1 bg-slate-50 rounded-2xl border border-slate-200 overflow-hidden flex flex-col shadow-sm relative">
                
                <div class="bg-white px-6 py-4 border-b border-slate-200 flex justify-between items-center z-10">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600"><i class="fa-solid fa-robot"></i></div>
                        <div>
                            <h2 class="text-sm font-bold text-slate-800">AgriSense Copilot</h2>
                            <p class="text-xs text-slate-400 font-medium">Context: ${state.metrics.crop} | ${state.metrics.moisture}% Moisture</p>
                        </div>
                    </div>
                </div>

                <div id="chat-scroll" class="flex-1 overflow-y-auto p-6 scroll-smooth">
                    ${historyHtml}
                    ${state.isProcessing ? `
                        <div class="flex justify-start mb-4">
                            <div class="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-5 py-3 shadow-sm flex gap-1 items-center">
                                <div class="w-2 h-2 bg-slate-300 rounded-full animate-bounce"></div>
                                <div class="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                                <div class="w-2 h-2 bg-slate-300 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                            </div>
                        </div>
                    ` : ''}
                </div>

                <div class="bg-white p-4 border-t border-slate-200">
                    <form onsubmit="handleChatSubmit(event)" class="flex gap-2">
                        <input type="text" id="chat-input" placeholder="Ask the copilot..." autocomplete="off" class="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all" required>
                        <button type="submit" disabled="${state.isProcessing}" class="bg-emerald-600 hover:bg-emerald-700 text-white w-12 rounded-xl shadow-md transition-colors disabled:opacity-50 flex items-center justify-center">
                            <i class="fa-solid fa-paper-plane"></i>
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;
}

// ==========================================
// 4. CONTROLLERS & RENDER ENGINE
// ==========================================

// Main Render Loop - Triggers whenever Store state changes
function render(state) {
    const appElement = document.getElementById('app');
    
    let activeContent = '';
    if (state.activeTab === 'overview') activeContent = OverviewTab(state);
    else if (state.activeTab === 'irrigation') activeContent = IrrigationTab(state);
    else if (state.activeTab === 'ai') activeContent = AssistantTab(state);

    appElement.innerHTML = `
        ${Sidebar(state)}
        <main class="flex-1 h-full overflow-y-auto bg-slate-50 p-4 md:p-8 pb-24 md:pb-8 relative">
            ${activeContent}
        </main>
    `;

    // Auto-scroll chat to bottom if active
    if (state.activeTab === 'ai') {
        const chatBox = document.getElementById('chat-scroll');
        if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// Subscribe renderer to the Store
Store.subscribe(render);

// --- Form Handlers ---

window.handleIrrigationSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const payload = Object.fromEntries(formData.entries());
    payload.moisture = Number(payload.moisture);
    
    // Optimistically update the global UI state
    Store.updateMetric('moisture', payload.moisture);
    Store.updateMetric('crop', payload.crop_type);

    try {
        const data = await APIService.post("/irrigation/assess", payload);
        Store.updateMetric('health', data.action === 'irrigate' ? 'Needs Water' : 'Optimal');
        // Auto-switch to overview to show the updated metrics
        Store.setState({ activeTab: 'overview' }); 
    } catch (err) {
        alert("Failed to reach the edge device. Check network.");
    }
};

window.handleChatSubmit = async (e) => {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const userText = input.value.trim();
    if (!userText) return;

    // Add user message to state
    const newHistory = [...Store.getState().chatHistory, { role: 'user', text: userText }];
    Store.setState({ chatHistory: newHistory });

    try {
        // Send the global metrics along with the question so the AI has context!
        const res = await APIService.post("/llm/chat", { 
            question: userText, 
            session_id: "pro-app", 
            ...Store.getState().metrics 
        });
        
        Store.setState({ 
            chatHistory: [...newHistory, { role: 'ai', text: res.reply }] 
        });
    } catch (err) {
        Store.setState({ 
            chatHistory: [...newHistory, { role: 'ai', text: "Service Unavailable. Cloud servers are currently experiencing high load." }] 
        });
    }
};

// Add global styles for animations
const style = document.createElement('style');
style.textContent = `@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }`;
document.head.appendChild(style);

// Initialize App
render(Store.getState());
