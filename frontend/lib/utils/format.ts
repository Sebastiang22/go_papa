/**
 * Utilidades de formateo para la aplicación
 */

/**
 * Formatea un número como moneda en pesos colombianos
 */
export const formatCOP = (value: number): string => {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

/**
 * Formatea una fecha en formato corto (DD/MM/YYYY HH:MM)
 */
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
};

/**
 * Formatea una fecha en formato largo (día, mes año, hora:minuto)
 */
export const formatDateLong = (dateString: string): string => {
  return new Date(dateString).toLocaleString("es-CO", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}; 