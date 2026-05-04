(function () {
  const originalFetch = window.fetch;

  window.fetch = async (...args) => {
    const response = await originalFetch(...args);

    try {
      if (args[0].includes("_search")) {
        console.log("HIT _search:", args[0]);
      }
    } catch (e) {}

    return response;
  };

  console.log("Injected script running");
})();