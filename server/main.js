const {app, BrowserWindow, Menu} = require('electron')

require('electron-reload')(__dirname, {
  electron: require(`${__dirname}/node_modules/electron`)
});

Menu.setApplicationMenu(false)
function createWindow () {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    autoHideMenuBar: true,
    icon: 'ui/assets/favicon.ico',
    webPreferences: {
      nodeIntegration: true,
      devTools: true
    }
  })
  mainWindow.loadFile('ui/unicorn.html')

  mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {
  createWindow()
  
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})
app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})