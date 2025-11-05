import { app, BrowserWindow, ipcMain, dialog, Menu, shell, globalShortcut } from 'electron';
import * as path from 'path';
import * as fs from 'fs/promises';
import { spawn } from 'child_process';
import Store from 'electron-store';

const isDev = process.env.NODE_ENV !== 'production';
const store = new Store();

let mainWindow: BrowserWindow | null = null;
let backendProcess: any = null;
let isQuitting = false;

// Configuración de la aplicación
const APP_CONFIG = {
  name: 'Neuro-AI',
  version: '2.0.0',
  backendPort: 5000,
  windowConfig: {
    defaultWidth: 1400,
    defaultHeight: 900,
    minWidth: 1200,
    minHeight: 700
  }
};

// Crear el menú de la aplicación
function createMenu() {
  const template: any = [
    {
      label: 'Archivo',
      submenu: [
        {
          label: 'Cargar Imágenes',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow?.webContents.send('menu-load-images');
          }
        },
        {
          label: 'Cargar Carpeta',
          accelerator: 'CmdOrCtrl+Shift+O',
          click: () => {
            mainWindow?.webContents.send('menu-load-folder');
          }
        },
        { type: 'separator' },
        {
          label: 'Exportar PDF',
          accelerator: 'CmdOrCtrl+E',
          click: () => {
            mainWindow?.webContents.send('menu-export-pdf');
          }
        },
        {
          label: 'Exportar CSV',
          accelerator: 'CmdOrCtrl+Shift+E',
          click: () => {
            mainWindow?.webContents.send('menu-export-csv');
          }
        },
        { type: 'separator' },
        {
          label: 'Salir',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edición',
      submenu: [
        { role: 'undo', label: 'Deshacer' },
        { role: 'redo', label: 'Rehacer' },
        { type: 'separator' },
        { role: 'cut', label: 'Cortar' },
        { role: 'copy', label: 'Copiar' },
        { role: 'paste', label: 'Pegar' },
        { role: 'selectAll', label: 'Seleccionar Todo' }
      ]
    },
    {
      label: 'Vista',
      submenu: [
        {
          label: 'Pantalla Completa',
          accelerator: 'F11',
          click: () => {
            const isFullScreen = mainWindow?.isFullScreen();
            mainWindow?.setFullScreen(!isFullScreen);
          }
        },
        { type: 'separator' },
        { role: 'reload', label: 'Recargar' },
        { role: 'forceReload', label: 'Forzar Recarga' },
        { role: 'toggleDevTools', label: 'Herramientas de Desarrollador' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Restablecer Zoom' },
        { role: 'zoomIn', label: 'Acercar' },
        { role: 'zoomOut', label: 'Alejar' }
      ]
    },
    {
      label: 'Herramientas',
      submenu: [
        {
          label: 'Historial de Diagnósticos',
          accelerator: 'CmdOrCtrl+H',
          click: () => {
            mainWindow?.webContents.send('menu-show-history');
          }
        },
        {
          label: 'Configuración',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            mainWindow?.webContents.send('menu-show-settings');
          }
        },
        { type: 'separator' },
        {
          label: 'Limpiar Caché',
          click: async () => {
            const result = await dialog.showMessageBox(mainWindow!, {
              type: 'question',
              buttons: ['Sí', 'No'],
              defaultId: 1,
              title: 'Limpiar Caché',
              message: '¿Está seguro de que desea limpiar el caché de la aplicación?'
            });
            
            if (result.response === 0) {
              store.clear();
              mainWindow?.webContents.send('cache-cleared');
            }
          }
        }
      ]
    },
    {
      label: 'Ayuda',
      submenu: [
        {
          label: 'Documentación',
          click: () => {
            shell.openExternal('https://github.com/neuro-ai/docs');
          }
        },
        {
          label: 'Reportar un Problema',
          click: () => {
            shell.openExternal('https://github.com/neuro-ai/issues');
          }
        },
        { type: 'separator' },
        {
          label: 'Acerca de',
          click: () => {
            mainWindow?.webContents.send('menu-show-about');
          }
        }
      ]
    }
  ];

  if (process.platform === 'darwin') {
    template.unshift({
      label: app.getName(),
      submenu: [
        { role: 'about', label: `Acerca de ${APP_CONFIG.name}` },
        { type: 'separator' },
        { role: 'services', label: 'Servicios' },
        { type: 'separator' },
        { role: 'hide', label: `Ocultar ${APP_CONFIG.name}` },
        { role: 'hideOthers', label: 'Ocultar Otros' },
        { role: 'unhide', label: 'Mostrar Todo' },
        { type: 'separator' },
        { role: 'quit', label: `Salir de ${APP_CONFIG.name}` }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Iniciar el servidor backend de Python
async function startBackend() {
  return new Promise((resolve, reject) => {
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const backendPath = isDev 
      ? path.join(__dirname, '../../backend/app.py')
      : path.join(process.resourcesPath, 'backend/app.py');

    backendProcess = spawn(pythonPath, [backendPath], {
      cwd: path.dirname(backendPath),
      env: {
        ...process.env,
        FLASK_PORT: APP_CONFIG.backendPort.toString()
      }
    });

    backendProcess.stdout.on('data', (data: Buffer) => {
      console.log(`Backend: ${data.toString()}`);
      if (data.toString().includes('Running on')) {
        resolve(true);
      }
    });

    backendProcess.stderr.on('data', (data: Buffer) => {
      console.error(`Backend Error: ${data.toString()}`);
    });

    backendProcess.on('error', (error: Error) => {
      console.error('Failed to start backend:', error);
      reject(error);
    });

    // Timeout para iniciar sin backend si falla
    setTimeout(() => {
      console.warn('Backend took too long to start, continuing without it...');
      resolve(false);
    }, 10000);
  });
}

// Crear la ventana principal
async function createWindow() {
  // Recuperar el tamaño y posición guardados
  const windowBounds = store.get('windowBounds', {
    width: APP_CONFIG.windowConfig.defaultWidth,
    height: APP_CONFIG.windowConfig.defaultHeight,
    x: undefined,
    y: undefined
  });

  mainWindow = new BrowserWindow({
    ...windowBounds,
    minWidth: APP_CONFIG.windowConfig.minWidth,
    minHeight: APP_CONFIG.windowConfig.minHeight,
    title: APP_CONFIG.name,
    icon: path.join(__dirname, '../../public/icons/icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    frame: true,
    show: false,
    backgroundColor: '#f8fafc'
  });

  // Guardar el tamaño y posición cuando cambian
  mainWindow.on('resize', () => {
    if (mainWindow && !mainWindow.isMaximized() && !mainWindow.isFullScreen()) {
      const bounds = mainWindow.getBounds();
      store.set('windowBounds', bounds);
    }
  });

  mainWindow.on('move', () => {
    if (mainWindow && !mainWindow.isMaximized() && !mainWindow.isFullScreen()) {
      const bounds = mainWindow.getBounds();
      store.set('windowBounds', bounds);
    }
  });

  // Cargar el contenido
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
  }

  // Mostrar la ventana cuando esté lista
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // Manejar el cierre de la ventana
  mainWindow.on('close', (e) => {
    if (!isQuitting && process.platform === 'darwin') {
      e.preventDefault();
      mainWindow?.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Registrar atajos de teclado globales
  globalShortcut.register('F11', () => {
    const isFullScreen = mainWindow?.isFullScreen();
    mainWindow?.setFullScreen(!isFullScreen);
  });

  globalShortcut.register('Escape', () => {
    if (mainWindow?.isFullScreen()) {
      mainWindow.setFullScreen(false);
    }
  });
}

// Manejadores IPC
function setupIpcHandlers() {
  // Diálogo para seleccionar archivos
  ipcMain.handle('dialog:openFiles', async () => {
    const result = await dialog.showOpenDialog(mainWindow!, {
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Imágenes', extensions: ['jpg', 'jpeg', 'png', 'bmp', 'dcm'] },
        { name: 'Todos los archivos', extensions: ['*'] }
      ]
    });
    return result;
  });

  // Diálogo para seleccionar carpeta
  ipcMain.handle('dialog:openFolder', async () => {
    const result = await dialog.showOpenDialog(mainWindow!, {
      properties: ['openDirectory']
    });
    return result;
  });

  // Diálogo para guardar archivo
  ipcMain.handle('dialog:saveFile', async (event, options) => {
    const result = await dialog.showSaveDialog(mainWindow!, options);
    return result;
  });

  // Obtener configuración
  ipcMain.handle('store:get', (event, key) => {
    return store.get(key);
  });

  // Guardar configuración
  ipcMain.handle('store:set', (event, key, value) => {
    store.set(key, value);
  });

  // Obtener información del sistema
  ipcMain.handle('app:getInfo', () => {
    return {
      name: APP_CONFIG.name,
      version: APP_CONFIG.version,
      platform: process.platform,
      arch: process.arch,
      nodeVersion: process.versions.node,
      electronVersion: process.versions.electron
    };
  });

  // Minimizar ventana
  ipcMain.handle('window:minimize', () => {
    mainWindow?.minimize();
  });

  // Maximizar/Restaurar ventana
  ipcMain.handle('window:toggleMaximize', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow.restore();
    } else {
      mainWindow?.maximize();
    }
  });

  // Cerrar ventana
  ipcMain.handle('window:close', () => {
    mainWindow?.close();
  });

  // Obtener estado del backend
  ipcMain.handle('backend:status', () => {
    return {
      running: backendProcess && !backendProcess.killed,
      port: APP_CONFIG.backendPort
    };
  });
}

// Inicialización de la aplicación
app.whenReady().then(async () => {
  // Iniciar el backend
  try {
    const backendStarted = await startBackend();
    console.log('Backend started:', backendStarted);
  } catch (error) {
    console.error('Backend failed to start:', error);
  }

  // Crear ventana y configurar todo
  await createWindow();
  createMenu();
  setupIpcHandlers();

  // En macOS, recrear la ventana cuando se hace clic en el ícono del dock
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else {
      mainWindow?.show();
    }
  });
});

// Manejar el cierre de la aplicación
app.on('before-quit', () => {
  isQuitting = true;
  
  // Terminar el proceso del backend
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
  }
  
  // Desregistrar atajos globales
  globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Prevenir múltiples instancias
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    // Si alguien intenta abrir una segunda instancia, enfocar la ventana existente
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

// Manejar errores no capturados
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  dialog.showErrorBox('Error Inesperado', error.message);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
