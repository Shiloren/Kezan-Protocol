import React from 'react';

const Button = ({ children, variant = 'primary', ...props }) => {
  const baseStyles = 'px-4 py-2 rounded-lg font-semibold';
  const variants = {
    primary: 'bg-goblin-green hover:bg-deep-emerald text-warm-white',
    secondary: 'bg-deep-emerald text-warm-white hover:bg-goblin-green',
    destructive: 'bg-muted-red text-warm-white hover:bg-black-mineral',
  };

  return (
    <button className={`${baseStyles} ${variants[variant]}`} {...props}>
      {children}
    </button>
  );
};

export default Button;
