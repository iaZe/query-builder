import { useCallback } from 'react';
import { useQueryStore } from '../store/useQueryStore';
import { SUGGESTIONS } from '../config/queryConstants';
import { HeaderBrand } from './HeaderBrand';
import { AiSearchBar } from './AiSearchBar';
import { SuggestionChips } from './SuggestionChips';
import './Header.css';

export function Header() {
  const { aiPrompt, setAiPrompt, fetchAiQuery, isLoading } = useQueryStore();

  const handleSearch = useCallback(() => {
    fetchAiQuery();
  }, [fetchAiQuery]);

  const handleSuggestionClick = useCallback(
    (prompt: string) => {
      fetchAiQuery(prompt);
    },
    [fetchAiQuery],
  );

  return (
    <header className="app-header">
           {' '}
      <div className="header-top-row">
                <HeaderBrand />     {' '}
      </div>
           {' '}
      <div className="header-search-row">
               {' '}
        <AiSearchBar
          prompt={aiPrompt}
          onPromptChange={setAiPrompt}
          onSearch={handleSearch}
          isLoading={isLoading}
        />
             {' '}
      </div>
           {' '}
      <div className="header-chips-row">
               {' '}
        <SuggestionChips
          suggestions={SUGGESTIONS}
          onSuggestionClick={handleSuggestionClick}
          isLoading={isLoading}
        />
             {' '}
      </div>
         {' '}
    </header>
  );
}
