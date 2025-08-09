import React from 'react';

const Card = ({ title, children, borderColor = 'spectral-cyan' }) => {
  return (
    <div className={`bg-graphite-soft border border-${borderColor} rounded-xl p-4 text-warm-white`}>
      <h3 className="text-golden-glow font-bold">{title}</h3>
      <div className="text-light-gray mt-2">{children}</div>
    </div>
  );
};

export default Card;
