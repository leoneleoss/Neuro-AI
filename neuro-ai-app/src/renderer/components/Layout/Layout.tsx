import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Badge,
  Tooltip,
  Avatar,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Biotech as BiotechIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  Notifications as NotificationsIcon,
  Minimize as MinimizeIcon,
  Maximize as MaximizeIcon,
  Close as CloseIcon,
  CloudOff as CloudOffIcon,
  Cloud as CloudIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppSelector } from '../../hooks/redux';

const drawerWidth = 260;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const backendStatus = useAppSelector(state => state.system.backendStatus);
  const notifications = useAppSelector(state => state.system.notifications);
  const unreadNotifications = notifications.filter(n => n.type === 'error' || n.type === 'warning').length;

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/',
      color: '#2563eb',
    },
    {
      text: 'Análisis',
      icon: <BiotechIcon />,
      path: '/analysis',
      color: '#10b981',
    },
    {
      text: 'Historial',
      icon: <HistoryIcon />,
      path: '/history',
      color: '#f59e0b',
    },
    {
      text: 'Configuración',
      icon: <SettingsIcon />,
      path: '/settings',
      color: '#8b5cf6',
    },
    {
      text: 'Acerca de',
      icon: <InfoIcon />,
      path: '/about',
      color: '#64748b',
    },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const handleMinimize = () => {
    window.electronAPI.window.minimize();
  };

  const handleMaximize = () => {
    window.electronAPI.window.toggleMaximize();
  };

  const handleClose = () => {
    window.electronAPI.window.close();
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ 
        background: 'linear-gradient(135deg, #2563eb 0%, #60a5fa 100%)',
        minHeight: '80px !important',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
          <Avatar sx={{ 
            bgcolor: 'white', 
            color: 'primary.main',
            width: 48,
            height: 48,
          }}>
            <PsychologyIcon fontSize="large" />
          </Avatar>
          <Box>
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 700 }}>
              Neuro-AI
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.9)' }}>
              v2.0.0
            </Typography>
          </Box>
        </Box>
      </Toolbar>
      
      <Divider />
      
      <Box sx={{ p: 2 }}>
        <Chip
          icon={backendStatus.isRunning ? <CloudIcon /> : <CloudOffIcon />}
          label={backendStatus.isRunning ? 'Backend Activo' : 'Backend Inactivo'}
          color={backendStatus.isRunning ? 'success' : 'error'}
          size="small"
          sx={{ width: '100%' }}
        />
        {backendStatus.modelsLoaded && (
          <Chip
            icon={<PsychologyIcon />}
            label="Modelos Cargados"
            color="primary"
            size="small"
            sx={{ width: '100%', mt: 1 }}
          />
        )}
      </Box>
      
      <Divider />
      
      <List sx={{ flexGrow: 1, px: 1 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <motion.div
                style={{ width: '100%' }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <ListItemButton
                  onClick={() => handleNavigate(item.path)}
                  sx={{
                    borderRadius: 2,
                    backgroundColor: isActive ? `${item.color}15` : 'transparent',
                    borderLeft: isActive ? `4px solid ${item.color}` : '4px solid transparent',
                    '&:hover': {
                      backgroundColor: `${item.color}10`,
                    },
                  }}
                >
                  <ListItemIcon sx={{ 
                    color: isActive ? item.color : 'text.secondary',
                    minWidth: 40,
                  }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={item.text}
                    sx={{
                      '& .MuiTypography-root': {
                        fontWeight: isActive ? 600 : 400,
                        color: isActive ? item.color : 'text.primary',
                      }
                    }}
                  />
                </ListItemButton>
              </motion.div>
            </ListItem>
          );
        })}
      </List>
      
      <Divider />
      
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          © 2024 Neuro-AI Team
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: 'background.paper',
          color: 'text.primary',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find(item => item.path === location.pathname)?.text || 'Neuro-AI'}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Notificaciones">
              <IconButton color="inherit">
                <Badge badgeContent={unreadNotifications} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            
            <Box sx={{ 
              display: 'flex', 
              gap: 0.5,
              ml: 2,
              pl: 2,
              borderLeft: '1px solid',
              borderColor: 'divider',
            }}>
              <IconButton size="small" onClick={handleMinimize}>
                <MinimizeIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={handleMaximize}>
                <MaximizeIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={handleClose} sx={{ color: 'error.main' }}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              borderRight: 'none',
              boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              borderRight: '1px solid',
              borderColor: 'divider',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: 'background.default',
          overflow: 'auto',
        }}
      >
        <Toolbar />
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </Box>
    </Box>
  );
};

export default Layout;
