/**
 * Cost Management Page (Admin Only)
 * 
 * Allows admins to manage global model pricing.
 */

import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  IconButton,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { listModelPricing, deleteModelPricing, type ModelPricing } from '@/api/model-pricing';
import { DataTable, type DataTableColumn } from '@/components/data-table';
import { CreatePricingDialog } from './create-pricing-dialog';
import { EditPricingDialog } from './edit-pricing-dialog';

export function CostManagementPage() {
  const queryClient = useQueryClient();
  const [editingPricing, setEditingPricing] = useState<ModelPricing | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [deletingPricing, setDeletingPricing] = useState<ModelPricing | null>(null);

  // Fetch pricing
  const { data, isLoading, error } = useQuery({
    queryKey: ['model-pricing'],
    queryFn: () => listModelPricing(),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (pricingId: string) => deleteModelPricing(pricingId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['model-pricing'] });
      setDeletingPricing(null);
    },
  });

  // Format price for display
  const formatPrice = (price: string | number) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return `CHF ${numPrice.toFixed(3)}`;
  };

  // Table columns matching CSV structure
  const columns: DataTableColumn[] = [
    {
      id: 'hosting_provider',
      label: 'Model Name',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {value}
        </Typography>
      ),
    },
    {
      id: 'model_name',
      label: 'Model',
      sortable: true,
    },
    {
      id: 'type',
      label: 'Type',
      sortable: true,
    },
    {
      id: 'input_price_per_million',
      label: 'Input (/M Tokens)',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {formatPrice(value)}
        </Typography>
      ),
    },
    {
      id: 'output_price_per_million',
      label: 'Output (/M Tokens)',
      sortable: true,
      render: (value) => (
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {formatPrice(value)}
        </Typography>
      ),
    },
    {
      id: 'description',
      label: 'Description',
      sortable: false,
      render: (value) => (
        <Typography variant="body2" sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {value || '-'}
        </Typography>
      ),
    },
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_, row: ModelPricing) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setEditingPricing(row);
            }}
            color="primary"
          >
            <EditIcon fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              setDeletingPricing(row);
            }}
            color="error"
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Cost Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsCreateDialogOpen(true)}
        >
          Add Model Pricing
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error instanceof Error ? error.message : 'Failed to load model pricing'}
        </Alert>
      )}

      {isLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <DataTable
          columns={columns}
          data={data || []}
          searchPlaceholder="Search by provider or model name..."
          emptyMessage="No model pricing configured."
        />
      )}

      {/* Create Pricing Dialog */}
      <CreatePricingDialog
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['model-pricing'] });
          setIsCreateDialogOpen(false);
        }}
      />

      {/* Edit Pricing Dialog */}
      {editingPricing && (
        <EditPricingDialog
          pricing={editingPricing}
          open={!!editingPricing}
          onClose={() => setEditingPricing(null)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['model-pricing'] });
            setEditingPricing(null);
          }}
        />
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deletingPricing}
        onClose={() => setDeletingPricing(null)}
      >
        <DialogTitle>Delete Model Pricing</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete pricing for{' '}
            <strong>
              {deletingPricing?.hosting_provider}/{deletingPricing?.model_name}
            </strong>
            ? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeletingPricing(null)}>Cancel</Button>
          <Button
            onClick={() => deletingPricing && deleteMutation.mutate(deletingPricing.id)}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

