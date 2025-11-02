import React, { useState, useMemo } from 'react';
import { useQueryStore } from '../store/useQueryStore';
import { SingleSelectDropdown } from './ui/SingleSelectDropdown';
import './AddFilterModal.css';

const STRING_OPERATORS = [
  { value: 'eq', label: 'Igual a' },
  { value: 'neq', label: 'Diferente de' },
  { value: 'contains', label: 'Contém' },
  { value: 'is_null', label: 'É nulo' },
  { value: 'is_not_null', label: 'Não é nulo' },
];

const NUMERIC_OPERATORS = [
  { value: 'eq', label: 'Igual a' },
  { value: 'neq', label: 'Diferente de' },
  { value: 'gt', label: 'Maior que' },
  { value: 'gte', label: 'Maior ou igual a' },
  { value: 'lt', label: 'Menor que' },
  { value: 'lte', label: 'Menor ou igual a' },
];

export function AddFilterModal() {
  const { definitions, addFilter, closeFilterModal } = useQueryStore();

  const [field, setField] = useState('');
  const [operator, setOperator] = useState('');
  const [value, setValue] = useState('');

  const fieldOptions = useMemo(() => {
    const metrics = Object.entries(definitions.metrics).map(([key, val]) => ({
      value: key,
      label: val.label,
      type: val.type || 'number'
    }));
    const dimensions = Object.entries(definitions.dimensions).map(([key, val]) => ({
      value: key,
      label: val.label,
      type: val.type || 'string'
    }));
    return [...metrics, ...dimensions];
  }, [definitions]);

  const selectedFieldType = useMemo(() => {
    const selected = fieldOptions.find(f => f.value === field);
    if (!selected) return 'string';
    if (selected.type === 'currency' || selected.type === 'number') return 'number';
    if (selected.type === 'date' || selected.type === 'datetime') return 'date';
    return 'string';
  }, [field, fieldOptions]);

  const operatorOptions = selectedFieldType === 'number' ? NUMERIC_OPERATORS : STRING_OPERATORS;
  
  const inputType = selectedFieldType === 'number' ? 'number' : 'text';
  
  const isValueHidden = operator === 'is_null' || operator === 'is_not_null';

  const handleFieldChange = (newField: string) => {
    setField(newField);
    setOperator('');
  };
  
  const handleSave = () => {
    if (!field || !operator) return;
    
    const filterValue = isValueHidden ? null : value;
    
    addFilter({ field, operator, value: String(filterValue) });
    closeFilterModal();
  };

  return (
    <div className="modal-backdrop" onClick={closeFilterModal}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Adicionar Filtro</h3>
        </div>
        <div className="modal-body">
          <div className="query-section">
            <label className="query-label">Campo</label>
            <SingleSelectDropdown
              placeholder="Selecione um campo..."
              options={fieldOptions}
              value={field}
              onChange={handleFieldChange}
            />
          </div>

          {field && (
            <div className="query-section">
              <label className="query-label">Condição</label>
              <SingleSelectDropdown
                placeholder="Selecione um operador..."
                options={operatorOptions}
                value={operator}
                onChange={setOperator}
              />
            </div>
          )}

          {field && operator && !isValueHidden && (
            <div className="query-section">
              <label className="query-label">Valor</label>
              <input
                type={inputType}
                className="query-input"
                value={value}
                onChange={(e) => setValue(e.target.value)}
              />
            </div>
          )}
        </div>
        <div className="modal-footer">
          <button className="button-secondary" onClick={closeFilterModal}>Cancelar</button>
          <button className="button-primary" onClick={handleSave}>Salvar Filtro</button>
        </div>
      </div>
    </div>
  );
}

