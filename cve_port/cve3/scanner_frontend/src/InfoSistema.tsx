import React, { useState } from "react";

export function InfoSistema({ data }) {
  const [open, setOpen] = useState({
    interfaces: false,
    discos: false,
    modulos: false,
  });

  const toggle = (key) => {
    setOpen(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div style={{ padding: "10px" }}>
      <h2>Información del sistema</h2>

      <p><strong>Arquitectura:</strong> {data.arquitectura || "N/A"}</p>
      <p><strong>Kernel:</strong> {data.kernel_version || "N/A"}</p>
      <p><strong>OS Contenedor:</strong> {data.os_contenedor || "N/A"}</p>
      <p><strong>IP Escaneada:</strong> {data.escaneado || "N/A"}</p>
      <p><strong>Fecha análisis:</strong> {data.fecha_detectado || "N/A"}</p>

      {/* Interfaces */}
      <h3 onClick={() => toggle("interfaces")} style={{ cursor: "pointer" }}>
        {open.interfaces ? "▼" : "▶"} Interfaces de red ({data.interfaces_red?.length || 0})
      </h3>
      {open.interfaces && (
        <ul>
          {data.interfaces_red?.map((i, idx) => (
            <li key={idx}>{i}</li>
          ))}
        </ul>
      )}

      {/* Discos */}
      <h3 onClick={() => toggle("discos")} style={{ cursor: "pointer" }}>
        {open.discos ? "▼" : "▶"} Discos detectados ({data.discos_detectados?.length || 0})
      </h3>
      {open.discos && (
        <ul>
          {data.discos_detectados?.map((d, idx) => (
            <li key={idx}>{d}</li>
          ))}
        </ul>
      )}

      {/* Módulos */}
      <h3 onClick={() => toggle("modulos")} style={{ cursor: "pointer" }}>
        {open.modulos ? "▼" : "▶"} Módulos del kernel ({data.modulos_kernel?.length || 0})
      </h3>
      {open.modulos && (
        <ul>
          {data.modulos_kernel?.map((m, idx) => (
            <li key={idx}>{m}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

