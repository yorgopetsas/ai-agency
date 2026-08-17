import axios, { AxiosInstance } from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_KEY = 'API_KEY';
const AUTH_TOKEN = 'AUTH_TOKEN';
const USER_DATA = 'USER_DATA';
const SERVER_URL = 'SERVER_URL';

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  client_id?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface Article {
  id: string;
  headline: string;
  overview: string;
  paragraphs: string[];
  source_url: string;
  image_url: string;
  rating?: { total: number };
  provider?: string;
  published_at: string;
  date_formatted: string;
}

export interface Branding {
  client_id: string;
  company_name: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  background_color: string;
  text_color: string;
  font_family: string;
  border_radius: number;
  logo_url?: string;
  favicon_url?: string;
  domain?: string;
}

export interface ClientPlan {
  plan_id: string;
  name: string;
  quotas: Record<string, number>;
  features: string[];
}

class ApiService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      timeout: 15000,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  async getBaseUrl(): Promise<string> {
    const url = await SecureStore.getItemAsync(SERVER_URL);
    return url || 'http://localhost:5001';
  }

  async setBaseUrl(url: string): Promise<void> {
    await SecureStore.setItemAsync(SERVER_URL, url);
    this.client.defaults.baseURL = url;
  }

  async loadToken(): Promise<void> {
    this.token = await SecureStore.getItemAsync(AUTH_TOKEN);
    if (this.token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
    }
  }

  async saveAuth(data: AuthResponse): Promise<void> {
    this.token = data.access_token;
    await SecureStore.setItemAsync(AUTH_TOKEN, data.access_token);
    await SecureStore.setItemAsync(USER_DATA, JSON.stringify(data.user));
    this.client.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
  }

  async clearAuth(): Promise<void> {
    this.token = null;
    await SecureStore.deleteItemAsync(AUTH_TOKEN);
    await SecureStore.deleteItemAsync(USER_DATA);
    delete this.client.defaults.headers.common['Authorization'];
  }

  async getUser(): Promise<User | null> {
    const data = await SecureStore.getItemAsync(USER_DATA);
    return data ? JSON.parse(data) : null;
  }

  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    const base = await this.getBaseUrl();
    const { data } = await axios.post(`${base}/api/auth/login`, { email, password });
    await this.saveAuth(data);
    return data;
  }

  async register(email: string, password: string, name: string, clientId?: string): Promise<AuthResponse> {
    const base = await this.getBaseUrl();
    const { data } = await axios.post(`${base}/api/auth/register`, {
      email, password, name, client_id: clientId,
    });
    await this.saveAuth(data);
    return data;
  }

  async changePassword(current: string, newPassword: string): Promise<void> {
    const base = await this.getBaseUrl();
    await this.client.put(`${base}/api/auth/password`, {
      current_password: current, new_password: newPassword,
    });
  }

  // Articles
  async getArticles(): Promise<Article[]> {
    const base = await this.getBaseUrl();
    const { data } = await axios.get(`${base}/api/news/articles`);
    return data.articles || data;
  }

  async getArticle(id: string): Promise<Article> {
    const base = await this.getBaseUrl();
    const { data } = await axios.get(`${base}/api/news/articles/${id}`);
    return data;
  }

  // Branding
  async getBranding(clientId: string): Promise<Branding> {
    const base = await this.getBaseUrl();
    const { data } = await axios.get(`${base}/api/branding/${clientId}`);
    return data;
  }

  async getBrandingByDomain(domain: string): Promise<Branding> {
    const base = await this.getBaseUrl();
    const { data } = await axios.get(`${base}/api/branding/domain/${domain}`);
    return data;
  }

  // Billing
  async getPlan(clientId: string): Promise<ClientPlan> {
    const base = await this.getBaseUrl();
    const { data } = await axios.get(`${base}/api/billing/clients/${clientId}/summary`);
    return data;
  }

  async getUsage(clientId: string): Promise<Record<string, { used: number; limit: number; percentage: number }>> {
    const base = await this.getBaseUrl();
    const { data } = await axios.get(`${base}/api/billing/clients/${clientId}/usage`);
    return data.usage || data;
  }

  // Generic request
  async request(method: string, path: string, body?: any): Promise<any> {
    const base = await this.getBaseUrl();
    const url = `${base}${path}`;
    if (method === 'GET') {
      const { data } = await this.client.get(url);
      return data;
    }
    const { data } = await this.client[method.toLowerCase()](url, body);
    return data;
  }
}

export const api = new ApiService();
