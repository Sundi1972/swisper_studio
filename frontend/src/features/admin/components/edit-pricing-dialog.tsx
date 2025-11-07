/**
 * Edit Pricing Dialog (Admin Only)
 * 
 * Allows admins to edit existing model pricing entries.
 */

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  Box,
  Typography,
} from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { updateModelPricing, type ModelPricing, type UpdateModelPricingRequest } from '@/api/model-pricing';

interface EditPricingDialogProps {
  pricing: ModelPricing;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function EditPricingDialog({ pricing, open, onClose, onSuccess }: EditPricingDialogProps) {
  const [hostingProvider, setHostingProvider] = useState('');
  const [modelName, setModelName] = useState('');
  const [type, setType] = useState('');
  const [description, setDescription] = useState('');
  const [inputPrice, setInputPrice] = useState('');
  const [outputPrice, setOutputPrice] = useState('');

  // Initialize form with pricing data
  useEffect(() => {
    if (pricing) {
      setHostingProvider(pricing.hosting_provider);
      setModelName(pricing.model_name);
      setType(pricing.type);
      setDescription(pricing.description || '');
      setInputPrice(pricing.input_price_per_million.toString());
      setOutputPrice(pricing.output_price_per_million.toString());
    }
  }, [pricing]);

  const { mutateAsync, isPending, error } = useMutation({
    mutationFn: (data: UpdateModelPricingRequest) => updateModelPricing(pricing.id, data),
    onSuccess: () => {
      onSuccess();
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await mutateAsync({
      hosting_provider: hostingProvider,
      model_name: modelName,
      type: type,
      description: description || undefined,
      input_price_per_million: parseFloat(inputPrice),
      output_price_per_million: parseFloat(outputPrice),
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Edit Model Pricing</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error instanceof Error ? error.message : 'Failed to update pricing'}
            </Alert>
          )}

          <Box sx={{ mb: 2, mt: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Update pricing for{' '}
              <strong>
                {pricing.hosting_provider}/{pricing.model_name}
              </strong>
            </Typography>
          </Box>

          <TextField
            label="Model Name"
            fullWidth
            value={hostingProvider}
            onChange={(e) => setHostingProvider(e.target.value)}
            required
            disabled={isPending}
            helperText="Short model identifier"
            sx={{ mb: 2 }}
            autoFocus
          />

          <TextField
            label="Model"
            fullWidth
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            required
            disabled={isPending}
            helperText="Full model path"
            sx={{ mb: 2 }}
          />

          <TextField
            label="Type"
            fullWidth
            value={type}
            onChange={(e) => setType(e.target.value)}
            required
            disabled={isPending}
            helperText="Model type"
            sx={{ mb: 2 }}
          />

          <TextField
            label="Input Price (CHF per 1M tokens)"
            type="number"
            fullWidth
            value={inputPrice}
            onChange={(e) => setInputPrice(e.target.value)}
            required
            disabled={isPending}
            inputProps={{ min: 0, step: 0.001 }}
            sx={{ mb: 2 }}
          />

          <TextField
            label="Output Price (CHF per 1M tokens)"
            type="number"
            fullWidth
            value={outputPrice}
            onChange={(e) => setOutputPrice(e.target.value)}
            required
            disabled={isPending}
            inputProps={{ min: 0, step: 0.001 }}
            sx={{ mb: 2 }}
          />

          <TextField
            label="Description"
            fullWidth
            multiline
            rows={2}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isPending}
            placeholder="Model description and capabilities"
          />
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isPending}
          >
            {isPending ? 'Updating...' : 'Update Pricing'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

