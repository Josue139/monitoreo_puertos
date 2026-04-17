import React, { useState } from 'react';
import Timeline from './Timeline';
import PortTable from './PortTable';
import './index.css';

function App() {
  const [selectedPort, setSelectedPort] = useState(null);

  return (
    <div style={{ padding: '40px' }}>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0 }}>Tráfico de Puertos</h1>
        <p style={{ fontSize: '14px', color: '#a1a1aa', margin: '4px 0 0 0' }}>
          Análisis Forense en Tiempo Real - IES Villaverde
        </p>
      </header>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <Timeline selectedPort={selectedPort} onPortClick={setSelectedPort} />
        <PortTable selectedPort={selectedPort} />
      </div>
    </div>
  );
}

export default App;
