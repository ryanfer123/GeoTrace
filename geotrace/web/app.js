"use strict";
const $ = (id) => document.getElementById(id);
const esc = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const presets = {
  aral: {
    name: "Aral Sea, Central Asia",
    title: "Aral Sea shoreline study",
    bounds: [56, 42, 62, 47],
    before: "2001-08-01",
    after: "2023-08-01",
  },
  urmia: {
    name: "Lake Urmia, Iran",
    title: "Lake Urmia visual study",
    bounds: [44.5, 36.5, 46.5, 38.5],
    before: "2010-08-01",
    after: "2023-08-01",
  },
  california: {
    name: "Northern California, USA",
    title: "California landscape study",
    bounds: [-124, 37, -119, 42],
    before: "2020-08-01",
    after: "2020-09-01",
  },
};
let catalog = null,
  current = null,
  records = [],
  busy = false,
  displaySpec = null;
const compareContent = $("compare-button").innerHTML;
function notice(message, error = false) {
  $("notice").textContent = message;
  $("notice").hidden = !message;
  $("notice").classList.toggle("error", error);
}
async function api(path, data) {
  const r = await fetch(
    path,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        },
  );
  const value = await r.json();
  if (!r.ok) throw new Error(value.error || `Request failed (${r.status}).`);
  return value;
}
function readSpec() {
  return {
    name: $("name").value,
    notes: $("notes").value,
    bounds: ["west", "south", "east", "north"].map((id) => Number($(id).value)),
    layer: $("layer").value,
    before: $("before").value,
    after: $("after").value,
  };
}
function applySpec(spec) {
  for (const [i, id] of ["west", "south", "east", "north"].entries())
    $(id).value = spec.bounds[i];
  $("layer").value = spec.layer;
  $("before").value = spec.before;
  $("after").value = spec.after;
  $("name").value = spec.name;
  $("notes").value = spec.notes;
  updateAvailability();
}
function updateAvailability() {
  const layer = catalog?.layers.find((x) => x.id === $("layer").value);
  if (!layer) return;
  const first = layer.intervals[0].split("/")[0],
    last = layer.intervals.at(-1).split("/")[1] || layer.intervals.at(-1);
  $("availability").textContent =
    `Advertised range ${first} to ${last}. Some dates have gaps; each request is checked.`;
  $("before").min = $("after").min = first;
  $("before").max = $("after").max = last;
  $("catalog-date").textContent =
    `Metadata verified ${catalog.verified}. No nearest-date substitution.`;
}
function populateCatalog(value) {
  catalog = value;
  const chosen = $("layer").value;
  $("layer").innerHTML = value.layers
    .map((l) => `<option value="${esc(l.id)}">${esc(l.name)}</option>`)
    .join("");
  $("layer").value = value.layers.some((x) => x.id === chosen)
    ? chosen
    : "MODIS_Terra_CorrectedReflectance_TrueColor";
  updateAvailability();
}
function changed() {
  current = null;
  $("save-button").disabled = true;
  $("view-state").textContent = "Settings changed · load to update";
}
function showComparison(comparison) {
  const { spec, sources } = comparison;
  displaySpec = spec;
  current = comparison;
  const west = spec.bounds[0],
    south = spec.bounds[1],
    east = spec.bounds[2],
    north = spec.bounds[3];
  const height = Math.max(
    240,
    Math.min(1200, Math.round((1200 * (north - south)) / (east - west))),
  );
  $("scene").style.aspectRatio = `1200 / ${height}`;
  $("before-image").src = "/api/images/" + sources.before.key;
  $("after-image").src = "/api/images/" + sources.after.key;
  $("before-image").alt =
    `${spec.before} NASA satellite browse image, bounds ${spec.bounds.join(", ")}`;
  $("after-image").alt =
    `${spec.after} NASA satellite browse image of the same bounds`;
  $("before-label").textContent = spec.before;
  $("after-label").textContent = spec.after;
  $("view-title").textContent = spec.name;
  $("scene-coordinate").textContent =
    `${west}°, ${south}° → ${east}°, ${north}°`;
  $("view-state").textContent = "Aligned geographic bounds";
  $("provenance-content").innerHTML = `<div class="provenance-grid">${[
    "before",
    "after",
  ]
    .map((label) => {
      const item = sources[label];
      return `<article class="provenance-item"><h3>${label === "before" ? "Earlier" : "Later"} · ${esc(spec[label])}</h3><p>${esc(spec.layer)}</p><p><a href="${esc(item.url)}" target="_blank" rel="noreferrer">Open exact NASA image request ↗</a></p><p>Fetched ${esc(new Date(item.fetched_at).toLocaleString())} · ${(item.bytes / 1024).toFixed(1)} KiB</p><p class="checksum">SHA256 ${esc(item.sha256)}</p></article>`;
    })
    .join("")}</div>`;
  $("save-button").disabled = false;
  Promise.all([$("before-image").decode(), $("after-image").decode()])
    .then(() => {
      $("image-loading").hidden = true;
      document.dispatchEvent(new CustomEvent("geo:comparison"));
    })
    .catch(() => {
      $("image-loading").hidden = false;
      $("image-loading").querySelector("p").textContent =
        "The cached images could not be displayed";
      notice("Image display failed. Load the comparison again.", true);
    });
}
async function loadComparison() {
  if (busy) return;
  busy = true;
  document
    .querySelectorAll("#investigation-form input,#investigation-form select")
    .forEach((e) => (e.disabled = true));
  $("compare-button").disabled = true;
  $("compare-button").textContent = "Loading satellite views…";
  $("save-button").disabled = true;
  $("image-loading").hidden = false;
  $("image-loading").querySelector("p").textContent =
    "Preparing the satellite views";
  notice("");
  try {
    const comparison = await api("/api/compare", readSpec());
    showComparison(comparison);
  } catch (error) {
    current = null;
    $("view-state").textContent = "Source unavailable";
    $("image-loading").querySelector("p").textContent =
      "This view could not be loaded";
    $("image-loading").querySelector("small").textContent =
      "Try another advertised date or check your connection.";
    notice(error.message, true);
  } finally {
    busy = false;
    document
      .querySelectorAll("#investigation-form input,#investigation-form select")
      .forEach((e) => (e.disabled = false));
    $("compare-button").disabled = false;
    $("compare-button").innerHTML = compareContent;
  }
}
function renderRecords() {
  $("saved-count").textContent =
    `${records.length} investigation${records.length === 1 ? "" : "s"}`;
  $("saved-list").innerHTML = records.length
    ? records
        .map(
          (r) =>
            `<article class="saved-record"><div><h3>${esc(r.spec.name)}</h3><p>${esc(r.spec.before)} → ${esc(r.spec.after)} · ${esc(r.spec.layer)}<br>${esc(new Date(r.created).toLocaleString())}</p>${r.spec.notes ? `<p class="saved-notes">${esc(r.spec.notes)}</p>` : ""}</div><div class="saved-actions"><button data-open="${esc(r.id)}">Open comparison</button><a href="/api/export/${esc(r.id)}" download>JSON ↓</a><a href="/api/export/${esc(r.id)}?format=md" download>Report ↓</a></div></article>`,
        )
        .join("")
    : '<p class="empty-note">Save a comparison and its notes to keep a traceable record here.</p>';
}
$("investigation-form").addEventListener("submit", (event) => {
  event.preventDefault();
  loadComparison();
});
$("layer").addEventListener("change", () => {
  updateAvailability();
  changed();
});
for (const id of ["west", "south", "east", "north", "before", "after"])
  $(id).addEventListener("input", changed);
$("preset").addEventListener("change", () => {
  const preset = presets[$("preset").value];
  if (!preset) return;
  applySpec({
    name: preset.title,
    notes: "",
    bounds: preset.bounds,
    layer: $("layer").value,
    before: preset.before,
    after: preset.after,
  });
  changed();
});
$("swipe").addEventListener("input", () => {
  const split = Number($("swipe").value);
  $("after-image").style.clipPath = `inset(0 0 0 ${split}%)`;
  $("swipe-line").style.left = `${split}%`;
  $("split-value").textContent = `${split} / ${100 - split}`;
});
$("save-button").addEventListener("click", async () => {
  if (!current || busy) return;
  const spec = {
    ...current.spec,
    name: $("name").value,
    notes: $("notes").value,
  };
  $("save-button").disabled = true;
  try {
    const record = await api("/api/investigations", spec);
    records.unshift(record);
    renderRecords();
    notice("Investigation saved locally with image provenance and your notes.");
  } catch (error) {
    notice(error.message, true);
  } finally {
    $("save-button").disabled = !current;
  }
});
$("saved-list").addEventListener("click", (event) => {
  const button = event.target.closest("[data-open]");
  if (!button) return;
  const record = records.find((r) => r.id === button.dataset.open);
  if (!record) return;
  applySpec(record.spec);
  $("preset").value = "custom";
  showComparison(record);
  $("scene").scrollIntoView({
    block: "center",
    behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "instant"
      : "smooth",
  });
  notice("Saved investigation loaded.");
});
$("refresh-catalog").addEventListener("click", async () => {
  $("refresh-catalog").disabled = true;
  try {
    populateCatalog(await api("/api/catalog/refresh", {}));
    notice("NASA layer availability refreshed.");
  } catch (error) {
    notice(error.message, true);
  } finally {
    $("refresh-catalog").disabled = false;
  }
});
(async () => {
  try {
    const state = await api("/api/state");
    populateCatalog(state.catalog);
    records = state.investigations;
    renderRecords();
    await loadComparison();
  } catch (error) {
    notice(error.message, true);
  }
})();
