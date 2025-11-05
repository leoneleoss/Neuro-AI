import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { AnimatePresence } from 'framer-motion';

// Páginas
import Dashboard from './pages/Dashboard';
import Analysis from './pages/Analysis';
import History from './pages/History';
import Settings from './pages/Settings';
import About from './pages/About';

// Componentes
import Layout from './components/Layout/Layout';
import DisclaimerDialog from './components/Dialogs/DisclaimerDialog';
import LoadingScreen from './components/Common/LoadingScreen';

// Hooks y servicios
import { useAppDispatch, useAppSelector } from './hooks/redux';
import { checkBackendStatus } from './services/api';
import { setBackendStatus } from './store/slices/systemSlice';

const App: React.FC = () => {
  const dispatch = useAppDispatch();
  const [loading, setLoading] = useState(true);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  
  useEffect(() => {
    // Verificar el estado del backend al iniciar
    const initializeApp = async () => {
      try {
        // Verificar si el disclaimer ya fue aceptado
        const accepted = await window.electronAPI.store.get('disclaimerAccepted');
        setDisclaimerAccepted(!!accepted);
        
        // Verificar estado del backend
        const backendStatus = await checkBackendStatus();
        dispatch(setBackendStatus({
          isRunning: backendStatus.status === 'healthy',
          modelsLoaded: backendStatus.models?.brain || backendStatus.models?.chest || false
        }));
      } catch (error) {
        console.error('Error inicializando la aplicación:', error);
        dispatch(setBackendStatus({
          isRunning: false,
          modelsLoaded: false
        }));
      } finally {
        setLoading(false);
      }
    };
    
    initializeApp();
    
    // Configurar listeners del menú
    const unsubscribers = [
      window.electronAPI.menu.onLoadImages(() => {
        window.location.href = '/analysis?action=load';
      }),
      window.electronAPI.menu.onLoadFolder(() => {
        window.location.href = '/analysis?action=loadFolder';
      }),
      window.electronAPI.menu.onShowHistory(() => {
        window.location.href = '/history';
      }),
      window.electronAPI.menu.onShowSettings(() => {
        window.location.href = '/settings';
      }),
      window.electronAPI.menu.onShowAbout(() => {
        window.location.href = '/about';
      })
    ];
    
    // Cleanup
    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, [dispatch]);
  
  const handleAcceptDisclaimer = async () => {
    await window.electronAPI.store.set('disclaimerAccepted', true);
    setDisclaimerAccepted(true);
  };
  
  if (loading) {
    return <LoadingScreen />;
  }
  
  return (
    <Router>
      <AnimatePresence mode="wait">
        {!disclaimerAccepted ? (
          <DisclaimerDialog 
            open={true}
            onAccept={handleAcceptDisclaimer}
          />
        ) : (
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/history" element={<History />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/about" element={<About />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Layout>
        )}
      </AnimatePresence>
    </Router>
  );
};

export default App;
