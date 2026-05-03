const { app, BrowserWindow, ipcMain, screen, globalShortcut, shell } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow = null;
let hotkeyEnabled = false;

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 600,
    frame: false,
    transparent: true,
    resizable: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow = win;

  win.isMaximizedFlag = false;
  win.normalBounds = null;

  win.loadFile('index.html');

  function createDetailWindow(cmdData) {
    const detailWin = new BrowserWindow({
      width: 480,
      height: 360,
      frame: false,
      transparent: true,
      resizable: false,
      parent: win,
      modal: false,
      webPreferences: {
        nodeIntegration: true,
        contextIsolation: false
      }
    });
    detailWin.loadFile('detail.html', {
      query: cmdData
    });
  }

  ipcMain.on('window-minimize', (event) => {
    BrowserWindow.fromWebContents(event.sender).minimize();
  });
  ipcMain.on('window-close', (event) => {
    BrowserWindow.fromWebContents(event.sender).close();
  });

  win.on('will-move', (event, newBounds) => {
    if (win.isMaximizedFlag) {
      event.preventDefault();
      if (win.normalBounds) {
        win.setBounds(win.normalBounds);
      } else {
        win.setBounds({
          width: 900,
          height: 600,
          x: newBounds.x - 450,
          y: newBounds.y - 300
        });
      }
      win.isMaximizedFlag = false;
      win.webContents.send('window-state-change', 'normal');
    }
  });

  ipcMain.on('window-maximize', (event) => {
    const senderWin = BrowserWindow.fromWebContents(event.sender);
    if (!senderWin || senderWin !== win) return;

    if (!win.isMaximizedFlag) {
      win.normalBounds = win.getBounds();
      const currentScreen = screen.getDisplayMatching(win.normalBounds);
      const { x, y, width, height } = currentScreen.workArea;
      win.setBounds({ x, y, width, height });
      win.isMaximizedFlag = true;
      win.webContents.send('window-state-change', 'maximized');
    } else {
      if (win.normalBounds) win.setBounds(win.normalBounds);
      win.isMaximizedFlag = false;
      win.webContents.send('window-state-change', 'normal');
    }
  });

  ipcMain.on('open-detail', (event, cmdData) => {
    createDetailWindow(cmdData);
  });

  // ========== 数据接口 ==========
  ipcMain.handle('get-commands', async () => {
    const filePath = path.join(__dirname, 'commands.json');
    const rawData = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(rawData);
  });

  ipcMain.handle('get-examples', async () => {
    const examplesPath = path.join(__dirname, 'examples.json');
    if (!fs.existsSync(examplesPath)) return {};
    const raw = fs.readFileSync(examplesPath, 'utf-8');
    return JSON.parse(raw);
  });

  ipcMain.handle('get-items', async () => {
    const itemsPath = path.join(__dirname, 'items.json');
    if (!fs.existsSync(itemsPath)) return [];
    const raw = fs.readFileSync(itemsPath, 'utf-8');
    return JSON.parse(raw);
  });

  // 收藏
  const favoritesPath = path.join(__dirname, 'favorites.json');
  function getFavorites() {
    try {
      if (fs.existsSync(favoritesPath))
        return JSON.parse(fs.readFileSync(favoritesPath, 'utf-8'));
    } catch (e) {}
    return [];
  }
  function saveFavorites(favs) {
    fs.writeFileSync(favoritesPath, JSON.stringify(favs, null, 2), 'utf-8');
  }
  ipcMain.handle('get-favorites', async () => getFavorites());
  ipcMain.handle('toggle-favorite', async (event, commandId) => {
    const favs = getFavorites();
    let isFav = false;
    const index = favs.indexOf(commandId);
    if (index > -1) favs.splice(index, 1);
    else { favs.push(commandId); isFav = true; }
    saveFavorites(favs);
    return { success: true, isFav };
  });

  // ===================== 笔记功能 =====================
  const notesPath = path.join(__dirname, 'notes.json');
  function getNotes() {
    try {
      if (fs.existsSync(notesPath))
        return JSON.parse(fs.readFileSync(notesPath, 'utf-8'));
    } catch (e) {}
    return [];
  }
  function saveNotes(notes) {
    fs.writeFileSync(notesPath, JSON.stringify(notes, null, 2), 'utf-8');
  }

  ipcMain.handle('get-notes', async () => getNotes());
  ipcMain.handle('add-note', async (event, text) => {
    const notes = getNotes();
    const note = {
      id: Date.now().toString(),
      text: text,
      time: new Date().toISOString()
    };
    notes.push(note);
    saveNotes(notes);
    return { success: true, note };
  });
  ipcMain.handle('delete-note', async (event, noteId) => {
    let notes = getNotes();
    notes = notes.filter(n => n.id !== noteId);
    saveNotes(notes);
    return { success: true };
  });

  // ========== 快捷键 ==========
  function toggleWindow() {
    if (!mainWindow) return;
    if (mainWindow.isMinimized() || !mainWindow.isVisible()) {
      mainWindow.show();
      mainWindow.restore();
      mainWindow.setAlwaysOnTop(true, 'screen-saver');
      mainWindow.focus();
    } else if (mainWindow.isAlwaysOnTop() && mainWindow.isFocused()) {
      mainWindow.setAlwaysOnTop(false);
      mainWindow.hide();
    } else {
      mainWindow.setAlwaysOnTop(true, 'screen-saver');
      mainWindow.focus();
    }
  }
  function registerHotkey() {
    try {
      const ret = globalShortcut.register('Alt+M', toggleWindow);
      if (!ret) console.warn('快捷键 Alt+M 注册失败');
      return ret;
    } catch (e) { return false; }
  }
  function unregisterHotkey() { globalShortcut.unregister('Alt+M'); }

  ipcMain.handle('toggle-hotkey', async (event, enable) => {
    if (enable) {
      if (!hotkeyEnabled) {
        hotkeyEnabled = registerHotkey();
        if (!hotkeyEnabled) {
          mainWindow.webContents.send('hotkey-status', false, '注册失败');
          return { enabled: false, message: '注册失败' };
        }
      }
      return { enabled: true };
    } else {
      if (hotkeyEnabled) { unregisterHotkey(); hotkeyEnabled = false; }
      if (mainWindow) mainWindow.setAlwaysOnTop(false);
      return { enabled: false };
    }
  });
  ipcMain.handle('get-hotkey-status', async () => hotkeyEnabled);

  // 打开外部链接
  ipcMain.on('open-external', (event, url) => {
    if (url) shell.openExternal(url);
  });

  win.on('closed', () => {
    if (hotkeyEnabled) { unregisterHotkey(); hotkeyEnabled = false; }
    mainWindow = null;
  });
}

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});