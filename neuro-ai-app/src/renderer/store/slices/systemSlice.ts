import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SystemState {
  backendStatus: {
    isRunning: boolean;
    modelsLoaded: boolean;
    port?: number;
  };
  appInfo: {
    name: string;
    version: string;
    platform: string;
    arch: string;
  } | null;
  notifications: {
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    message: string;
    timestamp: string;
  }[];
  isFullscreen: boolean;
  isDarkMode: boolean;
}

const initialState: SystemState = {
  backendStatus: {
    isRunning: false,
    modelsLoaded: false,
  },
  appInfo: null,
  notifications: [],
  isFullscreen: false,
  isDarkMode: false,
};

const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    setBackendStatus: (state, action: PayloadAction<SystemState['backendStatus']>) => {
      state.backendStatus = action.payload;
    },
    setAppInfo: (state, action: PayloadAction<SystemState['appInfo']>) => {
      state.appInfo = action.payload;
    },
    addNotification: (state, action: PayloadAction<Omit<SystemState['notifications'][0], 'id' | 'timestamp'>>) => {
      state.notifications.push({
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
      });
      // Mantener solo las últimas 10 notificaciones
      if (state.notifications.length > 10) {
        state.notifications = state.notifications.slice(-10);
      }
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setFullscreen: (state, action: PayloadAction<boolean>) => {
      state.isFullscreen = action.payload;
    },
    setDarkMode: (state, action: PayloadAction<boolean>) => {
      state.isDarkMode = action.payload;
    },
  },
});

export const {
  setBackendStatus,
  setAppInfo,
  addNotification,
  clearNotifications,
  setFullscreen,
  setDarkMode,
} = systemSlice.actions;

export default systemSlice.reducer;
