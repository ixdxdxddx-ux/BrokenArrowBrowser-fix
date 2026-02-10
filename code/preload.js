// Preload script: exposes a safe API from the main process to the renderer.
// This runs in the isolated context before any web content loads.

const { contextBridge, ipcRenderer } = require("electron");

// Expose a minimal browser API to the renderer (window.electronAPI)
contextBridge.exposeInMainWorld("electronAPI", {
  // Example: ask main process to navigate the current window to a URL
  openURL: (url) => {
    ipcRenderer.send("open-url", url);
  },
});

