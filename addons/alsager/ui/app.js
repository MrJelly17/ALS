// Alsager web UI logic (MVA-3: status + ingestion controls + data preview).
const $ = (sel) => document.querySelector(sel);

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
  const res = await fetch("/api/ingestion/status");
  const snap = await res.json();
  // recent rows come from a dedicated endpoint in later modules; for MVA-3
  // we surface total/snapshot. (Data table fill deferred to MVA-3 data API.)
  const tbody = $("#data-rows");
  tbody.innerHTML =
    `<tr><td colspan="5" class="muted">Ingestion running: ${snap.running} · ` +
    `total rows: ${snap.rows_total} · today: ${snap.rows_today}. ` +
    `Per-row preview lands with the data API.</td></tr>`;
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
      <td><input type="checkbox" class="ent-check" value="${e.entity_id}" /></td>
      <td><span class="ent-id">${e.entity_id}</span><br><small class="muted">${e.friendly_name}</small></td>
      <td>${e.domain}</td>
      <td>${e.state}</td>`;
    rows.appendChild(tr);
  }
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
