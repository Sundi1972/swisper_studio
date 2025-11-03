/**
 * User Management Page (Admin Only)
 * 
 * Allows admins to view and manage all users.
 */

import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Edit as EditIcon,
  PersonAdd as PersonAddIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { listUsers } from '@/api/users';
import type { User } from '@/types/auth';
import { EditUserDialog } from './edit-user-dialog';
import { CreateUserDialog } from './create-user-dialog';

export function UserManagementPage() {
  const queryClient = useQueryClient();
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  // Fetch users
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => listUsers(),
  });

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

  // Format last login
  const formatLastLogin = (lastLogin: string | null) => {
    if (!lastLogin) return 'Never';
    const date = new Date(lastLogin);
    return date.toLocaleString();
  };

  return (
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">Users</Typography>
          <Button
            variant="contained"
            startIcon={<PersonAddIcon />}
            onClick={() => setIsCreateDialogOpen(true)}
          >
            Add User
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error instanceof Error ? error.message : 'Failed to load users'}
          </Alert>
        )}

        {isLoading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Last Login</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data?.users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Chip
                        label={user.role.toUpperCase()}
                        size="small"
                        color={getRoleColor(user.role)}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={user.is_active ? 'Active' : 'Inactive'}
                        size="small"
                        color={user.is_active ? 'success' : 'default'}
                        variant={user.is_active ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                    <TableCell>{formatLastLogin(user.last_login)}</TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => setEditingUser(user)}
                        color="primary"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {data && data.users.length === 0 && (
          <Box textAlign="center" mt={4}>
            <Typography variant="body1" color="text.secondary">
              No users found.
            </Typography>
          </Box>
        )}

        {/* Create User Dialog */}
        <CreateUserDialog
          open={isCreateDialogOpen}
          onClose={() => setIsCreateDialogOpen(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
            setIsCreateDialogOpen(false);
          }}
        />

        {/* Edit User Dialog */}
        {editingUser && (
          <EditUserDialog
            user={editingUser}
            open={!!editingUser}
            onClose={() => setEditingUser(null)}
            onSuccess={() => {
              queryClient.invalidateQueries({ queryKey: ['users'] });
              setEditingUser(null);
            }}
          />
        )}
      </Box>
  );
}

