import React from 'react';
import { useQueryStore } from '../store/useQueryStore';

export function CustomDateRangePicker() {
  const { query, setCustomDateRange } = useQueryStore();

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCustomDateRange({
      startDate: name === 'start_date' ? value : query.customStartDate || '',
      endDate: name === 'end_date' ? value : query.customEndDate || '',
    });
  };

  return (
    <div className="query-section-row">
           {' '}
      <div className="query-section">
                <label className="query-label">Data Início</label>
               {' '}
        <input
          type="date"
          name="start_date"
          className="query-input"
          value={query.customStartDate || ''}
          onChange={handleDateChange}
        />
             {' '}
      </div>
           {' '}
      <div className="query-section">
                <label className="query-label">Data Fim</label>
               {' '}
        <input
          type="date"
          name="end_date"
          className="query-input"
          value={query.customEndDate || ''}
          onChange={handleDateChange}
        />
             {' '}
      </div>
         {' '}
    </div>
  );
}
