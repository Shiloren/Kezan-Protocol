import React from 'react';
import { Hammer } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-graphite-soft text-warm-white p-4 flex items-center gap-2">
      <Hammer className="text-goblin-green" />
      <span className="font-alt text-lg">Kezan Protocol</span>
    </nav>
  );
}
