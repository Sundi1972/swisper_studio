/**
 * Trace list page
 * Following Langfuse UX patterns + Swisper MUI components
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import { DataGrid, GridColDef, GridToolbar } from '@mui/x-data-grid';

import { useTracesQuery } from '../hooks/use-traces-query';

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
    width: 300,
  },
];

export function TraceListPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useTracesQuery(projectId!, page);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box data-testid="trace-list-page">
      <Typography variant="h5" gutterBottom>
        Traces
      </Typography>

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
    </Box>
  );
}

