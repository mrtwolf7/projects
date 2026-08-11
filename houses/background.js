chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "INJECT") {
    chrome.scripting.executeScript({
      target: { tabId: sender.tab.id },
      world: "MAIN",
      func: () => {
        console.log("MAIN WORLD SCRIPT RUNNING");

        const originalFetch = window.fetch;

        window.fetch = async (...args) => {
          const response = await originalFetch(...args);

          const url = args[0];

          if (typeof url === "string" && url.includes("/api/property-search/map/search")) {
            console.log("━━━━━━━━━━━━━━━━━━━━━━");
            console.log("🎯 RIGHTMOVE MAP SEARCH");
            console.log("URL:", url);

            try {
              const clone = response.clone();
              const data = await clone.json();

              console.log("RESULT COUNT:", data.resultCount);
              console.log("DATA:", data);

              window.postMessage(
                {
                  type: "RM_MAP_DATA",
                  data: data,
                },
                "*"
              );
            } catch (e) {
              console.log("⚠️ JSON parse failed");
            }

            console.log("━━━━━━━━━━━━━━━━━━━━━━");
          }

          return response;
        };
      },
    });
  }
});