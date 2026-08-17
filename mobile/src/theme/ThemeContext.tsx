import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Theme, defaultTheme, applyBranding } from '../theme';
import { brandingService, AppConfig } from '../services/branding';
import { api } from '../services/api';

interface ThemeContextType {
  theme: Theme;
  config: AppConfig;
  loading: boolean;
  refresh: (clientId?: string, serverUrl?: string) => Promise<void>;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: defaultTheme,
  config: brandingService.getConfig(),
  loading: true,
  refresh: async () => {},
});

export function ThemeProvider({ children, clientId, serverUrl }: {
  children: ReactNode;
  clientId?: string;
  serverUrl?: string;
}) {
  const [theme, setTheme] = useState<Theme>(defaultTheme);
  const [config, setConfig] = useState<AppConfig>(brandingService.getConfig());
  const [loading, setLoading] = useState(true);

  const refresh = async (cId?: string, sUrl?: string) => {
    setLoading(true);
    const cfg = await brandingService.load(cId || clientId, sUrl || serverUrl);
    setTheme(cfg.theme);
    setConfig(cfg);
    setLoading(false);
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, config, loading, refresh }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
