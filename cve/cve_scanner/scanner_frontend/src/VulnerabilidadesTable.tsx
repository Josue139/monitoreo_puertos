import React, { useState } from "react";
import type { Vulnerabilidad } from "./types";

export function VulnerabilidadesTable({ data }: { data: Vulnerabilidad[] }) {
  const [clicked, setClicked] = useState<string[]>([]);

  const markClicked = (cve: string) => {
    setClicked((prev) => [...new Set([...prev, cve])]);
  };

  return (
    <div className="table-wrapper">
      <table className="vuln-table">
        <thead>
          <tr>
            <th>CVE</th>
            <th>Librería</th>
            <th>Versión</th>
            <th>Score</th>
            <th>Severidad</th>
            <th>Fecha detectado</th>
            <th>Fix</th>
            <th>Origen</th>
          </tr>
        </thead>

        <tbody>
          {data.map((v, index) => {
            const isClicked = clicked.includes(v.cve);

            return (
              <tr key={index}>
                <td>
                  <a
                    href={`https://www.cve.org/CVERecord?id=${v.cve}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={() => markClicked(v.cve)}
                    style={{
                      color: isClicked ? "#A855F7" : "#0EA5E9",
                      textDecoration: "none",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                      transition: "color 0.15s ease-in-out"
                    }}
                  >
                    {v.cve}

                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="14"
                      height="14"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3z" />
                      <path d="M5 5h5V3H3v7h2V5z" />
                      <path d="M19 19H5V9H3v12h16v-2z" />
                    </svg>
                  </a>
                </td>

                <td>{v.libreria}</td>
                <td>{v.version}</td>
                <td>{v.score}</td>

                <td className={`sev-${v.severidad.toLowerCase()}`}>
                  {v.severidad}
                </td>

                <td>{v.fecha_detectado}</td>
                <td>{v.fix}</td>
                <td>{v.origen}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

