import { api, Branding } from './api';
import { Theme, applyBranding, defaultTheme } from '../theme';

export interface AppConfig {
  clientId: string;
  companyName: string;
  theme: Theme;
  logoUrl?: string;
  faviconUrl?: string;
  domain?: string;
  features: string[];
  apiBaseUrl: string;
}

const DEFAULT_CONFIG: AppConfig = {
  clientId: 'internal',
  companyName: 'AI Agency',
  theme: defaultTheme,
  features: ['articles', 'profile', 'settings'],
  apiBaseUrl: 'http://localhost:5001',
};

class BrandingService {
  private config: AppConfig = DEFAULT_CONFIG;
  private loaded = false;

  async load(clientId?: string, serverUrl?: string): Promise<AppConfig> {
    try {
      if (serverUrl) {
        await api.setBaseUrl(serverUrl);
      }
      await api.loadToken();

      if (clientId) {
        const branding = await api.getBranding(clientId);
        this.config = {
          clientId,
          companyName: branding.company_name || 'AI Agency',
          theme: applyBranding(branding),
          logoUrl: branding.logo_url,
          faviconUrl: branding.favicon_url,
          domain: branding.domain,
          features: ['articles', 'profile', 'settings'],
          apiBaseUrl: serverUrl || 'http://localhost:5001',
        };
      }
    } catch (err) {
      console.warn('Branding load failed, using defaults:', err);
      this.config = DEFAULT_CONFIG;
    }
    this.loaded = true;
    return this.config;
  }

  getConfig(): AppConfig {
    return this.config;
  }

  isLoaded(): boolean {
    return this.loaded;
  }

  updateTheme(branding: Record<string, any>): void {
    this.config.theme = applyBranding(branding, this.config.theme);
  }
}

export const brandingService = new BrandingService();
