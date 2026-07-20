// Alsager web UI logic (MVA-3: status + ingestion controls + data preview).
const $ = (sel) => document.querySelector(sel);

function escapeHtml(str) {
  if (typeof str !== "string") {
    str = String(str ?? "");
  }
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function loadStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    $("#version").textContent = data.version ?? "—";
    $("#ha-connected").textContent = data.ha_connected ? "yes" : "no";
    $("#entities").textContent = data.monitored_entities ?? "—";
    $("#ingestion").textContent = data.ingestion ?? "—";
    $("#rows-total").textContent = data.rows_total ?? "—";
    $("#rows-today").textContent = data.rows_today ?? "—";
    $("#last-error").textContent = data.last_error || "none";

    const conn = $("#conn");
    if (data.ha_connected) {
      conn.textContent = "HA: connected";
      conn.className = "badge badge-ok";
    } else {
      conn.textContent = "HA: not connected";
      conn.className = "badge badge-warn";
    }
  } catch (err) {
    const conn = $("#conn");
    conn.textContent = "HA: error";
    conn.className = "badge badge-err";
  }
}

async function startIngestion() {
  await fetch("/api/ingestion/start", { method: "POST" });
  await loadStatus();
}
async function stopIngestion() {
  await fetch("/api/ingestion/stop", { method: "POST" });
  await loadStatus();
}

async function loadData() {
  try {
    const res = await fetch("/api/ingestion/recent?limit=50");
    const rows = await res.json();
    const tbody = $("#data-rows");
    tbody.innerHTML = "";
    if (rows.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="muted" style="text-align: center;">No ingestion data available yet. Start ingestion and make sure you are monitoring entities.</td></tr>`;
      return;
    }
    for (const r of rows) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${escapeHtml(r.id)}</td>
        <td><strong class="ent-id">${escapeHtml(r.entity_id)}</strong></td>
        <td>${escapeHtml(r.state)}</td>
        <td>${escapeHtml(r.domain)}</td>
        <td><small class="muted">${escapeHtml(r.received_at)}</small></td>`;
      tbody.appendChild(tr);
    }
  } catch (err) {
    const tbody = $("#data-rows");
    tbody.innerHTML = `<tr><td colspan="5" class="muted" style="text-align: center;">Error loading preview: ${escapeHtml(err.message)}</td></tr>`;
  }
}

async function loadEntities() {
  const domain = $("#domain-filter").value;
  const url = "/api/entities" + (domain ? `?domain=${encodeURIComponent(domain)}` : "");
  const res = await fetch(url);
  const data = await res.json();

  $("#entity-source").textContent =
    `Source: ${data.source} · ${data.count} entities`;

  const filter = $("#entity-filter").value.toLowerCase();
  const rows = $("#entity-rows");
  rows.innerHTML = "";
  for (const e of data.entities) {
    if (filter && !(`${e.entity_id} ${e.friendly_name}`.toLowerCase().includes(filter))) {
      continue;
    }
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input type="checkbox" class="ent-check" value="${escapeHtml(e.entity_id)}" /></td>
      <td><span class="ent-id">${escapeHtml(e.entity_id)}</span><br><small class="muted">${escapeHtml(e.friendly_name)}</small></td>
      <td>${escapeHtml(e.domain)}</td>
      <td>${escapeHtml(e.state)}</td>`;
    rows.appendChild(tr);
  }
  await loadMonitored();
}

async function loadMonitored() {
  const res = await fetch("/api/monitored");
  const data = await res.json();
  const set = new Set(data.monitored);
  $("#monitored-summary").textContent =
    `Monitored (${set.size}): ` + (set.size ? [...set].join(", ") : "none");
  document.querySelectorAll(".ent-check").forEach((cb) => {
    cb.checked = set.has(cb.value);
  });
}

async function startMonitoring() {
  const selected = [...document.querySelectorAll(".ent-check:checked")].map((cb) => cb.value);
  if (!selected.length) {
    alert("Select at least one entity.");
    return;
  }
  await fetch("/api/monitored", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ entity_ids: selected }),
  });
  await loadMonitored();
  await loadStatus();
}

async function stopMonitoring() {
  const selected = [...document.querySelectorAll(".ent-check:checked")].map((cb) => cb.value);
  if (selected.length) {
    await fetch("/api/monitored", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entity_ids: selected }),
    });
  }
  await loadMonitored();
  await loadStatus();
}

function wireTabs() {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach((p) => p.classList.add("hidden"));
      tab.classList.add("active");
      document.querySelector(`.tab-panel[data-panel="${tab.dataset.tab}"]`).classList.remove("hidden");

      const tabName = tab.dataset.tab;
      if (tabName === "status") {
        loadStatus();
      } else if (tabName === "entities") {
        loadEntities();
      } else if (tabName === "data") {
        loadData();
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  wireTabs();
  loadStatus();
  $("#start-ingestion").addEventListener("click", startIngestion);
  $("#stop-ingestion").addEventListener("click", stopIngestion);
  $("#refresh-status").addEventListener("click", loadStatus);
  $("#refresh-data").addEventListener("click", loadData);

  $("#load-entities").addEventListener("click", loadEntities);
  $("#entity-filter").addEventListener("input", loadEntities);
  $("#domain-filter").addEventListener("change", loadEntities);
  $("#start-monitoring").addEventListener("click", startMonitoring);
  $("#stop-monitoring").addEventListener("click", stopMonitoring);
  loadEntities();
});
