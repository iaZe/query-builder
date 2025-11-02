import { useEffect, useMemo, useCallback } from 'react';
import { useQueryStore } from '../store/useQueryStore';
import { MultiSelectDropdown } from './ui/MultiSelectDropdown';
import { SingleSelectDropdown } from './ui/SingleSelectDropdown';
import { FaChartBar, FaTags, FaCalendarAlt, FaFilter, FaPlus } from 'react-icons/fa';
import { AddFilterModal } from './AddFilterModal';
import { FilterList } from './FilterList';
import {
  PERIOD_OPTIONS,
  ORDER_BY_OPTIONS,
} from '../config/queryConstants';
import { mapDefinitionsToOptions } from '../utils/queryBuilderUtils';

export function QueryBuilder() {
  const {
    query,
    definitions,
    isDefinitionsLoading,
    fetchDefinitions,
    setMetrics,
    setDimensions,
    setPeriod,
    setOrderBy,
    setLimit,
    fetchVisualization,
    isLoading,
    isFilterModalOpen,
    openFilterModal,
    removeFilter,
  } = useQueryStore();

  useEffect(() => {
    fetchDefinitions();
  }, [fetchDefinitions]);

  const metricOptions = useMemo(
    () => mapDefinitionsToOptions(definitions.metrics),
    [definitions.metrics]
  );
  
  const dimensionOptions = useMemo(
    () => mapDefinitionsToOptions(definitions.dimensions),
    [definitions.dimensions]
  );

  const getFilterLabel = useCallback(
    (fieldKey: string) => {
      return (
        definitions.metrics[fieldKey]?.label ||
        definitions.dimensions[fieldKey]?.label ||
        fieldKey
      );
    },
    [definitions.metrics, definitions.dimensions]
  );

  if (isDefinitionsLoading) {
    return (
      <div className="query-builder-sidebar">
        <p>Carregando definições...</p>
      </div>
    );
  }

  return (
    <>
      <div className="query-builder-sidebar">
        <div className="query-section">
          <label className="query-label">
            <span className="icon-wrapper icon-metrics">
              <FaChartBar />
            </span>
            Métricas
          </label>
          <MultiSelectDropdown
            placeholder="Selecione as métricas"
            options={metricOptions}
            selectedValues={query.metrics}
            onChange={setMetrics}
          />
        </div>

        <div className="query-section">
          <label className="query-label">
            <span className="icon-wrapper icon-dimensions">
              <FaTags />
            </span>
            Dimensões
          </label>
          <MultiSelectDropdown
            placeholder="Selecione as dimensões"
            options={dimensionOptions}
            selectedValues={query.dimensions}
            onChange={setDimensions}
          />
        </div>

        <div className="query-section">
          <label className="query-label">
            <span className="icon-wrapper icon-period">
              <FaCalendarAlt />
            </span>
            Período
          </label>
          <SingleSelectDropdown
            placeholder="Selecione o período"
            options={PERIOD_OPTIONS}
            value={query.period}
            onChange={setPeriod}
          />
        </div>

        <div className="query-section-row">
          <div className="query-section">
            <label className="query-label">Ordenar</label>
            <SingleSelectDropdown
              placeholder="Ordem"
              options={ORDER_BY_OPTIONS}
              value={query.order_by.direction}
              onChange={(dir) =>
                setOrderBy({
                  ...query.order_by,
                  direction: dir as 'asc' | 'desc',
                })
              }
            />
          </div>

          <div className="query-section">
            <label className="query-label">Limite</label>
            <input
              type="number"
              className="query-input"
              value={query.limit}
              min={1}
              max={100000}
              onChange={(e) => setLimit(Number(e.target.value))}
            />
          </div>
        </div>

        <div className="query-section">
          <div className="query-label-filter">
            <label className="query-label">
              <span className="icon-wrapper icon-filters">
                <FaFilter />
              </span>
              Filtros
            </label>
            <button className="add-filter-button" onClick={openFilterModal}>
              <FaPlus /> Adicionar
            </button>
          </div>

          <div className="filters-list-container">
            <FilterList
              filters={query.filters}
              getFilterLabel={getFilterLabel}
              onRemoveFilter={removeFilter}
            />
          </div>
        </div>

        <button
          className="generate-button"
          onClick={fetchVisualization}
          disabled={isLoading || query.metrics.length === 0}
        >
          {isLoading ? 'Gerando...' : 'Gerar Visualização'}
        </button>
      </div>

      {isFilterModalOpen && <AddFilterModal />}
    </>
  );
}