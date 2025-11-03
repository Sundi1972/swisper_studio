import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  InputAdornment,
  TableSortLabel,
  Box,
  Typography
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';

export interface DataTableColumn {
  id: string;
  label: string;
  sortable?: boolean;
  required?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
}

interface DataTableProps {
  title?: string;
  subtitle?: string;
  columns: DataTableColumn[];
  data: any[];
  searchPlaceholder?: string;
  onRowClick?: (row: any) => void;
  emptyMessage?: string;
}

type SortDirection = 'asc' | 'desc' | null;

export function DataTable({
  title,
  subtitle,
  columns,
  data,
  searchPlaceholder = 'Search...',
  onRowClick,
  emptyMessage = 'No records found'
}: DataTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);

  // Filter data based on search term (searches across ALL fields)
  const filteredData = data.filter((row) => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    const rowValues = Object.values(row);
    
    return rowValues.some((value) =>
      String(value).toLowerCase().includes(searchLower)
    );
  });

  // Sort filtered data
  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortColumn || !sortDirection) return 0;

    const aValue = a[sortColumn];
    const bValue = b[sortColumn];

    // Handle null/undefined
    if (aValue == null) return 1;
    if (bValue == null) return -1;

    // Numeric sort
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    }

    // String sort
    const aStr = String(aValue).toLowerCase();
    const bStr = String(bValue).toLowerCase();
    
    if (sortDirection === 'asc') {
      return aStr.localeCompare(bStr);
    } else {
      return bStr.localeCompare(aStr);
    }
  });

  const handleSort = (columnId: string) => {
    const column = columns.find((c) => c.id === columnId);
    if (!column?.sortable) return;

    if (sortColumn === columnId) {
      // Cycle through: asc → desc → null
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortColumn(null);
      }
    } else {
      setSortColumn(columnId);
      setSortDirection('asc');
    }
  };

  return (
    <Paper>
      {/* Header */}
      {(title || subtitle) && (
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          {title && (
            <Typography variant="h6">
              {title}
            </Typography>
          )}
          {subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
      )}

      {/* Search Box */}
      <Box sx={{ p: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder={searchPlaceholder}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {/* Table */}
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell key={column.id}>
                  {column.sortable ? (
                    <TableSortLabel
                      active={sortColumn === column.id}
                      direction={sortColumn === column.id ? (sortDirection as 'asc' | 'desc') : 'asc'}
                      onClick={() => handleSort(column.id)}
                    >
                      {column.label}
                      {column.required && <span style={{ color: '#f44336', marginLeft: 4 }}>*</span>}
                    </TableSortLabel>
                  ) : (
                    <>
                      {column.label}
                      {column.required && <span style={{ color: '#f44336', marginLeft: 4 }}>*</span>}
                    </>
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedData.length === 0 && (
              <TableRow>
                <TableCell colSpan={columns.length} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                    {searchTerm ? `No results for "${searchTerm}"` : emptyMessage}
                  </Typography>
                </TableCell>
              </TableRow>
            )}

            {sortedData.map((row, index) => (
              <TableRow
                key={index}
                hover
                onClick={() => onRowClick?.(row)}
                sx={{ cursor: onRowClick ? 'pointer' : 'default' }}
              >
                {columns.map((column) => (
                  <TableCell key={column.id}>
                    {column.render
                      ? column.render(row[column.id], row)
                      : String(row[column.id] || '-')}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}

