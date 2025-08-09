import React from 'react';
import PropTypes from 'prop-types';

const GameVersionSelector = ({ currentVersion, onVersionChange }) => {
  const versions = [
    { id: 'retail', name: 'WoW Retail' },
    { id: 'classic', name: 'WoW Classic' },
    { id: 'classic_era', name: 'WoW Classic Era' }
  ];

  return (
    <div className="flex items-center space-x-4 p-4 bg-graphite-soft rounded-lg">
      <span className="text-warm-white">Versión:</span>
      <div className="flex space-x-2">
        {versions.map(version => (
          <button
            key={version.id}
            onClick={() => onVersionChange(version.id)}
            className={`px-4 py-2 rounded-md transition-colors ${
              currentVersion === version.id
                ? 'bg-goblin-green text-warm-white'
                : 'bg-black-mineral text-steel-gray hover:bg-deep-emerald/20'
            }`}
          >
            {version.name}
          </button>
        ))}
      </div>
    </div>
  );
};

GameVersionSelector.propTypes = {
  currentVersion: PropTypes.oneOf(['retail', 'classic', 'classic_era']).isRequired,
  onVersionChange: PropTypes.func.isRequired
};

export default GameVersionSelector;
