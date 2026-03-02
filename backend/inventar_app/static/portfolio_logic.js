/**
 * Portfolio & Inventory Logic - Optimierte Version
 * Kommuniziert mit der FastAPI auf Port 8080
 */

const API_URL = "http://127.0.0.1:8080/api";
let localData = [];

// Benachrichtigungen (Toasts)
function showNotification(msg, color = 'bg-emerald-500') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `p-4 rounded-xl text-white font-bold shadow-2xl transition-all duration-500 ${color}`;
    toast.innerText = msg;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

// Status-Punkt Update
function updateStatusUI(isOnline) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');
    if (dot && text) {
        if (isOnline) {
            dot.className = "w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_10px_#10b981]";
            text.innerText = "API Verbunden";
            text.className = "text-[10px] font-bold uppercase text-emerald-400";
        } else {
            dot.className = "w-3 h-3 rounded-full bg-red-500 shadow-[0_0_10px_#ef4444]";
            text.innerText = "API Offline";
            text.className = "text-[10px] font-bold uppercase text-red-400";
        }
    }
}

// Daten laden & Health Check
async function loadInventory() {
    try {
        // Erst den Health-Check prüfen für den grünen Punkt
        const healthCheck = await fetch(`${API_URL}/health`);
        if (healthCheck.ok) {
            updateStatusUI(true);
        }

        // Dann die Artikel laden
        const response = await fetch(`${API_URL}/artikel`);
        if (response.ok) {
            localData = await response.json();

            // Gesamtbestand berechnen
            const total = localData.reduce((acc, item) => acc + item.menge, 0);
            const totalDisplay = document.getElementById('total-stock');
            if (totalDisplay) totalDisplay.innerText = `${total} Einheiten gesamt`;

            renderInventory(localData);
        }
    } catch (err) {
        console.error("API Verbindung fehlgeschlagen:", err);
        updateStatusUI(false);
        const list = document.getElementById('item-list');
        if (list) list.innerHTML = "<p class='text-red-400 text-center py-10 italic'>Verbindung zur FastAPI (Port 8080) fehlgeschlagen!</p>";
    }
}

// Liste im HTML aufbauen
function renderInventory(data) {
    const list = document.getElementById('item-list');
    if (!list) return;

    list.innerHTML = data.map(item => {
        let colorClass = "text-emerald-400";
        let dangerIcon = "";

        if (item.menge === 0) {
            colorClass = "text-red-500 danger-pulse";
            dangerIcon = "<i class='fas fa-exclamation-triangle mr-2'></i>";
        } else if (item.menge < 5) {
            colorClass = "text-amber-400";
        }

        return `
        <div class="flex justify-between items-center p-5 glass rounded-2xl border border-white/5 hover:bg-white/5 transition-all">
            <div>
                <h4 class="font-bold text-slate-100 text-lg">${item.name}</h4>
                <p class="text-[10px] font-mono text-slate-500 uppercase">${item.artikelnummer}</p>
            </div>
            <div class="flex items-center gap-4">
                <div class="flex items-center gap-2 bg-black/40 p-1.5 rounded-xl border border-white/5">
                    <button onclick="updateStock(${item.id}, -1)" class="w-8 h-8 rounded hover:bg-red-500/20 text-red-400"><i class="fas fa-minus text-xs"></i></button>
                    <span class="w-12 text-center font-black text-xl tabular-nums ${colorClass}">
                        ${dangerIcon}${item.menge}
                    </span>
                    <button onclick="updateStock(${item.id}, 1)" class="w-8 h-8 rounded hover:bg-emerald-500/20 text-emerald-400"><i class="fas fa-plus text-xs"></i></button>
                </div>
                <button onclick="handleDelete(${item.id})" class="text-slate-600 hover:text-red-500 p-2"><i class="fas fa-trash-alt"></i></button>
            </div>
        </div>`;
    }).join('') || '<p class="text-slate-500 text-center py-10 italic text-sm">Keine Artikel gefunden.</p>';
}

// Suche
function handleSearch() {
    const term = document.getElementById('search-input').value.toLowerCase();
    const filtered = localData.filter(item =>
        item.name.toLowerCase().includes(term) ||
        item.artikelnummer.toLowerCase().includes(term)
    );
    renderInventory(filtered);
}

// Speichern
async function handleSave() {
    const nameEl = document.getElementById('in-name');
    const nrEl = document.getElementById('in-nr');
    const mengeEl = document.getElementById('in-menge');

    if (!nameEl.value || !nrEl.value) {
        showNotification("Name und Artikel-Nr. werden benötigt!", "bg-red-500");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/artikel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: nameEl.value,
                artikelnummer: nrEl.value,
                menge: parseInt(mengeEl.value) || 0
            })
        });

        if (response.ok) {
            showNotification(`${nameEl.value} erfolgreich gespeichert!`);
            nameEl.value = "";
            nrEl.value = "";
            mengeEl.value = "0";
            loadInventory();
        } else {
            const error = await response.json();
            showNotification(error.detail || "Fehler beim Speichern", "bg-red-500");
        }
    } catch (e) {
        showNotification("Server nicht erreichbar", "bg-red-500");
    }
}

// Bestand ändern (+/-)
async function updateStock(id, diff) {
    try {
        const res = await fetch(`${API_URL}/artikel/${id}/menge?diff=${diff}`, { method: 'PATCH' });
        if (res.ok) loadInventory();
    } catch (e) {
        showNotification("Fehler beim Aktualisieren", "bg-red-500");
    }
}

// Löschen
async function handleDelete(id) {
    if (confirm("Möchtest du diesen Artikel wirklich unwiderruflich löschen?")) {
        try {
            const res = await fetch(`${API_URL}/artikel/${id}`, { method: 'DELETE' });
            if (res.ok) {
                showNotification("Artikel erfolgreich entfernt.");
                loadInventory();
            }
        } catch (e) {
            showNotification("Löschen fehlgeschlagen", "bg-red-500");
        }
    }
}

// Start beim Laden der Seite
window.onload = loadInventory;