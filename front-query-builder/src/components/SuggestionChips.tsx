import React from 'react';

type SuggestionChipsProps = {
  suggestions: string[];
  onSuggestionClick: (prompt: string) => void;
  isLoading: boolean;
};

export const SuggestionChips = React.memo(
  ({ suggestions, onSuggestionClick, isLoading }: SuggestionChipsProps) => {
    return (
      <div className="suggestion-chips">
               {' '}
        {suggestions.map((text) => (
          <button
            key={text}
            className="chip"
            onClick={() => onSuggestionClick(text)}
            disabled={isLoading}
          >
                        {text}         {' '}
          </button>
        ))}
             {' '}
      </div>
    );
  },
);
