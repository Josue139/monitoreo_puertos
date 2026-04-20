import { useEffect, useState } from "react";
import { InfoSistema } from "./InfoSistema";

export default function Sistema() {
  const [drivers, setDrivers] = useState(null);

  useEffect(() => {
    fetch("/api/drivers")
      .then(res => res.json())
      .then(data => {
        console.log("JSON recibido:", data);
        setDrivers(data);
      })
      .catch(err => console.error("Error:", err));
  }, []);

  if (!drivers) return <p style={{ padding: 20 }}>Cargando...</p>;

  return (
    <div style={{ padding: "20px", color: "white" }}>
      <h1>Información de Drivers</h1>
       <a 
      href="/" 
      style={{
        display: "inline-block",
        marginBottom: "20px",
        padding: "8px 14px",
        background: "#444",
        color: "white",
        borderRadius: "6px",
        textDecoration: "none"
      }}
    >
      ⬅ Volver al inicio
    </a>
      {/* Mostrar InfoSistema */}
      <InfoSistema data={drivers} />
    </div>
  );
}

