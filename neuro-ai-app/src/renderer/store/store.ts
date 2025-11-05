import { configureStore } from '@reduxjs/toolkit';
import analysisReducer from './slices/analysisSlice';
import systemReducer from './slices/systemSlice';
import historyReducer from './slices/historySlice';
import settingsReducer from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    analysis: analysisReducer,
    system: systemReducer,
    history: historyReducer,
    settings: settingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['analysis/setImages'],
        ignoredPaths: ['analysis.images'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
