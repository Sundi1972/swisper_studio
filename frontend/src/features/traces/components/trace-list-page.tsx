/**
 * Trace list page
 * Following Langfuse UX patterns + Swisper MUI components
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import DialogContentText from '@mui/material/DialogContentText';
import DeleteIcon from '@mui/icons-material/Delete';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import { DataGrid, GridColDef, GridToolbar, GridActionsCellItem } from '@mui/x-data-grid';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

import { useTracesQuery } from '../hooks/use-traces-query';

export function TraceListPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [traceToDelete, setTraceToDelete] = useState<string | null>(null);
  const [deleteAllDialogOpen, setDeleteAllDialogOpen] = useState(false);
  const { data, isLoading } = useTracesQuery(projectId!, page);

  // Delete single trace mutation
  const deleteTraceMutation = useMutation({
    mutationFn: (traceId: string) => apiClient.delete(`/traces/${traceId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['traces', projectId] });
      setDeleteDialogOpen(false);
      setTraceToDelete(null);
    },
  });

  // Delete all traces mutation
  const deleteAllTracesMutation = useMutation({
    mutationFn: () => apiClient.delete(`/traces?project_id=${projectId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['traces', projectId] });
      setDeleteAllDialogOpen(false);
    },
  });

  const handleDeleteClick = (traceId: string) => {
    setTraceToDelete(traceId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (traceToDelete) {
      deleteTraceMutation.mutate(traceToDelete);
    }
  };

  const handleDeleteAllClick = () => {
    setDeleteAllDialogOpen(true);
  };

  const handleConfirmDeleteAll = () => {
    deleteAllTracesMutation.mutate();
  };

  const columns: GridColDef[] = [
    {
      field: 'timestamp',
      headerName: 'Time',
      width: 200,
      valueFormatter: (value) => new Date(value).toLocaleString(),
    },
    {
      field: 'name',
      headerName: 'Name',
      width: 250,
    },
    {
      field: 'user_id',
      headerName: 'User ID',
      width: 200,
    },
    {
      field: 'session_id',
      headerName: 'Session ID',
      width: 200,
    },
    {
      field: 'id',
      headerName: 'Trace ID',
      width: 250,
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 100,
      getActions: (params) => [
        <GridActionsCellItem
          icon={<DeleteIcon />}
          label="Delete"
          onClick={(e) => {
            e.stopPropagation();
            handleDeleteClick(params.id as string);
          }}
          showInMenu={false}
        />,
      ],
    },
  ];

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box data-testid="trace-list-page">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">
          Traces
        </Typography>
        
        <Button
          variant="outlined"
          color="error"
          startIcon={<DeleteSweepIcon />}
          onClick={handleDeleteAllClick}
          disabled={!data?.data.length || deleteAllTracesMutation.isPending}
        >
          {deleteAllTracesMutation.isPending ? 'Deleting...' : 'Delete All Traces'}
        </Button>
      </Box>

      <DataGrid
        rows={data?.data || []}
        columns={columns}
        loading={isLoading}
        paginationMode="server"
        rowCount={data?.meta.total_items || 0}
        paginationModel={{ page: page - 1, pageSize: 50 }} // MUI uses 0-based pages
        onPaginationModelChange={(model) => setPage(model.page + 1)} // Convert to 1-based
        pageSizeOptions={[50]}
        autoHeight
        disableRowSelectionOnClick={false}
        onRowClick={(params) => navigate(`/projects/${projectId}/tracing/${params.id}`)}
        slots={{
          toolbar: GridToolbar,  // Enable search, filter, export toolbar
        }}
        slotProps={{
          toolbar: {
            showQuickFilter: true,  // Enable search box
            quickFilterProps: { debounceMs: 500 },
          },
        }}
        sx={{
          '& .MuiDataGrid-row': {
            cursor: 'pointer',
          },
        }}
      />

      {data?.data.length === 0 && (
        <Box textAlign="center" mt={4}>
          <Typography variant="body1" color="text.secondary">
            No traces yet. Send a trace from your Swisper instance to see it here.
          </Typography>
        </Box>
      )}

      {/* Delete Single Trace Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Trace?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this trace and all its observations?
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleteTraceMutation.isPending}
          >
            {deleteTraceMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete All Traces Confirmation Dialog */}
      <Dialog
        open={deleteAllDialogOpen}
        onClose={() => setDeleteAllDialogOpen(false)}
      >
        <DialogTitle>Delete All Traces?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            <strong>Warning:</strong> This will delete ALL traces and observations for this project.
            <br /><br />
            Total traces to delete: <strong>{data?.meta.total_items || 0}</strong>
            <br /><br />
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteAllDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDeleteAll}
            color="error"
            variant="contained"
            disabled={deleteAllTracesMutation.isPending}
          >
            {deleteAllTracesMutation.isPending ? 'Deleting...' : 'Delete All'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

