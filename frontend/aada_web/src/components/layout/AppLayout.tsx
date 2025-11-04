import { useState, useEffect, useCallback } from 'react';
import {
  AppBar,
  Avatar,
  BottomNavigation,
  BottomNavigationAction,
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  DashboardOutlined,
  MenuBookOutlined,
  PaymentsOutlined,
  WorkOutline,
  DescriptionOutlined,
  Menu as MenuIcon,
  DarkModeOutlined,
  LightModeOutlined,
} from '@mui/icons-material';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/auth-store';
import { useThemeStore } from '@/stores/theme-store';

const drawerWidth = 240;

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: <DashboardOutlined fontSize="small" /> },
  { label: 'Modules', path: '/modules', icon: <MenuBookOutlined fontSize="small" /> },
  { label: 'Payments', path: '/payments', icon: <PaymentsOutlined fontSize="small" /> },
  { label: 'Externships', path: '/externships', icon: <WorkOutline fontSize="small" /> },
  { label: 'Documents', path: '/documents', icon: <DescriptionOutlined fontSize="small" /> },
];

export default function AppLayout() {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));
  const navigate = useNavigate();
  const location = useLocation();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { user, clearSession } = useAuthStore();
  const { mode, toggle } = useThemeStore();

  // 🧠 Use callback wrappers so they don’t re-create each render
  const handleNavigate = useCallback(
    (path: string) => {
      if (location.pathname !== path) navigate(path);
      setDrawerOpen(false);
    },
    [navigate, location.pathname],
  );

  const handleLogout = useCallback(() => {
    clearSession();
    navigate('/login', { replace: true });
  }, [clearSession, navigate]);

  const activePath = location.pathname;
  const activeIndex = navItems.findIndex(
    (item) => activePath === item.path || activePath.startsWith(`${item.path}/`),
  );

  const themeIcon =
    mode === 'light' ? <DarkModeOutlined fontSize="small" /> : <LightModeOutlined fontSize="small" />;

  // Ensure initial nav highlighting stabilizes once
  useEffect(() => {
    if (activeIndex === -1) {
      navigate('/dashboard', { replace: true });
    }
  }, [activeIndex, navigate]);

  const drawerContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ px: 2, py: 3 }}>
        <Typography variant="h6" fontWeight={700}>
          AADA Student
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Atlanta Academy of Dental Assisting
        </Typography>
      </Box>
      <Divider />
      <List sx={{ flexGrow: 1 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={item.path}
            selected={activePath === item.path || activePath.startsWith(`${item.path}/`)}
            onClick={() => handleNavigate(item.path)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
      <Divider />
      <Box sx={{ px: 2, py: 3 }}>
        <Typography variant="body2" color="text.secondary">
          Need help? Email{' '}
          <Typography component="span" fontWeight={600}>
            support@aada.edu
          </Typography>
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        color="inherit"
        sx={{
          bgcolor: 'background.paper',
          borderBottom: `1px solid ${theme.palette.divider}`,
          ml: isDesktop ? `${drawerWidth}px` : 0,
          width: isDesktop ? `calc(100% - ${drawerWidth}px)` : '100%',
        }}
        elevation={0}
      >
        <Toolbar sx={{ display: 'flex', gap: 1 }}>
          {!isDesktop && (
            <IconButton edge="start" onClick={() => setDrawerOpen(true)} aria-label="Open navigation menu">
              <MenuIcon />
            </IconButton>
          )}
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="subtitle1" fontWeight={600}>
              Atlanta Academy of Dental Assisting
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Student Learning Portal
            </Typography>
          </Box>
          <Tooltip title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}>
            <IconButton color="primary" onClick={toggle}>
              {themeIcon}
            </IconButton>
          </Tooltip>
          <Typography
            variant="subtitle1"
            sx={{
              ml: 2,
              color: '#d4af37',
              fontWeight: 600,
              display: { xs: 'none', sm: 'block' }
            }}
          >
            Welcome, {user?.first_name ?? 'Student'}!
          </Typography>
          <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} sx={{ ml: 1 }} size="small">
            <Avatar sx={{ width: 32, height: 32 }}>
              {user?.first_name?.[0]?.toUpperCase() ?? 'A'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <MenuItem disabled>
              <Box>
                <Typography variant="subtitle2">
                  {user ? `${user.first_name} ${user.last_name}` : 'Student'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {user?.email ?? 'student@aada.edu'}
                </Typography>
              </Box>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>Sign out</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {isDesktop ? (
        <Drawer
          variant="permanent"
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            [`& .MuiDrawer-paper`]: {
              width: drawerWidth,
              boxSizing: 'border-box',
              borderRight: `1px solid ${theme.palette.divider}`,
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      ) : (
        <Drawer
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            [`& .MuiDrawer-paper`]: {
              width: drawerWidth,
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          mt: 8,
          p: { xs: 2, sm: 3 },
          minHeight: '100vh',
          width: '100%',
        }}
      >
        <Outlet />
      </Box>

      {!isDesktop && (
        <Box
          component="nav"
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            borderTop: `1px solid ${theme.palette.divider}`,
            bgcolor: 'background.paper',
          }}
        >
          <BottomNavigation
            value={activeIndex === -1 ? 0 : activeIndex}
            onChange={(_, newValue) => handleNavigate(navItems[newValue].path)}
            showLabels
          >
            {navItems.map((item) => (
              <BottomNavigationAction key={item.path} label={item.label} icon={item.icon} />
            ))}
          </BottomNavigation>
        </Box>
      )}
    </Box>
  );
}
