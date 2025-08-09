import React from 'react';
import PropTypes from 'prop-types';

const Alert = ({
  children,
  type = 'info',
  title,
  onClose,
  className = '',
  ...props
}) => {
  const baseClasses = 'rounded-md p-4 border';

  const types = {
    info: 'bg-spectral-cyan/10 border-spectral-cyan text-spectral-cyan',
    success: 'bg-goblin-green/10 border-goblin-green text-goblin-green',
    warning: 'bg-golden-glow/10 border-golden-glow text-golden-glow',
    error: 'bg-muted-red/10 border-muted-red text-muted-red',
  };

  return (
    <div
      className={`${baseClasses} ${types[type]} ${className}`}
      role="alert"
      aria-live={type === 'error' ? 'assertive' : 'polite'}
      {...props}
    >
      <div className="flex items-start">
        <div className="flex-1">
          {title && (
            <h3 className="font-medium mb-1">
              {title}
            </h3>
          )}
          <div className="text-sm">
            {children}
          </div>
        </div>
        {onClose && (
          <button
            type="button"
            className="ml-3 -mt-1 -mr-1 p-1 hover:opacity-80 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current rounded"
            onClick={onClose}
            aria-label="Cerrar alerta"
          >
            <span className="sr-only">Cerrar</span>
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

Alert.propTypes = {
  children: PropTypes.node.isRequired,
  type: PropTypes.oneOf(['info', 'success', 'warning', 'error']),
  title: PropTypes.string,
  onClose: PropTypes.func,
  className: PropTypes.string,
};

export default Alert;
