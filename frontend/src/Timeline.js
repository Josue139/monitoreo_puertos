import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import axios from 'axios';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

const COLORS = ['#00d2ff', '#4ade80', '#f87171', '#e879f9', '#fbbf24', '#22d3ee', '#818cf8', '#fb7185', '#a78bfa', '#2dd4bf'];

const selectStyle = {
  background: '#1c1c1f', color: '#a1a1aa', border: '1px solid #2d2d30',
  borderRadius: '6px', padding: '5px 10px', fontSize: '12px', cursor: 'pointer'
};

export default function Timeline({ onPortClick, selectedPort }) {
  const [data, setData] = useState([]);
  const [ports, setPorts] = useState([]);
  const [range, setRange] = useState('24h');
  const [limit, setLimit] = useState(10);
  const [selfScanData, setSelfScanData] = useState(null);

  const exportData = (type) => {
    const fileName = `reporte_trafico_${new Date().getTime()}`;
    if (type === 'json') {
      const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = `${fileName}.json`; a.click();
    } else {
      const csv = "Time," + ports.join(",") + "\n" + data.map(row => `${row.time},${ports.map(p => row[p] || 0).join(",")}`).join("\n");
      const blob = new Blob([csv], { type: 'text/csv' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = `${fileName}.csv`; a.click();
    }
  };

  const scanMyServer = async () => {
    try {
      const res = await axios.get('/api/scan-self');
      setSelfScanData(res.data);
    } catch (err) {
      console.error("Error en auditoría:", err);
    }
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    doc.text("STORM-PORT FORENSIC REPORT", 14, 20);
    autoTable(doc, {
        head: [['Puerto', 'Estado Detectado', 'Periodo']],
        body: ports.map(p => [p, 'Active', range]),
        startY: 30
    });
    doc.save("reporte.pdf");
  };

  useEffect(() => {
    axios.get(`/api/timeline?range=${range}`).then(res => {
      const pList = Object.keys(res.data).slice(0, limit);
      setPorts(pList);
      const timelineMap = {};
      
      pList.forEach(p => {
        res.data[p].forEach(pt => {
          const dateObj = new Date(pt.time);
          let timeLabel = (range === '7d' || range === '30d') 
            ? dateObj.toLocaleDateString([], { day: '2-digit', month: 'short' })
            : dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

          if (!timelineMap[timeLabel]) {
            timelineMap[timeLabel] = { time: timeLabel, raw: dateObj.getTime() };
          }
          timelineMap[timeLabel][p] = pt.val;
        });
      });
      setData(Object.values(timelineMap).sort((a,b) => a.raw - b.raw));
    });
  }, [range, limit]);

  return (
    <div style={{ background: '#111113', padding: '24px', borderRadius: '12px', border: '1px solid #1c1c1f' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h3 style={{ color: '#fff', fontSize: '13px', margin: 0 }}>PORT TRAFFIC HISTORY</h3>
          {selectedPort && (
            <button onClick={() => onPortClick(null)} style={{ background: '#3b82f6', color: '#fff', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px' }}>
              VER TODOS LOS PUERTOS
            </button>
          )}
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button onClick={scanMyServer} style={{...selectStyle, background: '#4f46e5', color: '#fff'}}>NMAP SCAN (LOCAL)</button>
          <button onClick={() => window.location.href = 'http://localhost:5173'} style={{...selectStyle, background: '#f59e0b', color: '#fff'}}>SCANNER CVE</button>
          <button onClick={generatePDF} style={{...selectStyle, background: '#27272a', color: '#fff'}}>PDF</button>
          <button onClick={() => exportData('csv')} style={selectStyle}>CSV</button>
          <button onClick={() => exportData('json')} style={selectStyle}>JSON</button>
          
          {/* SELECTOR DE LÍMITE (TOP) ACTUALIZADO */}
          <select style={selectStyle} value={limit} onChange={e => setLimit(parseInt(e.target.value))}>
            <option value="10">Top 10</option>
            <option value="20">Top 20</option>
            <option value="50">Top 50</option>
            <option value="100">Top 100</option>
          </select>

          {/* SELECTOR DE RANGO ACTUALIZADO */}
          <select style={selectStyle} value={range} onChange={e => setRange(e.target.value)}>
            <option value="1h">1 hora</option>
            <option value="2h">2 horas</option>
            <option value="6h">6 horas</option>
            <option value="12h">12 horas</option>
            <option value="24h">24 horas</option>
            <option value="7d">7 días</option>
            <option value="30d">30 días</option>
          </select>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid stroke="#1c1c1f" vertical={false} />
          <XAxis dataKey="time" stroke="#52525b" fontSize={10} minTickGap={30} />
          <YAxis stroke="#52525b" fontSize={10} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={{ background: '#000', border: '1px solid #333', fontSize: '12px' }} />
          {ports.map((p, i) => (
            <Line 
              key={p} type="monotone" dataKey={p} 
              stroke={COLORS[i % COLORS.length]} 
              strokeWidth={selectedPort === p ? 4 : 2}
              strokeOpacity={selectedPort && selectedPort !== p ? 0.1 : 1}
              dot={false} 
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '15px', marginTop: '20px' }}>
        {ports.map((p, i) => (
          <div key={p} onClick={() => onPortClick(p)} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: COLORS[i % COLORS.length] }}></div>
            <span style={{ fontSize: '12px', color: selectedPort === p ? '#fff' : '#a1a1aa' }}>Port {p}</span>
          </div>
        ))}
      </div>

    {selfScanData && (
      <div style={{
        position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        backgroundColor: '#18181b', padding: '20px', borderRadius: '8px',
        border: '1px solid #3f3f46', zIndex: 1000, color: '#fff', width: '400px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.5)'
      }}>
        <h3 style={{ marginTop: 0, color: '#a1a1aa' }}>Internal Forensic Audit</h3>
        <div style={{ maxHeight: '300px', overflowY: 'auto', fontFamily: 'monospace' }}>
          {selfScanData.map((item, index) => (
            <div key={index} style={{ marginBottom: '10px', borderBottom: '1px solid #27272a', paddingBottom: '5px' }}>
              <div style={{ color: '#60a5fa' }}>Port: {item.port}</div>
              <div>Banner: <span style={{ color: '#4ade80' }}>{item.banner}</span></div>
              <div style={{ fontSize: '0.8em', color: item.state === 'open' ? '#4ade80' : '#f87171' }}>
                Status: {item.state}
              </div>
            </div>
          ))}
        </div>
        <button onClick={() => setSelfScanData(null)} style={{ marginTop: '15px', padding: '8px 16px', background: '#3f3f46', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cerrar</button>
      </div>
    )}  
   </div>
  );
}
