import { DOW_MAP } from '../config/chartConstants';

const parseUtcDate = (value: any): Date => {
  if (
    typeof value === 'string' &&
    value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/)
  ) {
    return new Date(value + 'Z');
  }
  return new Date(value);
};

export const formatCurrency = (value: any): string => {
  const number = parseFloat(value);
  if (isNaN(number)) return String(value);
  return number.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
};

export const formatWeekday = (value: string | number): string =>
  DOW_MAP[String(value)] || String(value);

export const formatTimeMinutes = (value: any): string => {
  const minutes = parseFloat(value);
  if (isNaN(minutes)) return String(value);

  const totalSeconds = Math.floor(minutes * 60);
  const min = Math.floor(totalSeconds / 60);
  const sec = totalSeconds % 60;

  return `${min} min ${sec} s`;
};

export const formatAxisNumber = (value: any): string => {
  if (typeof value === 'number' || typeof value === 'string') {
    const num = parseFloat(String(value));
    if (isNaN(num)) return String(value);
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(0)}K`;
    return num.toLocaleString('pt-BR');
  }
  return String(value);
};

export const formatDate = (value: any): string => {
  try {
    const date = parseUtcDate(value);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      timeZone: 'UTC',
    });
  } catch (e) {
    return String(value);
  }
};

export const formatDateTime = (value: any): string => {
  try {
    const date = parseUtcDate(value);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'UTC',
    });
  } catch (e) {
    return String(value);
  }
};

export const formatTime = (value: any): string => {
  if (typeof value === 'number') return `${String(value).padStart(2, '0')}:00`;
  try {
    const date = parseUtcDate(value);
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'UTC',
    });
  } catch (e) {
    return String(value);
  }
};

export const formatGenericNumber = (value: any): string => {
  const number = parseFloat(value);
  if (!isNaN(number)) {
    return number.toLocaleString('pt-BR', { maximumFractionDigits: 2 });
  }
  return String(value);
};