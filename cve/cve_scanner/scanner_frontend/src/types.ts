export interface ImpactoCIA {
  confidencialidad: string;
  integridad: string;
  disponibilidad: string;
}

export interface Vulnerabilidad {
  cve: string;
  libreria: string;
  version: string;
  score: number;
  severidad: string;
  fecha_publicacion: string;
  fecha_detectado: string;
  descripcion: string;
  vector: string;
  impacto: ImpactoCIA;
  fix: string;
  sugerencia: string;
  driver: string | null;
  origen: string;
  enlace: string;
}
