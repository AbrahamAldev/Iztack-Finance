# 📜 Idea Original — Iztack-Tomin

> **Documento fundacional del proyecto.**
> Contiene las directrices primigenias que definen el alcance, propósito y filosofía del sistema.
> Usar como referencia para evaluar si el desarrollo se mantiene fiel a la visión original.

=================================================================
SISTEMA DE CONTROL DE FINANZAS PARA PYMES Y STARTUPS EN MEXICO
=================================================================

----------------------------------------------------
1. PUNTO DE PARTIDA: CAPTURA DEL TICKET
----------------------------------------------------
- Enviar una foto del ticket de compra desde el celular.
- Recepcion del ticket a traves de WhatsApp o Telegram.
- Procesamiento por un agente local o en la nube, que funcione de forma autonoma.
- El agente debe:
  - Detectar de que tienda o proveedor es el ticket.
  - Extraer todos los datos del ticket impreso: productos, importes, fecha, establecimiento, etc.


----------------------------------------------------
2. FACTURACION AUTOMATICA (CFDI)
----------------------------------------------------
- Con las credenciales guardadas del usuario, el agente entra al portal web de cada marca y realiza el proceso de solicitud de factura.
- Al terminar, debe descargar y almacenar el PDF y el XML de la factura correctamente generada.
- Si la factura ya fue enviada al correo, debe:
  - Buscarla en el email.
  - Evitar duplicados (PDF/XML ya existentes).
- Si ocurre un error, el bot debe notificarlo y proponer solucion:
  - Plazo vencido para facturar.
  - Datos ilegibles en el ticket.
  - Sin cuenta registrada en el portal.
- En caso de requerir una cuenta nueva, el agente:
  - Preguntara al usuario si desea crearla o usar una existente.
  - Si la crea, generara una contrasena, llenara los datos solicitados.
  - Al final, mandara las credenciales para que el usuario las guarde facilmente en su app de contrasenas de Apple o Google.


----------------------------------------------------
3. ALMACENAMIENTO Y ORGANIZACION DE LA INFORMACION
----------------------------------------------------
- Guardar las facturas y tickets en carpetas categorizadas por:
  - Establecimiento.
  - Tipo de gasto.
- Almacenamiento recomendado: Drive o equivalente que permita:
  - Visualizacion grafica.
  - Acceso desde distintos dispositivos.
  - Compartir la carpeta con un contador.
- Carpeta especial de garantias, donde se archivan productos con garantia o de un costo significativo. Ejemplos:
  - Muebles o colchones en IKEA.
  - Estufas, cafeteras o refrigeradores en Liverpool.
- Puede haber duplicidad intencional entre la carpeta de facturas y la de garantias (el mismo ticket puede vivir en ambas).
- Carpetas adicionales sugeridas:
  - Tickets vencidos.
  - Tickets danados.
  - Otras que se consideren utiles para mantener el orden.


----------------------------------------------------
4. ANALISIS FINANCIERO Y DASHBOARD
----------------------------------------------------
- Recopilar todos los productos comprados y generar un analisis financiero.
- Entregar el resultado en un Dashboard que muestre:
  - Areas de oportunidad en los gastos.
  - Areas de fuga de dinero.
- Ejemplos de analitica deseada:
  - Comparar compra semanal de rollos chicos vs. un paquete grande mensual.
  - Calcular cuanto se debe ahorrar cada semana para poder hacer una compra grande a fin o principio de mes sin que se sienta pesada.
- Dashboard principal (resumen general de familia mas cada negocio).
- Dashboards dedicados por cada nucleo (familia o negocio), con mas detalle y botones de accion.
- Diseno:
  - Minimalista, fresco, intuitivo.
  - Modo noche y modo dia.
  - Botones interactivos.
  - Seccion de configuracion (alta y baja de negocios, etc.).


----------------------------------------------------
5. LISTA DE COMPRAS INTELIGENTE
----------------------------------------------------
- Generacion de listas de compras basadas en el ciclo de uso detectado en los tickets.
- La lista debe auto ajustarse con cada nuevo ticket.
- Flujo colaborativo en familia:
  - Boton para generar lista de compras.
  - Compartirla con la familia para votar por eliminar o agregar productos.
  - Si se agrega algo: pedir nombre del producto, tienda preferida o link directo para evitar confusion.
  - Aprobacion final por el jefe de familia (acepta o rechaza cambios).
- Opciones de salida de la lista:
  - Pre ordenar productos que se puedan comprar en linea.
  - Generar lista digital para enviar a los jefes de familia.
  - Imprimir en impresora de tickets automatica con:
    - Lugar de compra (ejemplo: Central de Abastos).
    - Hora y fecha de impresion.
    - Cantidades y nombres.
    - Casillas para palomear.
    - Otros datos de alto valor.
- Actualizacion en tiempo real con la entrada de nuevos tickets:
  - Marcar lo que ya se compro.
  - Notificar lo que falta y preguntar si fue comprado sin ticket.


----------------------------------------------------
6. MULTI NEGOCIO FAMILIAR
----------------------------------------------------
- El sistema debe diferenciar cuentas, tickets y listas de cada negocio o nucleo familiar.
- Permitir anadir tantos negocios familiares como el usuario desee.
- Cada negocio debe contar con una API independiente que permita:
  - Integrarse con un sistema POS.
  - Que el POS pueda:
    - Solicitar alta de un nuevo producto o insumo.
    - Modificar cantidades.
    - Retirar productos.
  - Que el POS reciba informacion financiera: costos de productos, alertas de subidas de precio, etc.
- Analitica esperada para el negocio familiar:
  - Detectar areas de oportunidad (ejemplo: comprar mas en una tienda que en otra).
  - Avisar sobre ajuste de precios al publico segun variacion de costos.
- Dashboard de negocio:
  - Igual flujo de lista de compras, pero en lugar de ir a jefes de familia, va al jefe del negocio o encargado de compras.
  - Boton que mete los productos al carrito en el portal del proveedor.
  - Si no hay stock: sugerir sustituto o no comprar por ahora.
  - Al final, generar link del carrito para que el usuario termine el pago manualmente.
  - El mismo boton debe existir en el Dashboard familiar.


----------------------------------------------------
7. MODULO FISCAL (MEXICO)
----------------------------------------------------
- Apartado especial para ingresar:
  - Constancia de situacion fiscal.
  - Estados de cuenta bancarios.
- Entender:
  - Ingresos.
  - Regimen fiscal.
  - Obligaciones fiscales existentes.
- Integrar ingresos y egresos al sistema.
- Permitir indicar:
  - Cuenta bancaria personal de quienes reciben ingresos en casa.
  - Cuentas bancarias de cada negocio.
  - O bien, una sola cuenta para todo.
  - Considerar transferencias y pagos de servicios.
- Entregables del modulo:
  - Reporte de que gastos son deducibles de impuestos en Mexico.
  - Buenas practicas para optimizar y minimizar impuestos pagados de mas.
  - Calculo de compras y cruce con la informacion fiscal.


----------------------------------------------------
> **Ultima actualizacion:** 19/06/2026
> **Proyecto:** Iztack-Tomin
> **Propósito:** Mantener la vision original como referencia contra desviaciones.