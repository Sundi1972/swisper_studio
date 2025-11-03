import React, { createContext, useContext, useState, useEffect } from 'react';

export interface Environment {
  id: string;
  project_id: string;
  env_type: 'dev' | 'staging' | 'production';
  swisper_url: string;
  created_at: string;
  updated_at: string;
}

interface EnvironmentContextType {
  currentEnvironment: Environment | null;
  setCurrentEnvironment: (env: Environment) => void;
  environments: Environment[];
  setEnvironments: (envs: Environment[]) => void;
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined);

export function EnvironmentProvider({ children }: { children: React.ReactNode }) {
  const [currentEnvironment, setCurrentEnvironment] = useState<Environment | null>(null);
  const [environments, setEnvironments] = useState<Environment[]>([]);

  // Auto-select dev environment when environments load
  useEffect(() => {
    if (environments.length > 0 && !currentEnvironment) {
      const devEnv = environments.find((e) => e.env_type === 'dev');
      if (devEnv) {
        setCurrentEnvironment(devEnv);
      }
    }
  }, [environments, currentEnvironment]);

  return (
    <EnvironmentContext.Provider
      value={{ currentEnvironment, setCurrentEnvironment, environments, setEnvironments }}
    >
      {children}
    </EnvironmentContext.Provider>
  );
}

export function useEnvironment() {
  const context = useContext(EnvironmentContext);
  if (!context) {
    throw new Error('useEnvironment must be used within EnvironmentProvider');
  }
  return context;
}

