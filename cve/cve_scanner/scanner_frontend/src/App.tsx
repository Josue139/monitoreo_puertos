/* ============================================================
   APP PRINCIPAL DEL DASHBOARD
   - Maneja el tema claro/oscuro
   - Carga datos del backend
   - Renderiza tablas y gráficos
============================================================ */

import './App.css';
import { useState, useEffect } from 'react';
import { VulnerabilidadesTable } from "./VulnerabilidadesTable";
import type { Vulnerabilidad } from "./types";
import { GraficoSeveridad } from "./GraficoSeveridad";
import { GraficoScore } from "./GraficoScore";
import { GraficoFechas } from "./GraficoFechas";

function App() {

  /* ------------------------------------------------------------
     🎨 SISTEMA DE TEMA (dark azul moderno / light moderno)
     - Se guarda en localStorage
     - Se aplica como data-theme="light" o data-theme="dark"
  ------------------------------------------------------------ */
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "dark"
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  /* ------------------------------------------------------------
     🚀 EJECUTAR ESCANEO AUTOMÁTICO AL ENTRAR AL DASHBOARD
     - Llama a /api/scan (backend)
     - Genera un nuevo reporte y actualiza historial
  ------------------------------------------------------------ */
  useEffect(() => {
    fetch("/api/scan", { method: "POST" })
      .then(() => console.log("Escaneo ejecutado"))
      .catch(() => console.log("Error ejecutando escaneo"));
  }, []);

  /* ------------------------------------------------------------
     📡 CARGA DE DATOS DESDE EL BACKEND
  ------------------------------------------------------------ */
  const [vulns, setVulns] = useState<Vulnerabilidad[]>([]);

  useEffect(() => {
    fetch("/api/reporte")
      .then(res => res.json())
      .then(data => {
        setVulns(data.vulnerabilidades || []);
      })
      .catch(err => {
        console.error("Error cargando datos del backend:", err);
      });
  }, []);

  /* ------------------------------------------------------------
     🖥️ RENDER DEL DASHBOARD
  ------------------------------------------------------------ */
  return (
    <div className="app-root">
      
      {/* ENCABEZADO */}
      <header className="app-header">
        <div>
          <h1>CVE Scanner Dashboard</h1>
          <p>Resumen de vulnerabilidades detectadas</p>
        </div>

        {/* BOTÓN DE TEMA */}
        <button onClick={toggleTheme} className="theme-button">
          Cambiar tema
        </button>
        
        <a href="/sistema" className="theme-button">
          Información de drivers encontrados
        </a>

      </header>

      {/* CONTENIDO PRINCIPAL */}
      <main className="app-main">

        {/* RESUMEN */}
        <section className="card">
          <h2>Resumen</h2>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total de vulnerabilidades: </span>
              <span className="summary-value">{vulns.length}</span>
            </div>
          </div>
        </section>

        {/* TABLA */}
        <section className="card full">
          <h2>Vulnerabilidades detectadas</h2>
          <VulnerabilidadesTable data={vulns} />
        </section>

        {/* GRÁFICO SEVERIDAD */}
        <section className="card">
          <h2>Gráfico por severidad</h2>
          <GraficoSeveridad data={vulns} />
        </section>

        {/* GRÁFICO SCORE */}
        <section className="card">
          <h2>Score Ponderado</h2>
          <GraficoScore data={vulns} />
        </section>

        {/* GRÁFICO EVOLUCIÓN */}
        <section className="card full">
          <h2>Evolución de vulnerabilidades</h2>
          <GraficoFechas data={vulns} />
        </section>

      </main>
    </div>
  );
}

export default App;

