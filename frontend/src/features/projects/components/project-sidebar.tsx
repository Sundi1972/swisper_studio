import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Toolbar,
  Typography,
  Divider,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Search as SearchIcon,
  Timeline as TimelineIcon,
  AccountTree as GraphIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const DRAWER_WIDTH = 240;

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  disabled?: boolean;
}

interface ProjectSidebarProps {
  projectId: string;
}

/**
 * Project navigation sidebar.
 * 
 * Provides access to all project features:
 * - Overview (dashboard with key metrics)
 * - Tracing (trace list and details)
 * - Analytics (cost analysis, performance metrics) - Phase 3+
 * - Graphs (system architecture, trace visualization) - Phase 3
 * - Configuration (project settings, model pricing)
 */
export function ProjectSidebar({ projectId }: ProjectSidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems: MenuItem[] = [
    {
      id: 'overview',
      label: 'Overview',
      icon: <DashboardIcon />,
      path: `/projects/${projectId}`,
    },
    {
      id: 'tracing',
      label: 'Tracing',
      icon: <SearchIcon />,
      path: `/projects/${projectId}/tracing`,
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <TimelineIcon />,
      path: `/projects/${projectId}/analytics`,
      disabled: true, // Phase 3+
    },
    {
      id: 'graphs',
      label: 'Graphs',
      icon: <GraphIcon />,
      path: `/projects/${projectId}/graphs`,
      disabled: true, // Phase 3
    },
    {
      id: 'config',
      label: 'Configuration',
      icon: <SettingsIcon />,
      path: `/projects/${projectId}/config`,
    },
  ];

  const isActive = (path: string) => {
    // Exact match for overview
    if (path === `/projects/${projectId}`) {
      return location.pathname === path;
    }
    // Prefix match for nested routes
    return location.pathname.startsWith(path);
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          bgcolor: 'background.paper',
          borderRight: 1,
          borderColor: 'divider',
        },
      }}
    >
      {/* Logo/Title area */}
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          SwisperStudio
        </Typography>
      </Toolbar>
      
      <Divider />
      
      {/* Navigation menu */}
      <Box sx={{ overflow: 'auto', mt: 2 }}>
        <List>
          {menuItems.map((item) => (
            <ListItemButton
              key={item.id}
              selected={isActive(item.path)}
              onClick={() => !item.disabled && navigate(item.path)}
              disabled={item.disabled}
              sx={{
                mx: 1,
                borderRadius: 1,
                '&.Mui-selected': {
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    bgcolor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: item.disabled ? 'action.disabled' : 'inherit',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                secondary={item.disabled ? 'Coming soon' : undefined}
              />
            </ListItemButton>
          ))}
        </List>
      </Box>
    </Drawer>
  );
}

