import React from 'react';

export default function AuctionTable({ items }) {
  return (
    <table className="min-w-full bg-graphite-soft rounded">
      <thead className="bg-black-mineral">
        <tr>
          <th className="p-2 text-left">Item</th>
          <th className="p-2 text-left">Precio</th>
          <th className="p-2 text-left">Margen</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id} className="odd:bg-black-mineral even:bg-graphite-soft">
            <td className="p-2">{item.nombre || item.name}</td>
            <td className="p-2 font-mono">{item.precio || item.price}</td>
            <td className={`p-2 font-mono ${item.margen > 0 ? 'text-warm-yellow' : 'text-muted-red'}`}>
              {item.margen || item.margin}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
