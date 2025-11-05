import { contextBridge, ipcRenderer } from 'electron';

// API expuesta al proceso renderer
const electronAPI = {
  // Diálogos
  dialog: {
    openFiles: () => ipcRenderer.invoke('dialog:openFiles'),
    openFolder: () => ipcRenderer.invoke('dialog:openFolder'),
    saveFile: (options: any) => ipcRenderer.invoke('dialog:saveFile', options)
  },

  // Store (configuración persistente)
  store: {
    get: (key: string) => ipcRenderer.invoke('store:get', key),
    set: (key: string, value: any) => ipcRenderer.invoke('store:set', key, value)
  },

  // Información de la aplicación
  app: {
    getInfo: () => ipcRenderer.invoke('app:getInfo')
  },

  // Control de ventana
  window: {
    minimize: () => ipcRenderer.invoke('window:minimize'),
    toggleMaximize: () => ipcRenderer.invoke('window:toggleMaximize'),
    close: () => ipcRenderer.invoke('window:close')
  },

  // Backend
  backend: {
    getStatus: () => ipcRenderer.invoke('backend:status')
  },

  // Eventos del menú
  menu: {
    onLoadImages: (callback: () => void) => {
      ipcRenderer.on('menu-load-images', callback);
      return () => ipcRenderer.removeListener('menu-load-images', callback);
    },
    onLoadFolder: (callback: () => void) => {
      ipcRenderer.on('menu-load-folder', callback);
      return () => ipcRenderer.removeListener('menu-load-folder', callback);
    },
    onExportPDF: (callback: () => void) => {
      ipcRenderer.on('menu-export-pdf', callback);
      return () => ipcRenderer.removeListener('menu-export-pdf', callback);
    },
    onExportCSV: (callback: () => void) => {
      ipcRenderer.on('menu-export-csv', callback);
      return () => ipcRenderer.removeListener('menu-export-csv', callback);
    },
    onShowHistory: (callback: () => void) => {
      ipcRenderer.on('menu-show-history', callback);
      return () => ipcRenderer.removeListener('menu-show-history', callback);
    },
    onShowSettings: (callback: () => void) => {
      ipcRenderer.on('menu-show-settings', callback);
      return () => ipcRenderer.removeListener('menu-show-settings', callback);
    },
    onShowAbout: (callback: () => void) => {
      ipcRenderer.on('menu-show-about', callback);
      return () => ipcRenderer.removeListener('menu-show-about', callback);
    },
    onCacheCleared: (callback: () => void) => {
      ipcRenderer.on('cache-cleared', callback);
      return () => ipcRenderer.removeListener('cache-cleared', callback);
    }
  },

  // Utilidades
  utils: {
    // Enviar mensajes personalizados
    send: (channel: string, data: any) => {
      const validChannels = ['analyze-image', 'export-report', 'load-history'];
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, data);
      }
    },
    // Recibir mensajes personalizados
    on: (channel: string, callback: (data: any) => void) => {
      const validChannels = ['analysis-result', 'export-complete', 'history-loaded'];
      if (validChannels.includes(channel)) {
        ipcRenderer.on(channel, (event, data) => callback(data));
        return () => ipcRenderer.removeListener(channel, callback);
      }
      return () => {};
    }
  }
};

// Exponer la API de forma segura al contexto del renderer
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Tipos para TypeScript
export type ElectronAPI = typeof electronAPI;
