import React, { useState, useMemo, useCallback } from 'react';
import { useClickOutside } from '../../hooks/useClickOutside';
import { FaChevronDown } from 'react-icons/fa';
import './ui.css';

interface Option {
  value: string;
  label: string;
}

interface SingleSelectDropdownProps {
  options: Option[];
  value: string;
  onChange: (selected: string) => void;
  placeholder: string;
}

export function SingleSelectDropdown({
  options,
  value,
  onChange,
  placeholder,
}: SingleSelectDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);

  const closeDropdown = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleDropdown = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const dropdownRef = useClickOutside<HTMLDivElement>(closeDropdown);

  const selectOption = useCallback(
    (selectedValue: string) => {
      onChange(selectedValue);
      closeDropdown();
    },
    [onChange, closeDropdown],
  );

  const displayLabel = useMemo(
    () => options.find((opt) => opt.value === value)?.label || placeholder,
    [options, value, placeholder],
  );

  const handleOptionKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLLIElement>, optionValue: string) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        selectOption(optionValue);
      }
    },
    [selectOption],
  );

  return (
    <div className="dropdown-container" ref={dropdownRef}>
           {' '}
      <button
        className="dropdown-button"
        onClick={toggleDropdown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
                <span className="dropdown-button-label">{displayLabel}</span>
               {' '}
        <FaChevronDown className={`dropdown-chevron ${isOpen ? 'open' : ''}`} />
             {' '}
      </button>
           {' '}
      {isOpen && (
        <div className="dropdown-panel">
                   {' '}
          <ul role="listbox">
                       {' '}
            {options.map((option) => {
              const isSelected = option.value === value;
              return (
                <li
                  key={option.value}
                  role="option"
                  aria-selected={isSelected}
                  tabIndex={0}
                  onClick={() => selectOption(option.value)}
                  onKeyDown={(e) => handleOptionKeyDown(e, option.value)}
                  className={isSelected ? 'selected' : ''}
                >
                                    <span>{option.label}</span>             
                   {' '}
                </li>
              );
            })}
                     {' '}
          </ul>
                 {' '}
        </div>
      )}
         {' '}
    </div>
  );
}
