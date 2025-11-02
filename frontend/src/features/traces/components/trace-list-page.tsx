/**
 * Trace list page
 * Following Langfuse UX patterns + Swisper MUI components
 */

import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { styled } from '@mui/material/styles';

import { useTracesQuery } from '../hooks/use-traces-query';

const Container = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
}));

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
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container data-testid="trace-list-page">
      <Box display="flex" alignItems="center" mb={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/projects')}
          sx={{ mr: 2 }}
        >
          Back to Projects
        </Button>
        <Typography variant="h4">Traces</Typography>
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
        disableRowSelectionOnClick
      />

      {data?.data.length === 0 && (
        <Box textAlign="center" mt={4}>
          <Typography variant="body1" color="text.secondary">
            No traces yet. Send a trace from your Swisper instance to see it here.
          </Typography>
        </Box>
      )}
    </Container>
  );
}

