import React, { useState, useMemo, useCallback } from 'react';
import { useClickOutside } from '../../hooks/useClickOutside';
import { FaChevronDown, FaCheckSquare, FaRegSquare } from 'react-icons/fa';
import './ui.css';

interface Option {
  value: string;
  label: string;
}

interface MultiSelectDropdownProps {
  options: Option[];
  selectedValues: string[];
  onChange: (selected: string[]) => void;
  placeholder: string;
}

export function MultiSelectDropdown({
  options,
  selectedValues,
  onChange,
  placeholder,
}: MultiSelectDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);

  const closeDropdown = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleDropdown = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const dropdownRef = useClickOutside<HTMLDivElement>(closeDropdown);

  const toggleOption = useCallback(
    (value: string) => {
      const isSelected = selectedValues.includes(value);
      if (isSelected) {
        onChange(selectedValues.filter((v) => v !== value));
      } else {
        onChange([...selectedValues, value]);
      }
    },
    [selectedValues, onChange]
  );

  const displayLabel = useMemo(() => {
    if (selectedValues.length === 0) {
      return placeholder;
    }
    return selectedValues
      .map((val) => options.find((opt) => opt.value === val)?.label)
      .filter(Boolean)
      .join(', ');
  }, [selectedValues, options, placeholder]);

  const handleOptionKeyDown = (
    e: React.KeyboardEvent<HTMLLIElement>,
    value: string
  ) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleOption(value);
    }
  };

  return (
    <div className="dropdown-container" ref={dropdownRef}>
      <button
        className="dropdown-button"
        onClick={toggleDropdown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className="dropdown-button-label">{displayLabel}</span>
        <FaChevronDown className={`dropdown-chevron ${isOpen ? 'open' : ''}`} />
      </button>

      {isOpen && (
        <div className="dropdown-panel">
          <ul role="listbox">
            {options.map((option) => {
              const isSelected = selectedValues.includes(option.value);
              return (
                <li
                  key={option.value}
                  role="option"
                  aria-selected={isSelected}
                  tabIndex={0}
                  onClick={() => toggleOption(option.value)}
                  onKeyDown={(e) => handleOptionKeyDown(e, option.value)}
                >
                  {isSelected ? (
                    <FaCheckSquare className="dropdown-checkbox" />
                  ) : (
                    <FaRegSquare className="dropdown-checkbox" />
                  )}
                  <span>{option.label}</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}