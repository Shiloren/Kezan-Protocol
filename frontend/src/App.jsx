import React, { useEffect, useState } from 'react';
import Navbar from './components/Navbar';
import ItemCard from './components/ItemCard';
import AuctionTable from './components/AuctionTable';
import FilterPanel from './components/FilterPanel';
import { getConsejo, getGangas, getCrafteables } from './services/api';

export default function App() {
  const [consejo, setConsejo] = useState([]);
  const [gangas, setGangas] = useState([]);
  const [crafteables, setCrafteables] = useState([]);

  useEffect(() => {
    getConsejo().then(setConsejo);
    getGangas().then(setGangas);
    getCrafteables().then(setCrafteables);
  }, []);

  return (
    <div className="min-h-screen bg-black-mineral text-warm-white">
      <Navbar />
      <main className="p-4 space-y-8">
        <section>
          <h2 className="text-xl mb-2">Consejos de IA</h2>
          <div className="grid gap-4 md:grid-cols-3">
            {consejo.map((item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
        </section>
        <section>
          <h2 className="text-xl mb-2">Gangas</h2>
          <AuctionTable items={gangas} />
        </section>
        <section>
          <h2 className="text-xl mb-2">Crafteables rentables</h2>
          <FilterPanel items={crafteables} />
        </section>
      </main>
    </div>
  );
}
