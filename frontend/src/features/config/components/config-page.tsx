import { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Snackbar
} from '@mui/material';
import { useEnvironment } from '../../../contexts/environment-context';
import { 
  useConfigSchema, 
  useConfigRecords, 
  useConfigVersions, 
  useCreateVersion, 
  useDeployVersion 
} from '../hooks';
import { ConfigTableView } from './config-table-view';
import { ConfigEditView } from './config-edit-view';
import { VersionHistory } from './version-history';

/**
 * Configuration Management Page (Phase 4c).
 * 
 * Features:
 * - Environment-aware config editing
 * - Auto-generated forms from SAP schema
 * - Version management (create, deploy, history)
 * - Deploy to dev/staging/production
 */
export function ConfigPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentEnvironment } = useEnvironment();
  
  const [selectedTable, setSelectedTable] = useState('');
  const [editingRecord, setEditingRecord] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });
  
  const { data: schema, isLoading: schemaLoading } = useConfigSchema(
    projectId!,
    currentEnvironment?.id
  );
  
  const { data: recordsData, isLoading: recordsLoading } = useConfigRecords(
    projectId!,
    selectedTable
  );
  
  const { data: versions, isLoading: versionsLoading } = useConfigVersions(
    projectId!,
    selectedTable,
    editingRecord || undefined
  );
  
  const createVersion = useCreateVersion(projectId!);
  const deployVersion = useDeployVersion(projectId!);

  const handleEdit = (recordId: string) => {
    setEditingRecord(recordId);
  };

  const handleBack = () => {
    setEditingRecord(null);
  };

  const handleSaveVersion = async (configData: Record<string, any>, versionDescription: string) => {
    if (!selectedTable || !editingRecord) {
      setSnackbar({ open: true, message: 'Missing table or record', severity: 'error' });
      return;
    }

    try {
      await createVersion.mutateAsync({
        table_name: selectedTable,
        record_id: editingRecord,
        config_data: configData,
        description: versionDescription || undefined,
        created_by: 'user@example.com', // TODO: Get from auth context
      });

      setSnackbar({ open: true, message: 'Version saved successfully!', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: `Failed to save: ${error}`, severity: 'error' });
    }
  };

  const handleDeploy = async (versionId: string) => {
    if (!currentEnvironment) {
      setSnackbar({ open: true, message: 'No environment selected', severity: 'error' });
      return;
    }

    try {
      await deployVersion.mutateAsync({
        environmentId: currentEnvironment.id,
        versionId,
        deployedBy: 'user@example.com',
      });
      setSnackbar({ 
        open: true, 
        message: `Deployed to ${currentEnvironment.env_type} successfully!`, 
        severity: 'success' 
      });
    } catch (error) {
      setSnackbar({ open: true, message: `Deployment failed: ${error}`, severity: 'error' });
    }
  };

  if (!currentEnvironment) {
    return (
      <Alert severity="info">
        Loading environment...
      </Alert>
    );
  }

  if (schemaLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  const selectedTableSchema = schema?.tables.find((t: any) => t.name === selectedTable);
  const records = recordsData?.records || [];
  const currentRecord = editingRecord
    ? records.find((r) => r[selectedTableSchema?.primary_key || 'id'] === editingRecord)
    : null;

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Configuration Management
      </Typography>
      
      <Typography variant="body2" color="text.secondary" gutterBottom>
        Environment: <strong>{currentEnvironment.env_type.toUpperCase()}</strong>
        {' '}({currentEnvironment.swisper_url})
      </Typography>

      {/* Table Selector (always visible) */}
      {!editingRecord && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <FormControl fullWidth>
              <InputLabel>Config Table</InputLabel>
              <Select
                value={selectedTable}
                onChange={(e) => {
                  setSelectedTable(e.target.value);
                  setEditingRecord(null); // Reset editing when table changes
                }}
                label="Config Table"
              >
                {schema?.tables.map((table: any) => (
                  <MenuItem key={table.name} value={table.name}>
                    {table.description || table.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </CardContent>
        </Card>
      )}

      {/* Table View (when not editing) */}
      {!editingRecord && selectedTable && selectedTableSchema && (
        <Box sx={{ mb: 3 }}>
          {recordsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <ConfigTableView
              schema={selectedTableSchema}
              records={records}
              onEdit={handleEdit}
            />
          )}
        </Box>
      )}

      {/* Edit View (when editing a record) */}
      {editingRecord && selectedTableSchema && currentRecord && (
        <Box sx={{ mb: 3 }}>
          <ConfigEditView
            schema={selectedTableSchema}
            record={currentRecord}
            recordId={editingRecord}
            onBack={handleBack}
            onSave={handleSaveVersion}
            saving={createVersion.isPending}
          />
        </Box>
      )}

      {/* Version History (when editing) */}
      {editingRecord && versions && versions.length > 0 && (
        <VersionHistory
          versions={versions}
          onDeploy={handleDeploy}
          currentEnvironment={currentEnvironment}
          deploymentLoading={deployVersion.isPending}
        />
      )}
      
      {editingRecord && versionsLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={24} />
        </Box>
      )}
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}


