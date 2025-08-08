import React from 'react';

export default function FilterPanel({ items }) {
  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.id} className="border border-spectral-cyan bg-graphite-soft p-2 rounded">
          <h4 className="font-alt">{item.nombre || item.name}</h4>
        </div>
      ))}
    </div>
  );
}
