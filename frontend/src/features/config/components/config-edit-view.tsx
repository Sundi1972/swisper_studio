import { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormHelperText,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import type { ConfigSchemaTable, ConfigRecord, ConfigSchemaField } from '../types';

interface ConfigEditViewProps {
  schema: ConfigSchemaTable;
  record: ConfigRecord;
  recordId: string;
  onBack: () => void;
  onSave: (data: Record<string, any>, description: string) => Promise<void>;
  saving?: boolean;
}

export function ConfigEditView({
  schema,
  record,
  recordId,
  onBack,
  onSave,
  saving
}: ConfigEditViewProps) {
  const [formData, setFormData] = useState<Record<string, any>>(record);
  const [description, setDescription] = useState('');

  const handleSubmit = async () => {
    await onSave(formData, description);
  };

  const renderField = (field: ConfigSchemaField) => {
    const value = formData[field.name];

    // Skip immutable fields (like primary key)
    if (field.immutable) {
      return null;
    }

    switch (field.type) {
      case 'select':
        return (
          <FormControl fullWidth key={field.name}>
            <InputLabel>{field.name}{field.required && ' *'}</InputLabel>
            <Select
              value={value || field.default || ''}
              onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
              label={`${field.name}${field.required ? ' *' : ''}`}
            >
              {field.options?.map((option) => (
                <MenuItem key={option} value={option}>
                  {option}
                </MenuItem>
              ))}
            </Select>
            {field.description && (
              <FormHelperText>{field.description}</FormHelperText>
            )}
          </FormControl>
        );

      case 'boolean':
        return (
          <FormControlLabel
            key={field.name}
            control={
              <Checkbox
                checked={value ?? field.default ?? false}
                onChange={(e) => setFormData({ ...formData, [field.name]: e.target.checked })}
              />
            }
            label={
              <Box>
                <Typography variant="body2">{field.name}{field.required && ' *'}</Typography>
                {field.description && (
                  <Typography variant="caption" color="text.secondary">
                    {field.description}
                  </Typography>
                )}
              </Box>
            }
          />
        );

      case 'number':
        return (
          <TextField
            key={field.name}
            fullWidth
            label={`${field.name}${field.required ? ' *' : ''}`}
            type="number"
            value={value ?? field.default ?? ''}
            onChange={(e) => setFormData({
              ...formData,
              [field.name]: e.target.value ? parseFloat(e.target.value) : null
            })}
            helperText={field.description}
            required={field.required}
            inputProps={{
              min: field.min,
              max: field.max,
              step: field.step || 0.1, // Default to 0.1 for decimals
            }}
          />
        );

      case 'textarea':
        return (
          <TextField
            key={field.name}
            fullWidth
            multiline
            rows={4}
            label={`${field.name}${field.required ? ' *' : ''}`}
            value={value || field.default || ''}
            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
            helperText={field.description}
            required={field.required}
          />
        );

      default: // string
        return (
          <TextField
            key={field.name}
            fullWidth
            label={`${field.name}${field.required ? ' *' : ''}`}
            value={value || field.default || ''}
            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
            helperText={field.description}
            required={field.required}
            inputProps={{
              maxLength: field.max_length,
            }}
          />
        );
    }
  };

  return (
    <Box>
      {/* Back Navigation */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <IconButton onClick={onBack} size="large">
          <ArrowBackIcon />
        </IconButton>
        <Box>
          <Typography variant="h6">
            Editing: {recordId}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {schema.description || schema.name}
          </Typography>
        </Box>
      </Box>

      <Card>
        <CardContent>
          {/* Version Description */}
          <TextField
            fullWidth
            label="Version Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe your changes..."
            sx={{ mb: 3 }}
          />

          {/* Config Fields */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {schema.fields.map((field) => renderField(field))}
          </Box>

          {/* Actions */}
          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Version'}
            </Button>
            <Button
              variant="outlined"
              onClick={onBack}
              disabled={saving}
            >
              Cancel
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

