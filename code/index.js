// Simple, resource-conscious Electron main process for a Chromium-based window.
// Run with: electron .

const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

/** @type {BrowserWindow | null} */
let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      // Helps Chromium reduce background CPU when window is not focused
      backgroundThrottling: true,
      spellcheck: false,
    },
  });

  // Load a starting page (you can change this to a local HTML UI)
  mainWindow.loadURL("https://www.google.com");

  // Optional: prevent heavy devtools in production to save memory/CPU
  // mainWindow.removeMenu();

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// Handle navigation requests from the renderer via preload.js
ipcMain.on("open-url", (event, url) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (!win) return;

  let target = String(url || "").trim();
  if (!target) return;

  if (!target.startsWith("http://") && !target.startsWith("https://")) {
    target = "https://" + target;
  }

  win.loadURL(target);
});

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

