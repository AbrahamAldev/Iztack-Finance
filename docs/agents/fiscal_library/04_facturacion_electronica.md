# Facturación Electrónica (CFDI) en México

> **Advertencia:** Los requisitos técnicos y plazos del CFDI cambian con las versiones del SAT. Verifica la versión vigente (actualmente CFDI 4.0) y los catálogos del SAT actualizados.

## ¿Qué es el CFDI?

El Comprobante Fiscal Digital por Internet (CFDI) es un documento electrónico que acredita operaciones comerciales entre contribuyentes. Es emitido, timbrado y recibido a través de internet con autorización del SAT.

## Versiones del CFDI

- **CFDI 3.3:** Versión anterior, aún vigente en archivos históricos.
- **CFDI 4.0:** Versión vigente con campos adicionales como RfcProvCertif, Exportación, entre otros.

Consultar el Anexo 20 de la RMF para la versión vigente.

## Tipos de comprobantes

| Tipo | Uso |
|------|-----|
| Ingreso | Ventas, prestación de servicios |
| Egreso | Devoluciones, descuentos, bonificaciones |
| Traslado | Traslado de mercancías |
| Nómina | Recibo de nómina |
| Pago | Complemento de pago |

## Elementos básicos de un CFDI

- **Emisor:** RFC, nombre, régimen fiscal.
- **Receptor:** RFC, nombre, régimen fiscal, uso CFDI, domicilio fiscal (cuando aplica).
- **Conceptos:** Descripción, cantidad, valor unitario, importe, objeto de impuesto.
- **Impuestos:** Traslados y retenciones de ISR, IVA, IEPS según corresponda.
- **Complementos:** Información adicional según el tipo de operación (pagos, nómina, comercio exterior, etc.).

## Uso CFDI más comunes

- G01 Adquisición de mercancías.
- G03 Gastos en general.
- I01 Construcciones.
- I04 Equipo de computo y accesorios.
- P01 Por definir.

## Plazos para solicitar factura

- No existe un plazo único federal para todos los comercios; cada establecimiento establece sus políticas.
- Sin embargo, para efectos de deducción personal o empresa, el CFDI debe estar expedido en el ejercicio fiscal correspondiente o dentro de los plazos que señale la LISR.

## Requisitos para deducir un CFDI

1. Estar vigente y relacionado con el RFC del contribuyente.
2. Contener el uso CFDI correcto.
3. Estar respaldado por una operación real.
4. Ser emitido por un contribuyente inscrito en el RFC.

## Validación básica de un CFDI

- Verificar el sello del SAT.
- Confirmar que el emisor esté activo en el RFC.
- Revisar que el UUID no esté cancelado.
- Validar que el total y conceptos coincidan con la operación.

## Fuentes

- SAT: "Factura electrónica (CFDI)" — https://www.sat.gob.mx
- Anexo 20 de la Resolución Miscelánea Fiscal vigente.
- LISR y LIVA, artículos relacionados con comprobantes fiscales.
