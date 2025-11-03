import type { JsonQuery } from '../store/useQueryStore';
import { FilterPill } from './ui/FilterPill';

type FilterListProps = {
  filters: JsonQuery['filters'];
  getFilterLabel: (fieldKey: string) => string;
  onRemoveFilter: (index: number) => void;
};

export const FilterList = ({
  filters,
  getFilterLabel,
  onRemoveFilter,
}: FilterListProps) => {
  if (filters.length === 0) {
    return <p>Nenhum filtro aplicado</p>;
  }

  return (
    <div className="filter-pills-wrapper">
      {filters.map((filter, index) => (
        <FilterPill
          key={index}
          filter={filter}
          label={getFilterLabel(filter.field)}
          onRemove={() => onRemoveFilter(index)}
        />
      ))}
    </div>
  );
};