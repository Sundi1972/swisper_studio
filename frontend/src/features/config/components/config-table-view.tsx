import { Button } from '@mui/material';
import { Edit as EditIcon } from '@mui/icons-material';
import { DataTable, DataTableColumn } from '../../../components/data-table';
import type { ConfigSchemaTable, ConfigRecord } from '../types';

interface ConfigTableViewProps {
  schema: ConfigSchemaTable;
  records: ConfigRecord[];
  onEdit: (recordId: string) => void;
}

export function ConfigTableView({ schema, records, onEdit }: ConfigTableViewProps) {
  // Build columns from schema (show max 5 most important fields)
  const displayFields = schema.fields
    .filter(f => f.name === schema.primary_key || !f.immutable)
    .slice(0, 5);

  const columns: DataTableColumn[] = [
    ...displayFields.map((field) => ({
      id: field.name,
      label: field.name,
      sortable: true,
      required: field.required,
      render: (value: any) => {
        // Special rendering for boolean
        if (field.type === 'boolean') {
          return value ? '✓' : '✗';
        }
        return String(value || '-');
      }
    })),
    {
      id: 'actions',
      label: 'Actions',
      sortable: false,
      render: (_value: any, row: any) => (
        <Button
          size="small"
          startIcon={<EditIcon />}
          onClick={(e) => {
            e.stopPropagation(); // Prevent row click
            onEdit(row[schema.primary_key]);
          }}
        >
          Edit
        </Button>
      )
    }
  ];

  return (
    <DataTable
      title={schema.description || schema.name}
      subtitle={`${records.length} record${records.length !== 1 ? 's' : ''}`}
      columns={columns}
      data={records}
      searchPlaceholder="Search configurations..."
      emptyMessage="No records found"
    />
  );
}

