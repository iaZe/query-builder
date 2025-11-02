import axios from 'axios';
import type { Definitions, JsonQuery, ApiResponse } from '../store/useQueryStore';
import { getErrorMessage } from '../utils/errorUtils';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const apiClient = axios.create({
 baseURL: API_BASE_URL,
});

export const fetchDefinitions = async (): Promise<Definitions> => {
 try {
  const response = await apiClient.get<Definitions>('/definitions');
  return response.data;
 } catch (error) {
  console.error("Erro ao buscar definições:", error);
  throw new Error(getErrorMessage(error));
 }
};

export const fetchVisualization = async (query: JsonQuery): Promise<ApiResponse> => {
 const apiQueryPayload = {
  metrics: query.metrics,
  dimensions: query.dimensions,
  filters: query.filters,
  order_by: [query.order_by], 
  limit: query.limit
 };

 try {
  const response = await apiClient.post<ApiResponse>('/query', apiQueryPayload);
  return response.data;
 } catch (error) {
  console.error("Erro ao gerar visualização:", error);
  throw new Error(getErrorMessage(error));
 }
};

export const fetchAiQuery = async (prompt: string): Promise<ApiResponse> => {
 if (!prompt) {
  throw new Error("O prompt da IA não pode estar vazio.");
 }
 
 try {
  const response = await apiClient.post<ApiResponse>('/query-from-text', { prompt });
  return response.data;
 } catch (error) {
  console.error("Erro ao buscar query da IA:", error);
  throw new Error(getErrorMessage(error));
 }
};