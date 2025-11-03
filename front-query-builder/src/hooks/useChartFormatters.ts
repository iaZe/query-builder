import { useMemo } from 'react';
import { useQueryStore } from '../store/useQueryStore';
import * as Format from '../utils/formatters';

type DefinitionType = 'metric' | 'dimension';

export function useChartFormatters(
  dimensionKeys: string[],
  metricKeys: string[],
) {
  const { definitions } = useQueryStore.getState();

  const getDefinition = (key: string) => {
    if (definitions.metrics[key]) {
      return {
        info: definitions.metrics[key],
        type: 'metric' as DefinitionType,
      };
    }
    if (definitions.dimensions[key]) {
      return {
        info: definitions.dimensions[key],
        type: 'dimension' as DefinitionType,
      };
    }
    if (metricKeys.includes(key)) {
      return { info: null, type: 'metric' as DefinitionType };
    }
    if (dimensionKeys.includes(key)) {
      return { info: null, type: 'dimension' as DefinitionType };
    }
    return { info: null, type: null };
  };

  const getFormattedValue = (key: string, value: any): string => {
    const { info, type } = getDefinition(key);
    const keyType = info?.type;

    if (
      typeof value === 'string' &&
      value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)
    ) {
      if (value.endsWith('T00:00:00')) {
        return Format.formatDate(value);
      }
      return Format.formatDateTime(value);
    }

    if (type === 'dimension') {
      if (key === 'dia_da_semana') return Format.formatWeekday(value);
      if (keyType === 'datetime' || keyType === 'timestamp')
        return Format.formatDateTime(value);
      if (keyType === 'date') return Format.formatDate(value);
      if (keyType === 'time' || key === 'hora_venda')
        return Format.formatTime(value);
    }

    if (type === 'metric') {
      const isCurrency =
        keyType === 'currency' ||
        key.includes('vendas') ||
        key.includes('receita') ||
        key.includes('bruto') ||
        key.includes('ticket');
      if (isCurrency) return Format.formatCurrency(value);

      const isTime =
        keyType === 'time' || key.includes('tempo') || key.includes('duration');
      if (isTime) return Format.formatTimeMinutes(value);
    }

    return Format.formatGenericNumber(value);
  };

  const formatters = useMemo(() => {
    const primaryDimension = dimensionKeys[0];
    const primaryMetric = metricKeys[0];

    return {
      xAxis: (value: any) => getFormattedValue(primaryDimension, value),
      yAxis: (value: any) => {
        const { info } = getDefinition(primaryMetric);
        const isTime =
          info?.type === 'time' ||
          primaryMetric.includes('tempo') ||
          primaryMetric.includes('duration');

        if (isTime) {
          const num = parseFloat(String(value));
          if (isNaN(num)) return value;
          return `${num.toLocaleString('pt-BR', {
            maximumFractionDigits: 0,
          })} min`;
        }
        return Format.formatAxisNumber(value);
      },
      tooltip: (value: any, name: string) => {
        return [getFormattedValue(name, value), name.replace(/_/g, ' ')];
      },
      table: (value: any, key: string) => getFormattedValue(key, value),
    };
  }, [definitions, dimensionKeys, metricKeys]);

  return formatters;
}
