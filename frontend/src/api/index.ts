import apiClient from './client';
import {
  User,
  Plan,
  Phase,
  WorkoutLog,
  CreateLogInput,
  UpdateLogInput,
  DashboardData,
  RoutineTemplate,
} from '../types';

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post<User>('/auth/login', { email, password });
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },

  me: async () => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },
};

// Plans API
export const plansApi = {
  getPlans: async () => {
    const response = await apiClient.get<Plan[]>('/plans');
    return response.data;
  },

  getPlan: async (id: string) => {
    const response = await apiClient.get<Plan>(`/plans/${id}`);
    return response.data;
  },

  assignPlan: async (planId: string) => {
    const response = await apiClient.post('/plans/assign', { planId });
    return response.data;
  },

  getPhase: async (id: string) => {
    const response = await apiClient.get<{ phase: Phase; logs: WorkoutLog[] }>(
      `/plans/phases/${id}`
    );
    return response.data;
  },
};

// Logs API
export const logsApi = {
  getLogs: async (params?: {
    startDate?: string;
    endDate?: string;
    phaseId?: string;
    status?: string;
    search?: string;
    page?: number;
    limit?: number;
  }) => {
    const response = await apiClient.get<{
      logs: WorkoutLog[];
      total: number;
      page: number;
      totalPages: number;
    }>('/logs', { params });
    return response.data;
  },

  getLog: async (id: string) => {
    const response = await apiClient.get<WorkoutLog>(`/logs/${id}`);
    return response.data;
  },

  createLog: async (data: CreateLogInput) => {
    const response = await apiClient.post<WorkoutLog>('/logs', data);
    return response.data;
  },

  updateLog: async (id: string, data: UpdateLogInput) => {
    const response = await apiClient.patch<WorkoutLog>(`/logs/${id}`, data);
    return response.data;
  },

  getTodayWorkout: async () => {
    const response = await apiClient.get<{
      log: WorkoutLog | null;
      dayTemplate: any;
      scheduledDate: string;
    }>('/logs/today');
    return response.data;
  },

  exportLogs: async (params?: { startDate?: string; endDate?: string }) => {
    const response = await apiClient.get('/logs/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

// Dashboard API
export const dashboardApi = {
  getDashboard: async () => {
    const response = await apiClient.get<DashboardData>('/dashboard');
    return response.data;
  },
};

// Routines API
export const routinesApi = {
  getRoutines: async () => {
    const response = await apiClient.get<RoutineTemplate[]>('/routines');
    return response.data;
  },

  getRoutine: async (id: string) => {
    const response = await apiClient.get<RoutineTemplate>(`/routines/${id}`);
    return response.data;
  },

  createRoutine: async (data: { name: string; description?: string }) => {
    const response = await apiClient.post<RoutineTemplate>('/routines', data);
    return response.data;
  },

  updateRoutine: async (id: string, data: { name?: string; description?: string }) => {
    const response = await apiClient.patch<RoutineTemplate>(`/routines/${id}`, data);
    return response.data;
  },

  deleteRoutine: async (id: string) => {
    const response = await apiClient.delete(`/routines/${id}`);
    return response.data;
  },
};

// Users API
export const usersApi = {
  getUser: async (id: string) => {
    const response = await apiClient.get<User>(`/users/${id}`);
    return response.data;
  },

  updateUser: async (id: string, data: { name?: string }) => {
    const response = await apiClient.patch<User>(`/users/${id}`, data);
    return response.data;
  },
};
