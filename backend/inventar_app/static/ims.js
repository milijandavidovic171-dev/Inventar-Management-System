const API_URL = "http://127.0.0.1:8080/api/artikel";
let fullInventory = [];

// Navigation
function switchTab(tabId, btnElement) {
    document.getElementById('tab-portfolio').style.display = 'none';
    document.getElementById('tab-ims').style.display = 'none';
    document.getElementById('tab-add').style.display = 'none';

    document.getElementById('tab-' + tabId).style.display = 'block';

    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btnElement.classList.add('active');

    if(tabId === 'ims') fetchItems();
}

// Daten laden
async function fetchItems() {
    try {
        const response = await fetch(API_URL);
        fullInventory = await response.json();
        renderTable(fullInventory);
    } catch (error) {
        console.error("Fehler beim Laden:", error);
    }
}

function renderTable(dataList) {
    const listBody = document.getElementById('inventory-list');
    listBody.innerHTML = dataList.map(item => `
        <tr>
            <td>${item.name}</td>
            <td style="font-family: monospace">${item.artikelnummer}</td>
            <td style="font-weight: bold; color: ${item.menge < 5 ? 'red' : 'black'}">${item.menge}</td>
            <td>
                <button class="tk-button" onclick="changeMenge(${item.id}, 1)">+</button>
                <button class="tk-button" style="color: red;" onclick="deleteItem(${item.id})">X</button>
            </td>
        </tr>
    `).join('');

    const total = dataList.reduce((acc, i) => acc + i.menge, 0);
    document.getElementById('stats-label').innerText = `Gefunden: ${dataList.length} | Gesamt: ${total}`;
}

function handleSearch() {
    const term = document.getElementById('search-box').value.toLowerCase();
    const filtered = fullInventory.filter(item =>
        item.name.toLowerCase().includes(term) ||
        item.artikelnummer.toLowerCase().includes(term)
    );
    renderTable(filtered);
}

async function submitNewItem() {
    const payload = {
        name: document.getElementById('in-name').value,
        artikelnummer: document.getElementById('in-nr').value,
        menge: parseInt(document.getElementById('in-menge').value) || 0
    };

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });

    if (response.ok) {
        alert("Artikel gespeichert!");
        fetchItems();
        switchTab('ims', document.querySelectorAll('.nav-btn')[1]);
    }
}

async function changeMenge(id, diff) {
    await fetch(`${API_URL}/${id}/menge?diff=${diff}`, { method: 'PATCH' });
    fetchItems();
}

async function deleteItem(id) {
    if(confirm("Löschen?")) {
        await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        fetchItems();
    }
}

setInterval(() => {
    document.getElementById('clock').innerText = new Date().toLocaleTimeString();
}, 1000);

window.onload = fetchItems;