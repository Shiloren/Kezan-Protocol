import React from 'react';
import PropTypes from 'prop-types';

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  type = 'button',
  className = '',
  onClick,
  ariaLabel,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors';
  
  const variants = {
    primary: 'bg-goblin-green hover:bg-deep-emerald text-warm-white focus:ring-deep-emerald',
    secondary: 'bg-steel-gray hover:bg-graphite-soft text-warm-white focus:ring-steel-gray',
    danger: 'bg-muted-red hover:bg-red-700 text-warm-white focus:ring-muted-red',
    ghost: 'bg-transparent hover:bg-light-gray/10 text-steel-gray focus:ring-steel-gray',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  return (
    <button
      type={type}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${disabledClasses} ${className}`}
      disabled={disabled}
      onClick={onClick}
      aria-label={ariaLabel || undefined}
      {...props}
    >
      {children}
    </button>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger', 'ghost']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  disabled: PropTypes.bool,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  className: PropTypes.string,
  onClick: PropTypes.func,
  ariaLabel: PropTypes.string,
};

export default Button;
