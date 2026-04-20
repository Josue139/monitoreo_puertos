import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { useEffect, useRef } from "react";
import type { Vulnerabilidad } from "./types";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export function GraficoSeveridad({ data }: { data: Vulnerabilidad[] }) {
  const chartRef = useRef<any>(null);
  const theme = document.documentElement.getAttribute("data-theme");

  useEffect(() => {
    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, []);

  const styles = getComputedStyle(document.documentElement);
  const textColor = styles.getPropertyValue("--text").trim();

  const severidades = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
  const conteo = severidades.map(
    (sev) => data.filter((v) => v.severidad === sev).length
  );

  const chartData = {
    labels: severidades,
    datasets: [
      {
        label: "Cantidad",
        data: conteo,
        backgroundColor: [
          styles.getPropertyValue("--chart-low").trim(),
          styles.getPropertyValue("--chart-medium").trim(),
          styles.getPropertyValue("--chart-high").trim(),
          styles.getPropertyValue("--chart-critical").trim(),
        ],
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { labels: { color: textColor } },
      tooltip: { enabled: true },
    },
    scales: {
      x: { ticks: { color: "#0EA5E9" }
 },
      y: {
        ticks: {
          color: "#0EA5E9",
          stepSize: 1,
          precision: 0,
        },
        beginAtZero: true,
      },
    },
  };

  return <Bar key={theme} ref={chartRef} data={chartData} options={options} />;
}

