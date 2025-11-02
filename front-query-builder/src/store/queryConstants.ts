import type { JsonQuery, Definitions } from './useQueryStore';

export const DEFAULT_QUERY: JsonQuery = {
 metrics: ['total_vendas'],
 dimensions: [],
 period: 'last_6_months',
 filters: [],
 order_by: { field: 'total_vendas', direction: 'desc' },
 limit: 10,
};

export const EMPTY_DEFINITIONS: Definitions = {
 metrics: {},
 dimensions: {},
};