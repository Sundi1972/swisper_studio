/**
 * TypeScript types for Config Management (Phase 4)
 */

// SAP Schema Types
export interface ConfigSchemaField {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'textarea' | 'json';
  required: boolean;
  immutable?: boolean;
  description: string;
  
  // Type-specific properties
  max_length?: number;
  min?: number;
  max?: number;
  step?: number;
  options?: string[];
  default?: any;
  
  // UI hints
  placeholder?: string;
  help_text?: string;
  ui_group?: string;
}

export interface ConfigSchemaTable {
  name: string;
  description: string;
  primary_key: string;
  fields: ConfigSchemaField[];
}

export interface ConfigSchema {
  version: string;
  tables: ConfigSchemaTable[];
}

// Config Version Types
export interface ConfigVersion {
  id: string;
  project_id: string;
  table_name: string;
  record_id: string;
  version_number: number;
  config_data: Record<string, any>;
  description: string | null;
  created_by: string;
  created_at: string;
  parent_version_id: string | null;
}

// Deployment Types
export interface ConfigDeployment {
  id: string;
  version_id: string;
  environment_id: string;
  status: 'deployed' | 'failed' | 'rolled_back';
  deployed_by: string;
  deployed_at: string;
  error_message: string | null;
}

export interface DeployRequest {
  version_id: string;
  deployed_by: string;
}

export interface DeployResponse {
  success: boolean;
  version: ConfigVersion;
  deployment: ConfigDeployment;
}

// Config Record (from Swisper SAP)
export interface ConfigRecord {
  [key: string]: any;
}

export interface ConfigRecordsResponse {
  table: string;
  records: ConfigRecord[];
  count: number;
}

