import React from 'react';

export default function ItemCard({ item }) {
  return (
    <div className="border border-spectral-cyan bg-graphite-soft p-4 rounded">
      <h3 className="font-alt mb-2">{item.nombre || item.name}</h3>
      {item.descripcion || item.description ? (
        <p className="text-light-gray">{item.descripcion || item.description}</p>
      ) : null}
    </div>
  );
}
