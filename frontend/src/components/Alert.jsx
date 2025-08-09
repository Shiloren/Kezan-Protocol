import React from 'react';

const Alert = ({ children, type = 'warning' }) => {
  const baseStyles = 'p-3 border-l-4 text-warm-white';
  const types = {
    warning: 'bg-black-mineral border-golden-glow',
    error: 'bg-black-mineral border-muted-red',
    success: 'bg-black-mineral border-goblin-green',
  };

  return (
    <div className={`${baseStyles} ${types[type]}`}>
      {children}
    </div>
  );
};

export default Alert;
