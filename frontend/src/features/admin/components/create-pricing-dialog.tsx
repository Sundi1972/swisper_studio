/**
 * Create Pricing Dialog (Admin Only)
 * 
 * Allows admins to create new model pricing entries.
 */

import { useState } from 'react';
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
import { createModelPricing, type CreateModelPricingRequest } from '@/api/model-pricing';

interface CreatePricingDialogProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function CreatePricingDialog({ open, onClose, onSuccess }: CreatePricingDialogProps) {
  const [hostingProvider, setHostingProvider] = useState('');
  const [modelName, setModelName] = useState('');
  const [type, setType] = useState('');
  const [description, setDescription] = useState('');
  const [inputPrice, setInputPrice] = useState('');
  const [outputPrice, setOutputPrice] = useState('');

  const { mutateAsync, isPending, error} = useMutation({
    mutationFn: (data: CreateModelPricingRequest) => createModelPricing(data),
    onSuccess: () => {
      onSuccess();
      handleReset();
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

  const handleReset = () => {
    setHostingProvider('');
    setModelName('');
    setType('');
    setDescription('');
    setInputPrice('');
    setOutputPrice('');
  };

  const handleClose = () => {
    if (!isPending) {
      handleReset();
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>Add Model Pricing</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error instanceof Error ? error.message : 'Failed to create pricing'}
            </Alert>
          )}

          <Box sx={{ mb: 2, mt: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Add global pricing for a model. This will apply to all projects.
            </Typography>
          </Box>

          <TextField
            label="Model Name"
            fullWidth
            value={hostingProvider}
            onChange={(e) => setHostingProvider(e.target.value)}
            required
            disabled={isPending}
            placeholder="e.g., inference-apertus-8b"
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
            placeholder="e.g., swiss-ai/Apertus-8B-Instruct-2509"
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
            placeholder="e.g., Chat, Embedding, Multimodal"
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
            placeholder="0.000"
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
            placeholder="0.000"
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
          <Button onClick={handleClose} disabled={isPending}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isPending}
          >
            {isPending ? 'Creating...' : 'Create Pricing'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

