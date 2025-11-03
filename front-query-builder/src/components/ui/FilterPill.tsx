import React from 'react';
import { FaTrash } from 'react-icons/fa';
import './FilterPill.css';
import type { JsonQuery } from '../../store/useQueryStore';

type FilterPillProps = {
  filter: JsonQuery['filters'][0];
  label: string;
  onRemove: () => void;
};

export const FilterPill = React.memo(
  ({ filter, label, onRemove }: FilterPillProps) => {
    return (
      <div className="filter-pill">
        <span className="filter-pill-label">{label}</span>
        <span className="filter-pill-operator">{filter.operator}</span>
        <span className="filter-pill-value">{filter.value}</span>
        <button className="filter-pill-remove" onClick={onRemove}>
          <FaTrash />
        </button>
      </div>
    );
  }
);