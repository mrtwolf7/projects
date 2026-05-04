console.log("CONTENT SCRIPT LOADED");

chrome.runtime.sendMessage({ type: "INJECT" });

function waitForElement(selector) {
  return new Promise((resolve) => {
    const check = () => {
      const el = document.querySelector(selector);
      if (el) return resolve(el);
      requestAnimationFrame(check);
    };
    check();
  });
}

(async function init() {
  const mapContainer = await waitForElement(
    "#__next > main > section > div.MapViewContainer_mapParentContainer__WOBXf"
  );

  console.log("MAP CONTAINER READY");

  const overlay = document.createElement("div");

  overlay.style.position = "fixed";
  overlay.style.pointerEvents = "none";
  overlay.style.zIndex = "9999";

  document.body.appendChild(overlay);

  function updateOverlayPosition() {
    const rect = mapContainer.getBoundingClientRect();

    overlay.style.left = `${rect.left}px`;
    overlay.style.top = `${rect.top}px`;
    overlay.style.width = `${rect.width}px`;
    overlay.style.height = `${rect.height}px`;
  }

  setInterval(updateOverlayPosition, 500);

  window.addEventListener("message", (event) => {
    if (event.data.type === "RM_MAP_DATA") {
      drawDots(overlay, mapContainer);
    }
  });
})();

function drawDots(overlay, container) {
  overlay.innerHTML = "";

  const containerRect = container.getBoundingClientRect();

  const markers = document.querySelectorAll("gmp-advanced-marker");

  console.log("FOUND MARKERS:", markers.length);

  markers.forEach((marker) => {
    const rect = marker.getBoundingClientRect();

    if (rect.width === 0 && rect.height === 0) return;

    const x = rect.left - containerRect.left;
    const y = rect.top - containerRect.top;

    const dot = document.createElement("div");

    dot.style.position = "absolute";
    dot.style.width = "6px";
    dot.style.height = "6px";
    dot.style.background = "blue";
    dot.style.borderRadius = "50%";

    dot.style.left = `${x}px`;
    dot.style.top = `${y}px`;

    overlay.appendChild(dot);
  });
}