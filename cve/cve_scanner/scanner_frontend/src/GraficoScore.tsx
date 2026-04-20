import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { useEffect, useRef } from "react";
import type { Vulnerabilidad } from "./types";

ChartJS.register(ArcElement, Tooltip, Legend);

export function GraficoScore({ data }: { data: Vulnerabilidad[] }) {
  const chartRef = useRef<any>(null);
  const theme = document.documentElement.getAttribute("data-theme");

  useEffect(() => {
    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, []);

  if (data.length === 0) {
    return <p>No hay datos suficientes para calcular el score ponderado.</p>;
  }

  const styles = getComputedStyle(document.documentElement);
  const textColor = styles.getPropertyValue("--text").trim();

  // Contar severidades (CORREGIDO: severidad)
  const low = data.filter(v => v.severidad === "LOW").length;
  const medium = data.filter(v => v.severidad === "MEDIUM").length;
  const high = data.filter(v => v.severidad === "HIGH").length;
  const critical = data.filter(v => v.severidad === "CRITICAL").length;

  const total = low + medium + high + critical;

  const scoreBase =
    total === 0
      ? 0
      : (low * 1 + medium * 2 + high * 3 + critical * 4) / total;

  const scoreFinal = (scoreBase / 4) * 10;

  // 🎨 Color dinámico según el score
  let donutColor = "#22c55e"; // verde

  if (scoreFinal >= 8) donutColor = "#ef4444";       // rojo
  else if (scoreFinal >= 6) donutColor = "#f97316";  // naranja
  else if (scoreFinal >= 3) donutColor = "#eab308";  // amarillo

  const chartData = {
    labels: ["Score Ponderado"],
    datasets: [
      {
        data: [scoreFinal, 10 - scoreFinal],
        backgroundColor: [donutColor, textColor + "22"],
        borderWidth: 0,
      },
    ],
  };

  const options = {
    cutout: "70%",
    plugins: {
      legend: { display: false },
      tooltip: { enabled: true },
    },
  };

  return (
    <div style={{ width: "250px", margin: "0 auto" }}>
      
      <Doughnut key={theme} ref={chartRef} data={chartData} options={options} />

      <p
        style={{
          textAlign: "center",
          marginTop: "10px",
          fontSize: "18px",
          color: "#0EA5E9",
        }}
      >
        {scoreFinal.toFixed(2)} / 10
      </p>
    </div>
  );
}

