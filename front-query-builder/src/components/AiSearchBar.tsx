import React from 'react';
import { FaSearch } from 'react-icons/fa';
import { BsStars } from 'react-icons/bs';

type AiSearchBarProps = {
  prompt: string;
  onPromptChange: (value: string) => void;
  onSearch: () => void;
  isLoading: boolean;
};

export const AiSearchBar = React.memo(
  ({ prompt, onPromptChange, onSearch, isLoading }: AiSearchBarProps) => {
    return (
      <div className="search-bar-container">
        <FaSearch className="search-icon" />
        <input
          type="text"
          placeholder="Pergunte qualquer coisa sobre seus dados..."
          className="search-input"
          value={prompt}
          onChange={(e) => onPromptChange(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onSearch()}
          disabled={isLoading}
        />
        <span className="keyboard-shortcut">⌘K</span>
        <button
          className="ai-search-button"
          onClick={onSearch}
          disabled={isLoading}
        >
          <BsStars />
          Buscar com IA
        </button>
      </div>
    );
  }
);