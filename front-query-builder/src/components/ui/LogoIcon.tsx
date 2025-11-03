export function LogoIcon() {
  return (
    <svg
      width="40"
      height="40"
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
           {' '}
      <defs>
               {' '}
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#667EEA" />
                    <stop offset="100%" stopColor="#764BA2" />       {' '}
        </linearGradient>
             {' '}
      </defs>
            <rect width="40" height="40" rx="8" fill="url(#logoGradient)" />
            <path d="M10 28V12H14V28H10Z" fill="white" />
            <path d="M18 28V18H22V28H18Z" fill="white" />
            <path d="M26 28V22H30V28H26Z" fill="white" />   {' '}
    </svg>
  );
}
