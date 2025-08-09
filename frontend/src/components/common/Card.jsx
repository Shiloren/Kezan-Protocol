import React from 'react';
import PropTypes from 'prop-types';

const Card = ({
  children,
  variant = 'default',
  className = '',
  title,
  titleId,
  ...props
}) => {
  const baseClasses = 'rounded-lg shadow-sm overflow-hidden';
  
  const variants = {
    default: 'bg-graphite-soft border border-steel-gray/20',
    elevated: 'bg-black-mineral shadow-lg border border-steel-gray/30',
    outlined: 'bg-transparent border border-steel-gray/40',
  };

  const generatedTitleId = titleId || title?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div
      className={`${baseClasses} ${variants[variant]} ${className}`}
      role="region"
      aria-labelledby={title ? generatedTitleId : undefined}
      {...props}
    >
      {title && (
        <h2
          id={generatedTitleId}
          className="px-4 py-3 border-b border-steel-gray/20 font-medium text-warm-white"
        >
          {title}
        </h2>
      )}
      <div className="p-4">
        {children}
      </div>
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['default', 'elevated', 'outlined']),
  className: PropTypes.string,
  title: PropTypes.string,
  titleId: PropTypes.string,
};

export default Card;
