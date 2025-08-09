import React, { useState } from 'react';
import PropTypes from 'prop-types';

const WatchedItemsManager = ({ items, onAddItem, onRemoveItem, onUpdateThreshold }) => {
  const [newItemId, setNewItemId] = useState('');
  const [newThreshold, setNewThreshold] = useState('');

  const handleAddItem = (e) => {
    e.preventDefault();
    if (newItemId) {
      onAddItem(parseInt(newItemId, 10), newThreshold ? parseInt(newThreshold, 10) : null);
      setNewItemId('');
      setNewThreshold('');
    }
  };

  return (
    <div className="space-y-4">
      <form onSubmit={handleAddItem} className="flex space-x-4 mb-4">
        <input
          type="text"
          value={newItemId}
          onChange={(e) => setNewItemId(e.target.value)}
          placeholder="ID del Item"
          className="bg-black-mineral text-warm-white px-4 py-2 rounded-md border border-steel-gray/30 focus:border-goblin-green focus:outline-none"
        />
        <input
          type="text"
          value={newThreshold}
          onChange={(e) => setNewThreshold(e.target.value)}
          placeholder="Precio máximo (opcional)"
          className="bg-black-mineral text-warm-white px-4 py-2 rounded-md border border-steel-gray/30 focus:border-goblin-green focus:outline-none"
        />
        <button
          type="submit"
          className="bg-goblin-green hover:bg-deep-emerald text-warm-white px-4 py-2 rounded-md transition-colors"
        >
          Añadir Item
        </button>
      </form>

      <div className="space-y-2">
        {items.map(item => (
          <div
            key={item.id}
            className="flex items-center justify-between bg-graphite-soft p-4 rounded-md"
          >
            <div>
              <span className="text-warm-white">{item.name}</span>
              {item.threshold && (
                <span className="ml-2 text-steel-gray">
                  Max: {item.threshold}
                </span>
              )}
            </div>
            <div className="flex space-x-2">
              <input
                type="number"
                value={item.threshold || ''}
                onChange={(e) => onUpdateThreshold(item.id, parseInt(e.target.value, 10))}
                placeholder="Precio máximo"
                className="bg-black-mineral text-warm-white px-2 py-1 rounded-md border border-steel-gray/30 w-32"
              />
              <button
                onClick={() => onRemoveItem(item.id)}
                className="text-muted-red hover:text-red-400 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

WatchedItemsManager.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      threshold: PropTypes.number
    })
  ).isRequired,
  onAddItem: PropTypes.func.isRequired,
  onRemoveItem: PropTypes.func.isRequired,
  onUpdateThreshold: PropTypes.func.isRequired
};

export default WatchedItemsManager;
