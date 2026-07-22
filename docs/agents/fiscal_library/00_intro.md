# Biblioteca Fiscal — Introducción

> **Descargo de responsabilidad:** Esta biblioteca tiene fines educativos y de organización. No constituye asesoría fiscal, legal ni contable. Para decisiones con impacto fiscal, consulta siempre a un Contador Público certificado o al SAT directamente.

## Propósito

Esta biblioteca alimenta al **FiscalAdvisorAgent** de Iztack-Finance. Su objetivo es proporcionar contexto académico y práctico sobre obligaciones fiscales en México, especialmente para:

- Personas físicas con ingresos por sueldos y salarios.
- Personas físicas con actividad empresarial y profesional (incluyendo Régimen Simplificado de Confianza — RESICO).
- Pequeñas y medianas empresas (PYMES) en formación.

## Fuentes oficiales de consulta

- [Servicio de Administración Tributaria (SAT)](https://www.sat.gob.mx)
- [Ley del Impuesto sobre la Renta (LISR)](https://www.diputados.gob.mx/LeyesBiblio/ref/lir.htm)
- [Ley del Impuesto al Valor Agregado (LIVA)](https://www.diputados.gob.mx/LeyesBiblio/ref/liva.htm)
- [Código Fiscal de la Federación (CFF)](https://www.diputados.gob.mx/LeyesBiblio/ref/cff.htm)
- [SHCP — Secretaría de Hacienda y Crédito Público](https://www.gob.mx/shcp)

## Estructura de la biblioteca

1. `01_regimenes_fiscales.md` — Regímenes disponibles para personas físicas.
2. `02_deducciones_personales.md` — Deducciones personales autorizadas.
3. `03_contabilidad_pymes.md` — Nociones básicas de contabilidad para PYMES.
4. `04_facturacion_electronica.md` — CFDI, requisitos y plazos.
5. `05_obligaciones_sat.md` — Declaraciones, pagos y registros.

## Uso por el agente

Cuando un usuario pregunta sobre un tema fiscal, el agente recupera los fragmentos más relevantes de estos documentos y los usa como contexto para responder. La respuesta final debe:

- Ser clara y en español mexicano.
- Incluir una advertencia de que no sustituye asesoría profesional.
- Citar la fuente oficial cuando sea posible.
- No inventar montos, porcentajes ni fechas no contenidos en la biblioteca.
