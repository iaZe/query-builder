import { create } from 'zustand';
import * as apiService from '../services/apiService';
import { getErrorMessage } from '../utils/errorUtils';
import { DEFAULT_QUERY, EMPTY_DEFINITIONS } from './queryConstants';

interface DefinitionItem {
  sql: string;
  label: string;
  type: string | null;
  joins_needed: string[];
}

export interface Definitions {
  metrics: Record<string, DefinitionItem>;
  dimensions: Record<string, DefinitionItem>;
}

export interface JsonQuery {
  metrics: string[];
  dimensions: string[];
  period: string;
  customStartDate?: string;
  customEndDate?: string;
  filters: Array<{ field: string; operator: string; value: string | null }>;
  order_by: { field: string; direction: 'asc' | 'desc' };
  limit: number;
}

interface ApiDataRow {
  metrics: Record<string, any>;
  dimensions: Record<string, any>;
}

export interface ApiResponse {
  query_sql: string;
  data: ApiDataRow[];
  execution_time_ms: number;
  chart_suggestion: string;
  insights: string[] | null;
}

interface QueryState {
  query: JsonQuery;

  isFilterModalOpen: boolean;
  aiPrompt: string;

  definitions: Definitions;
  isDefinitionsLoading: boolean;
  definitionsError: string | null;

  response: ApiResponse | null;
  isLoading: boolean;
  error: string | null;

  setMetrics: (metrics: string[]) => void;
  setDimensions: (dimensions: string[]) => void;
  setPeriod: (period: string) => void;
  setCustomDateRange: (dates: { startDate: string; endDate: string }) => void;
  setOrderBy: (orderBy: JsonQuery['order_by']) => void;
  setLimit: (limit: number) => void;
  addFilter: (filter: JsonQuery['filters'][0]) => void;
  removeFilter: (index: number) => void;
  openFilterModal: () => void;
  closeFilterModal: () => void;
  setAiPrompt: (prompt: string) => void;

  fetchDefinitions: () => Promise<void>;
  fetchVisualization: () => Promise<void>;
  fetchAiQuery: (promptOverride?: string) => Promise<void>;
}

export const useQueryStore = create<QueryState>((set, get) => ({
  query: DEFAULT_QUERY,
  isFilterModalOpen: false,
  aiPrompt: '',
  definitions: EMPTY_DEFINITIONS,
  isDefinitionsLoading: false,
  definitionsError: null,
  response: null,
  isLoading: false,
  error: null,

  setMetrics: (metrics) =>
    set((state) => {
      const newOrderByField = metrics.includes(state.query.order_by.field)
        ? state.query.order_by.field
        : metrics[0] || '';
      return {
        query: {
          ...state.query,
          metrics,
          order_by: { ...state.query.order_by, field: newOrderByField },
        },
      };
    }),

  setDimensions: (dimensions) =>
    set((state) => ({
      query: { ...state.query, dimensions },
    })),

  setPeriod: (period) =>
    set((state) => ({
      query: { ...state.query, period },
    })),

  setCustomDateRange: (dates) =>
    set((state) => ({
      query: {
        ...state.query,
        customStartDate: dates.startDate,
        customEndDate: dates.endDate,
      },
    })),

  setOrderBy: (orderBy) =>
    set((state) => ({
      query: { ...state.query, order_by: orderBy },
    })),

  setLimit: (limit) =>
    set((state) => ({
      query: { ...state.query, limit: Math.min(Math.max(limit, 1), 100000) },
    })),

  addFilter: (filter) =>
    set((state) => ({
      query: { ...state.query, filters: [...state.query.filters, filter] },
    })),

  removeFilter: (index) =>
    set((state) => ({
      query: {
        ...state.query,
        filters: state.query.filters.filter((_, i) => i !== index),
      },
    })),

  openFilterModal: () => set({ isFilterModalOpen: true }),
  closeFilterModal: () => set({ isFilterModalOpen: false }),

  setAiPrompt: (prompt) => set({ aiPrompt: prompt }),

  fetchDefinitions: async () => {
    set({ isDefinitionsLoading: true, definitionsError: null });
    try {
      const data = await apiService.fetchDefinitions();
      set({ definitions: data, isDefinitionsLoading: false });
    } catch (err) {
      set({
        isDefinitionsLoading: false,
        definitionsError: getErrorMessage(err),
      });
    }
  },

  fetchVisualization: async () => {
    set({ isLoading: true, error: null, response: null });
    try {
      const currentQuery = get().query;
      const data = await apiService.fetchVisualization(currentQuery);
      set({ isLoading: false, response: data });
    } catch (err) {
      set({ isLoading: false, error: getErrorMessage(err) });
    }
  },

  fetchAiQuery: async (promptOverride?: string) => {
    const prompt = promptOverride ?? get().aiPrompt;
    if (!prompt) return;

    if (promptOverride) {
      set({ aiPrompt: promptOverride });
    }

    set({ isLoading: true, error: null, response: null });
    try {
      const data = await apiService.fetchAiQuery(prompt);
      set({ isLoading: false, response: data });
    } catch (err) {
      set({ isLoading: false, error: getErrorMessage(err) });
    }
  },
}));
