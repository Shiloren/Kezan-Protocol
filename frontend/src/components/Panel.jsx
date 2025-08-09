import React from 'react';

const Panel = ({ children }) => {
  return (
    <div className="bg-black-mineral p-4 rounded-lg text-warm-white">
      {children}
    </div>
  );
};

export default Panel;
