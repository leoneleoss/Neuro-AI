import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface ImageFile {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  dataUrl?: string;
  preview?: string;
}

export interface AnalysisResult {
  id: string;
  fileName: string;
  modelType: 'brain' | 'chest';
  prediction: string;
  confidence: number;
  allPredictions: Record<string, number>;
  medicalInfo: {
    titulo: string;
    descripcion: string;
    recomendaciones: string;
    nivel: 'ALTO' | 'MEDIO' | 'BAJO';
    urgencia: string;
  };
  timestamp: string;
  success: boolean;
  error?: string;
}

interface AnalysisState {
  images: ImageFile[];
  currentImageIndex: number;
  results: AnalysisResult[];
  isAnalyzing: boolean;
  analysisProgress: number;
  currentAnalysisType: 'auto' | 'brain' | 'chest';
  batchMode: boolean;
  selectedResults: string[];
}

const initialState: AnalysisState = {
  images: [],
  currentImageIndex: 0,
  results: [],
  isAnalyzing: false,
  analysisProgress: 0,
  currentAnalysisType: 'auto',
  batchMode: false,
  selectedResults: [],
};

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    setImages: (state, action: PayloadAction<ImageFile[]>) => {
      state.images = action.payload;
      state.currentImageIndex = 0;
    },
    addImages: (state, action: PayloadAction<ImageFile[]>) => {
      state.images = [...state.images, ...action.payload];
    },
    removeImage: (state, action: PayloadAction<string>) => {
      state.images = state.images.filter(img => img.id !== action.payload);
      if (state.currentImageIndex >= state.images.length && state.currentImageIndex > 0) {
        state.currentImageIndex--;
      }
    },
    clearImages: (state) => {
      state.images = [];
      state.currentImageIndex = 0;
    },
    setCurrentImageIndex: (state, action: PayloadAction<number>) => {
      state.currentImageIndex = action.payload;
    },
    addResult: (state, action: PayloadAction<AnalysisResult>) => {
      state.results.push(action.payload);
    },
    setResults: (state, action: PayloadAction<AnalysisResult[]>) => {
      state.results = action.payload;
    },
    clearResults: (state) => {
      state.results = [];
      state.selectedResults = [];
    },
    removeResult: (state, action: PayloadAction<string>) => {
      state.results = state.results.filter(r => r.id !== action.payload);
      state.selectedResults = state.selectedResults.filter(id => id !== action.payload);
    },
    setIsAnalyzing: (state, action: PayloadAction<boolean>) => {
      state.isAnalyzing = action.payload;
      if (!action.payload) {
        state.analysisProgress = 0;
      }
    },
    setAnalysisProgress: (state, action: PayloadAction<number>) => {
      state.analysisProgress = action.payload;
    },
    setAnalysisType: (state, action: PayloadAction<'auto' | 'brain' | 'chest'>) => {
      state.currentAnalysisType = action.payload;
    },
    setBatchMode: (state, action: PayloadAction<boolean>) => {
      state.batchMode = action.payload;
    },
    toggleResultSelection: (state, action: PayloadAction<string>) => {
      const id = action.payload;
      const index = state.selectedResults.indexOf(id);
      if (index >= 0) {
        state.selectedResults.splice(index, 1);
      } else {
        state.selectedResults.push(id);
      }
    },
    selectAllResults: (state) => {
      state.selectedResults = state.results.map(r => r.id);
    },
    deselectAllResults: (state) => {
      state.selectedResults = [];
    },
  },
});

export const {
  setImages,
  addImages,
  removeImage,
  clearImages,
  setCurrentImageIndex,
  addResult,
  setResults,
  clearResults,
  removeResult,
  setIsAnalyzing,
  setAnalysisProgress,
  setAnalysisType,
  setBatchMode,
  toggleResultSelection,
  selectAllResults,
  deselectAllResults,
} = analysisSlice.actions;

export default analysisSlice.reducer;
