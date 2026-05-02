const { app, BrowserWindow, ipcMain, screen } = require('electron');
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

  // 自定义最大化状态与存储普通状态的变量
  win.isMaximizedFlag = false;
  win.normalBounds = null;

  win.loadFile('index.html');

  // 详情窗口创建函数
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

  // 窗口控制 IPC
  ipcMain.on('window-minimize', (event) => {
    BrowserWindow.fromWebContents(event.sender).minimize();
  });

  ipcMain.on('window-close', (event) => {
    BrowserWindow.fromWebContents(event.sender).close();
  });

  // 最大化时拖动窗口 → 自动还原
  win.on('will-move', (event, newBounds) => {
    if (win.isMaximizedFlag) {
      event.preventDefault();          // 阻止本次移动
      if (win.normalBounds) {
        win.setBounds(win.normalBounds);
      } else {
        // 后备方案：没有保存过正常状态时，以鼠标当前位置为中心创建窗口
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

  // 最大化/还原（完全自定义，适配工作区并切换图标）
  ipcMain.on('window-maximize', (event) => {
    const senderWin = BrowserWindow.fromWebContents(event.sender);
    if (!senderWin || senderWin !== win) return;

    if (!win.isMaximizedFlag) {
      // 保存当前窗口状态
      win.normalBounds = win.getBounds();
      const currentScreen = screen.getDisplayMatching(win.normalBounds);
      const { x, y, width, height } = currentScreen.workArea;
      win.setBounds({ x, y, width, height });
      win.isMaximizedFlag = true;
      win.webContents.send('window-state-change', 'maximized');
    } else {
      if (win.normalBounds) {
        win.setBounds(win.normalBounds);
      }
      win.isMaximizedFlag = false;
      win.webContents.send('window-state-change', 'normal');
    }
  });

  // 打开详情窗口 IPC
  ipcMain.on('open-detail', (event, cmdData) => {
    createDetailWindow(cmdData);
  });

  // 读取指令数据
  ipcMain.handle('get-commands', async () => {
    const filePath = path.join(__dirname, 'commands.json');
    const rawData = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(rawData);
  });

  // 收藏相关
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

  ipcMain.handle('get-favorites', async () => {
    return getFavorites();
  });

  ipcMain.handle('toggle-favorite', async (event, commandId) => {
    const favs = getFavorites();
    let isFav = false;
    const index = favs.indexOf(commandId);
    if (index > -1) {
      favs.splice(index, 1);
    } else {
      favs.push(commandId);
      isFav = true;
    }
    saveFavorites(favs);
    return { success: true, isFav };
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});