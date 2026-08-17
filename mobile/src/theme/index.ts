export interface ThemeColors {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  card: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  border: string;
  error: string;
  success: string;
  warning: string;
  info: string;
}

export interface ThemeFonts {
  heading: string;
  body: string;
  mono: string;
}

export interface Theme {
  colors: ThemeColors;
  fonts: ThemeFonts;
  borderRadius: number;
  spacing: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
}

export const defaultTheme: Theme = {
  colors: {
    primary: '#6366f1',
    primaryLight: '#818cf8',
    primaryDark: '#4f46e5',
    secondary: '#8b5cf6',
    accent: '#06b6d4',
    background: '#f8fafc',
    surface: '#ffffff',
    card: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    textMuted: '#94a3b8',
    border: '#e2e8f0',
    error: '#ef4444',
    success: '#22c55e',
    warning: '#f59e0b',
    info: '#3b82f6',
  },
  fonts: {
    heading: 'System',
    body: 'System',
    mono: 'Courier',
  },
  borderRadius: 12,
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
};

export function applyBranding(branding: Record<string, any>, base: Theme = defaultTheme): Theme {
  const theme = { ...base };

  if (branding.primary_color) {
    theme.colors.primary = branding.primary_color;
    theme.colors.primaryLight = lightenColor(branding.primary_color, 20);
    theme.colors.primaryDark = darkenColor(branding.primary_color, 20);
  }
  if (branding.secondary_color) {
    theme.colors.secondary = branding.secondary_color;
  }
  if (branding.accent_color) {
    theme.colors.accent = branding.accent_color;
  }
  if (branding.background_color) {
    theme.colors.background = branding.background_color;
  }
  if (branding.text_color) {
    theme.colors.text = branding.text_color;
  }
  if (branding.border_radius) {
    theme.borderRadius = branding.border_radius;
  }
  if (branding.font_family) {
    theme.fonts.heading = branding.font_family;
    theme.fonts.body = branding.font_family;
  }

  return theme;
}

function lightenColor(hex: string, percent: number): string {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.min(255, (num >> 16) + Math.round(255 * percent / 100));
  const g = Math.min(255, ((num >> 8) & 0x00FF) + Math.round(255 * percent / 100));
  const b = Math.min(255, (num & 0x0000FF) + Math.round(255 * percent / 100));
  return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, '0')}`;
}

function darkenColor(hex: string, percent: number): string {
  const num = parseInt(hex.replace('#', ''), 16);
  const r = Math.max(0, (num >> 16) - Math.round(255 * percent / 100));
  const g = Math.max(0, ((num >> 8) & 0x00FF) - Math.round(255 * percent / 100));
  const b = Math.max(0, (num & 0x0000FF) - Math.round(255 * percent / 100));
  return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, '0')}`;
}
