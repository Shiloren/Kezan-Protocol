import React, { useEffect, useState } from 'react';
import MenuBar from './components/MenuBar';
import Navbar from './components/Navbar';
import ItemCard from './components/ItemCard';
import AuctionTable from './components/AuctionTable';
import FilterPanel from './components/FilterPanel';
import useKeyboardShortcuts from './hooks/useKeyboardShortcuts';
import { getConsejo, getGangas, getCrafteables } from './services/api';

export default function App() {
  const [consejo, setConsejo] = useState([]);
  const [gangas, setGangas] = useState([]);
  const [crafteables, setCrafteables] = useState([]);
  
  // Handlers para los atajos de teclado
  const keyboardHandlers = {
    newProfile: () => {
      console.log('Nuevo perfil');
      // Implementar lógica
    },
    importConfig: () => {
      console.log('Importar configuración');
      // Implementar lógica
    },
    exportConfig: () => {
      console.log('Exportar configuración');
      // Implementar lógica
    },
    searchItem: () => {
      console.log('Buscar item');
      // Implementar lógica
    },
    toggleScan: () => {
      console.log('Alternar escaneo');
      // Implementar lógica
    },
    marketAnalysis: () => {
      console.log('Análisis de mercado');
      // Implementar lógica
    },
    refresh: () => {
      console.log('Actualizar datos');
      // Implementar lógica
    },
    showHelp: () => {
      console.log('Mostrar ayuda');
      // Implementar lógica
    }
  };

  // Activar los atajos de teclado
  useKeyboardShortcuts(keyboardHandlers);

  useEffect(() => {
    getConsejo().then(setConsejo);
    getGangas().then(setGangas);
    getCrafteables().then(setCrafteables);
  }, []);

  return (
    <div className="min-h-screen bg-black-mineral text-warm-white">
      <MenuBar />
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
