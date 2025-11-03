/**
 * User Menu Component
 * 
 * Displays user info and logout option in header.
 */

import { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  Typography,
  Divider,
  Box,
  Chip,
} from '@mui/material';
import {
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { getUser, clearAuth } from '../utils/auth-storage';

export function UserMenu() {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const user = getUser();

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleClose();
    clearAuth();
    navigate('/login');
  };

  if (!user) {
    return null;
  }

  // Role color mapping
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'developer':
        return 'primary';
      case 'qa':
        return 'warning';
      case 'viewer':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <>
      <IconButton
        onClick={handleClick}
        size="large"
        edge="end"
        color="inherit"
        aria-label="user menu"
      >
        <AccountCircleIcon />
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {/* User Info */}
        <Box sx={{ px: 2, py: 1.5, minWidth: 250 }}>
          <Typography variant="subtitle1" fontWeight="bold">
            {user.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {user.email}
          </Typography>
          <Chip
            label={user.role.toUpperCase()}
            size="small"
            color={getRoleColor(user.role)}
            sx={{ textTransform: 'uppercase' }}
          />
        </Box>

        <Divider />

        {/* Admin: User Management */}
        {user.role === 'admin' && (
          <MenuItem onClick={() => { handleClose(); navigate('/admin/users'); }}>
            <PeopleIcon sx={{ mr: 1 }} fontSize="small" />
            Manage Users
          </MenuItem>
        )}

        {/* Logout */}
        <MenuItem onClick={handleLogout}>
          <LogoutIcon sx={{ mr: 1 }} fontSize="small" />
          Logout
        </MenuItem>
      </Menu>
    </>
  );
}

