import React from 'react';
import { LogoIcon } from './ui/LogoIcon';

const HeaderBrandInternal = () => {
  return (
    <div className="header-left">
      <LogoIcon />
      <div className="header-title">
        <h1>Analytics Platform</h1>
        <span>Construa queries e visualize insights em tempo real</span>
      </div>
    </div>
  );
};

export const HeaderBrand = React.memo(HeaderBrandInternal);