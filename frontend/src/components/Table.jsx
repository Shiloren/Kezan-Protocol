import React from 'react';

const Table = ({ headers, rows }) => {
  return (
    <table className="w-full text-left border-collapse">
      <thead>
        <tr className="bg-graphite-soft text-warm-white">
          {headers.map((header, index) => (
            <th key={index} className="px-4 py-2 border-b border-steel-gray">
              {header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowIndex} className="hover:bg-black-mineral">
            {row.map((cell, cellIndex) => (
              <td key={cellIndex} className="px-4 py-2 border-b border-steel-gray text-light-gray">
                {cell}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default Table;
