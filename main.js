const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

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
  win.loadFile('index.html');
}

// 打开详情窗口
function createDetailWindow(cmdData) {
  const detailWin = new BrowserWindow({
    width: 480,
    height: 360,
    frame: false,
    transparent: true,
    resizable: false,
    parent: BrowserWindow.getFocusedWindow() || undefined,
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

// 窗口控制 IPC
ipcMain.on('window-minimize', (event) => {
  BrowserWindow.fromWebContents(event.sender).minimize();
});
ipcMain.on('window-maximize', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win.isMaximized()) {
    win.unmaximize();
  } else {
    win.maximize();
  }
});
ipcMain.on('window-close', (event) => {
  BrowserWindow.fromWebContents(event.sender).close();
});

// 打开详情窗口的 IPC
ipcMain.on('open-detail', (event, cmdData) => {
  createDetailWindow(cmdData);
});

// 读取指令数据
ipcMain.handle('get-commands', async () => {
  const filePath = path.join(__dirname, 'commands.json');
  const rawData = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(rawData);
});

// ===== 收藏功能相关 =====
const favoritesPath = path.join(__dirname, 'favorites.json');

function getFavorites() {
  try {
    if (fs.existsSync(favoritesPath)) {
      return JSON.parse(fs.readFileSync(favoritesPath, 'utf-8'));
    }
  } catch (e) {}
  return [];
}

function saveFavorites(favs) {
  fs.writeFileSync(favoritesPath, JSON.stringify(favs, null, 2), 'utf-8');
}

// 获取收藏列表
ipcMain.handle('get-favorites', async () => {
  return getFavorites();
});

// 切换收藏状态（收藏/取消）
ipcMain.handle('toggle-favorite', async (event, commandId) => {
  const favs = getFavorites();
  let isFav = false;
  const index = favs.indexOf(commandId);
  if (index > -1) {
    favs.splice(index, 1);
    isFav = false;
  } else {
    favs.push(commandId);
    isFav = true;
  }
  saveFavorites(favs);
  return { success: true, isFav };
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});