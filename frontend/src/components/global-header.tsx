/**
 * Global Header Navigation
 * 
 * Persistent top navigation bar visible on all pages.
 * Provides quick access to key sections: Projects, Admin, System Architecture.
 */

import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Box,
  Button,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  FolderOpen as ProjectsIcon,
  AdminPanelSettings as AdminIcon,
  People as PeopleIcon,
  AttachMoney as MoneyIcon,
  KeyboardArrowDown as DownIcon,
} from '@mui/icons-material';
import { useState } from 'react';
import { SwisperLogo } from './swisper-logo';
import { UserMenu } from '@/features/auth/components/user-menu';
import { getUser } from '@/features/auth/utils/auth-storage';
import { EnvironmentSelector } from './environment-selector';
import { useParams } from 'react-router-dom';

export function GlobalHeader() {
  const navigate = useNavigate();
  const location = useLocation();
  const { projectId } = useParams();
  const user = getUser();
  
  const [adminMenuAnchor, setAdminMenuAnchor] = useState<null | HTMLElement>(null);

  const handleAdminMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAdminMenuAnchor(event.currentTarget);
  };

  const handleAdminMenuClose = () => {
    setAdminMenuAnchor(null);
  };

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  const isAdmin = user?.role === 'admin';

  return (
    <AppBar 
      position="sticky" 
      color="default" 
      elevation={0} 
      sx={{ 
        borderBottom: 1, 
        borderColor: 'divider',
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar>
        {/* Logo - Click to go home */}
        <Box sx={{ mr: 3, cursor: 'pointer' }} onClick={() => navigate('/projects')}>
          <SwisperLogo showStudio width={100} />
        </Box>

        {/* Main Navigation */}
        <Box sx={{ display: 'flex', gap: 1, flexGrow: 1 }}>
          {/* Projects */}
          <Button
            variant={isActive('/projects') && !isActive('/projects/') ? 'contained' : 'text'}
            startIcon={<ProjectsIcon />}
            onClick={() => navigate('/projects')}
            sx={{ 
              color: isActive('/projects') && !isActive('/projects/') ? 'primary.contrastText' : 'text.primary',
            }}
          >
            Projects
          </Button>

          {/* Admin (admin only) */}
          {isAdmin && (
            <>
              <Button
                variant={isActive('/admin') ? 'contained' : 'text'}
                startIcon={<AdminIcon />}
                endIcon={<DownIcon />}
                onClick={handleAdminMenuOpen}
                sx={{ 
                  color: isActive('/admin') ? 'primary.contrastText' : 'text.primary',
                }}
              >
                Admin
              </Button>
              <Menu
                anchorEl={adminMenuAnchor}
                open={Boolean(adminMenuAnchor)}
                onClose={handleAdminMenuClose}
              >
                <MenuItem 
                  onClick={() => { 
                    handleAdminMenuClose(); 
                    navigate('/admin/users'); 
                  }}
                >
                  <PeopleIcon sx={{ mr: 1 }} fontSize="small" />
                  User Management
                </MenuItem>
                <MenuItem 
                  onClick={() => { 
                    handleAdminMenuClose(); 
                    navigate('/admin/cost-management'); 
                  }}
                >
                  <MoneyIcon sx={{ mr: 1 }} fontSize="small" />
                  Cost Management
                </MenuItem>
              </Menu>
            </>
          )}
        </Box>

        {/* Right Side: Environment Selector (when in project) + User Menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {projectId && (
            <EnvironmentSelector />
          )}
          <UserMenu />
        </Box>
      </Toolbar>
    </AppBar>
  );
}

