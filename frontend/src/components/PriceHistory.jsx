import React from 'react';
import PropTypes from 'prop-types';

const PriceHistory = ({ history, itemId }) => {
  // Ordenar el historial por fecha
  const sortedHistory = [...history].sort((a, b) => 
    new Date(b.timestamp) - new Date(a.timestamp)
  );

  // Calcular estadísticas
  const prices = history.map(h => h.price);
  const stats = {
    min: Math.min(...prices),
    max: Math.max(...prices),
    avg: Math.round(prices.reduce((a, b) => a + b, 0) / prices.length)
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-graphite-soft p-4 rounded-md">
          <div className="text-steel-gray text-sm">Precio Mínimo</div>
          <div className="text-warm-white text-lg">{stats.min}</div>
        </div>
        <div className="bg-graphite-soft p-4 rounded-md">
          <div className="text-steel-gray text-sm">Precio Máximo</div>
          <div className="text-warm-white text-lg">{stats.max}</div>
        </div>
        <div className="bg-graphite-soft p-4 rounded-md">
          <div className="text-steel-gray text-sm">Precio Promedio</div>
          <div className="text-warm-white text-lg">{stats.avg}</div>
        </div>
      </div>

      <div className="bg-graphite-soft rounded-md overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-black-mineral">
              <th className="px-4 py-2 text-left text-steel-gray">Fecha</th>
              <th className="px-4 py-2 text-left text-steel-gray">Precio</th>
              <th className="px-4 py-2 text-left text-steel-gray">Cantidad</th>
            </tr>
          </thead>
          <tbody>
            {sortedHistory.map((entry, index) => (
              <tr 
                key={`${itemId}-${index}`}
                className="border-t border-steel-gray/10"
              >
                <td className="px-4 py-2 text-warm-white">
                  {new Date(entry.timestamp).toLocaleString()}
                </td>
                <td className="px-4 py-2 text-warm-white">
                  {entry.price}
                </td>
                <td className="px-4 py-2 text-warm-white">
                  {entry.quantity}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

PriceHistory.propTypes = {
  history: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.string.isRequired,
      price: PropTypes.number.isRequired,
      quantity: PropTypes.number.isRequired
    })
  ).isRequired,
  itemId: PropTypes.number.isRequired
};

export default PriceHistory;
