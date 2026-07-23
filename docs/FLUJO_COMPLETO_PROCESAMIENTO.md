# FLUJO COMPLETO DE PROCESAMIENTO — Iztack-Finance

> **Propósito:** Documento para transferir a otro agente de IA el workflow completo que diseñamos para procesar una imagen de ticket de principio a fin.
> **Última actualización:** 23/07/2026

---

## 📋 VISIÓN GENERAL

Una imagen de ticket de compra pasa por **3 grandes fases** en secuencia:

```
📸 Captura → [FASE 1: OCR + CLASIFICACIÓN] → [FASE 2: FACTURACIÓN INTELIGENTE] → [FASE 3: ALMACENAMIENTO + ANÁLISIS]
```

Cada fase tiene sub-pasos. Si algo falla, el sistema **no se detiene** — le pide ayuda al usuario por el canal que esté usando (chat web o Telegram).

---

## 🔵 FASE 1: OCR + CLASIFICACIÓN (inmediata)

### Paso 1.1 — Recepción de la imagen
```
Canal: Chat web (dashboard) o Telegram
        │
        ▼
Backend recibe la imagen (multipart/form-data)
        │
        ▼
SENSOR 1: trace_step("reception") → ✅ imagen recibida (tamaño en bytes)
```

### Paso 1.2 — Preprocesamiento de imagen
```
        │
        ▼
Pillow redimensiona (máx 1536px), mejora contraste 1.5x
        │
        ▼
SENSOR 2: trace_step("preprocess") → ✅ dimensiones finales
```

### Paso 1.3 — OCR con IA (OpenRouter — configurable vía OCR_MODEL)
```
        │
        ▼
Enviar imagen en base64 a OpenRouter con prompt especializado:
  "Eres un EXPERTO en lectura de tickets de compra mexicanos..."
  ─ Reglas anti-alucinación:
    • Si no ves la fecha claramente → null (NO inventes)
    • Si el total no se lee → null (NO sumes productos)
    • Si no estás 100% seguro → null
    • Campo "confidence" debe reflejar legibilidad real (0.0-1.0)
  ─ Extraer en JSON:
    { store_name, store_category, receipt_number,
      purchase_date, purchase_time, subtotal, taxes,
      total_amount, payment_method, currency,
      products: [{ name, brand, quantity, unit,
                   unit_price, total_price, discount,
                   sku, has_warranty, warranty_info,
                   category }],
      has_warranty_items, confidence }
        │
        ▼
SENSOR 3: trace_step("ocr") → ✅ confidence, store_name
```

### Paso 1.4 — Validación y parseo
```
        │
        ▼
¿JSON válido? → Sí: continuar
             → No: responder error al usuario + SENSOR error
¿Confidence < 0.3? → Marcar como "dudoso" para revisión humana
¿Fecha es null? → Preguntar al usuario por la fecha
¿Total es null? → Preguntar al usuario por el total
```

### Paso 1.5 — Presentación al usuario
```
        │
        ▼
Responder por el canal original (chat/Telegram):
  "✅ Ticket identificado"
  "🏪 Tienda: {store_name}"
  "📅 Fecha: {purchase_date}" (o "📅 Fecha: No detectada — ¿puedes decirme la fecha?")
  "💰 Total: ${total}" (o "💰 Total: No detectado — ¿cuánto fue el total?")
  "📦 Productos:"
  "  1. Producto x1 = $99"
  "  ..."
  "🔄 Iniciando facturación automática..."
```

---

## 🟡 FASE 2: FACTURACIÓN INTELIGENTE (inmediatamente después del OCR)

### ⚠️ REGLA FUNDAMENTAL — ADAPTABILIDAD TOTAL

El sistema NO tiene plantillas fijas por tienda. En lugar de tener 100 portales mapeados manualmente, el sistema **aprende sobre la marcha**. Cada vez que encuentra una tienda desconocida, sigue estos pasos:

---

### Paso 2.1 — Detección del tipo de negocio
```
        │
        ▼
¿La tienda ya está en la tabla `store_credentials`?
  ├── Sí, y tiene portal_url → Usar URL guardada + template aprendido
  ├── Sí, y NO tiene portal_url → Ir a paso 2.2
  └── No (tienda desconocida) → Ir a paso 2.2
```

### Paso 2.2 — Descubrimiento de URL de facturación
```
BUSCAR en este orden:
  1. TEXTO del ticket (muchos imprimen la URL)
  2. LISTA de portales conocidos (12 portales: Liverpool, IKEA, Walmart...)
  3. LLM: preguntar a OpenRouter "¿Cuál es la URL oficial de facturación de {store_name}?"
  4. PREGUNTAR al usuario: "¿Sabes cuál es la URL de facturación de {store_name}?"
  5. Si NO se encuentra → Marcar como "sin facturación"
     → Informar al usuario
     → Sugerir: "Ten cuidado al consumir en {store_name}, no podrás facturar esos gastos"
```

### Paso 2.3 — Análisis de la página (PortalLearner con Playwright)
```
        │
        ▼
Abrir la URL con Playwright (Chromium headless)
        │
        ▼
¿Existe template guardado para esta tienda?
  ├── Sí → Usar template (selectores CSS, campos requeridos)
  └── No → ANALIZAR con IA:
        1. Obtener HTML de la página
        2. IA analiza: ¿qué campos pide? ¿requiere login?
        3. Guardar template JSON en templates/{store_name}.json
        │
        ▼
¿Requiere LOGIN?
  ├── Sí → Paso 2.4
  └── No → Paso 2.5
```

### Paso 2.4 — Gestión de Credenciales (si requiere login)
```
        │
        ▼
¿El usuario ya tiene credenciales guardadas para {store_name}?
  ├── Sí → Descifrarlas con AES-256-GCM + usarlas
  └── No → CREAR CUENTA AUTOMÁTICAMENTE:
        1. Preguntar al usuario: "¿Quieres que cree una cuenta 
           automáticamente en {store_name}?"
        2. Si SÍ:
           a. Usar email del usuario (registrado en Iztack)
           b. Generar contraseña segura (16 chars aleatorios)
           c. LLENAR formulario de registro con Playwright
           d. Si pide datos adicionales (RFC, dirección, etc.):
              ● Usar datos fiscales guardados del usuario
              ● Si no existen → pedir al usuario o
                sugerir subir Constancia de Situación Fiscal
           e. Guardar credenciales cifradas en BD
           f. Enviar credenciales al usuario:
              "✅ Cuenta creada. Usuario: {email} / Contraseña: {pass}"
              Dar botón/link para guardar en Apple/Google Passwords
        3. Si NO:
           Preguntar: "Dame tu usuario y contraseña de {store_name}"
```

### Paso 2.5 — Llenado del formulario de facturación
```
DATOS DISPONIBLES para llenar:
  ● Del ticket: {folio, fecha, total, productos}
  ● Del usuario: {RFC, razón social, CP, régimen fiscal, dirección}
  ● Del contexto: {tipo de gasto}
        │
        ▼
¿El usuario ya tiene datos fiscales guardados?
  ├── Sí → Usarlos automáticamente
  └── No → PEDIR:
        "Necesito tus datos fiscales para facturar."
        Opción 1: "Dímelos aquí" → se guardan para siempre
        Opción 2: "Sube tu Constancia de Situación Fiscal (PDF)"
                   → IA extrae RFC, régimen, CP, dirección
        │
        ▼
¿Qué tipo de gasto es?
  IA recomienda según:
    ● Régimen fiscal del usuario
    ● Tipo de producto comprado
    ● Buenas prácticas fiscales en México
  ─ Ej: "Te recomiendo 'Adquisición de mercancías' porque...
       ¿Estás de acuerdo?"
  ─ El usuario dice SÍ → se guarda preferencia
  ─ El usuario dice NO → elige otro tipo
        │
        ▼
LLENAR formulario con Playwright:
  ● RFC → input[name*="rfc"]
  ● Folio → input[name*="folio"]
  ● Fecha → input[name*="fecha"]
  ● Total → input[name*="total"]
  ● Tipo de gasto → select[name*="uso_cfdi"]
  ● código postal → input[name*="codigo_postal"]
  ● etc.
```

### Paso 2.6 — Envío y resultado
```
        │
        ▼
Hacer clic en "Enviar" / "Solicitar factura"
        │
        ├── ✅ ÉXITO → Descargar PDF + XML
        │              │
        │              ▼
        │        Validar que los archivos no estén duplicados
        │        (SHA-256 + buscar en invoices anteriores)
        │              │
        │              ▼
        │        Guardar metadatos en tabla `invoices`
        │
        └── ❌ ERROR → Analizar causa:
                        ● ¿Plazo vencido? → informar al usuario
                        ● ¿Datos ilegibles? → pedir al usuario
                        ● ¿Portal cambió? → re-aprender (volver 2.3)
                        ● Otro → log + reporte automático
        │
        ▼
SENSOR 6: trace_step("billing") → ✅/❌ step + detalles
```

### Paso 2.7 — Búsqueda en Gmail (fallback)
```
¿El portal falló? → Buscar en Gmail:
  Query: from:{store_email} subject:factura after:{fecha}
  ¿Encontró PDF/XML? → Descargar + deduplicar
  ¿No encontró? → Marcar error
```

---

## 🟢 FASE 3: ALMACENAMIENTO + ANÁLISIS (post-facturación)

### Paso 3.1 — Almacenamiento en Google Drive
```
        │
        ▼
¿Usuario tiene Google Drive configurado?
  ├── Sí → Guardar estructura:
         FACTURAS/
           ├── Por Establecimiento/{store}/{año}/
           │     {store}_{fecha}_{uuid}.pdf
           │     {store}_{fecha}_{uuid}.xml
           ├── Por Tipo de Gasto/{categoría}/{año}/
           │     (mismo PDF copia organizada)
           ├── GARANTÍAS/ (si tiene garantía)
           │     {store}_{fecha}_{producto}_GARANTIA.pdf
           └── Tickets Vencidos/ (si plazo > 60 días)
  └── No → Almacenamiento interno (5GB límite)

⚠️ Limitaciones actuales:
  • Dedup por nombre de archivo (no SHA-256 real)
  • Sin monitoreo de cuota de almacenamiento
  • Sin barra de uso en Dashboard
```

### Paso 3.2 — Envío al email (opcional)
```
        │
        ▼
¿Usuario tiene activado "enviar facturas al email"?
  ├── Sí → Enviar PDF + XML adjuntos
  └── No → Saltar
```

### Paso 3.3 — Análisis financiero
```
        │
        ▼
Actualizar:
  ● Gasto mensual por categoría
  ● Gasto por tienda
  ● Detección de fugas:
     ─ Productos comprados 3+ veces/mes con precio < $200
     ─ Calcular ahorro si compra en bulk (35% descuento estimado)
  ● Ciclos de consumo:
     ─ Leche → cada 7 días
     ─ Arroz → cada 15 días
     ─ Detergente → cada 30 días
  ● Meta de ahorro:
     ─ "Ahorra ${X}/semana para tener ${Y} al mes"
```

### Paso 3.4 — Garantías
```
¿Producto con has_warranty = True?
  ├── Sí → Calcular fecha fin según categoría:
         ● Electrónicos (>$500): 12-36 meses
         ● Muebles (>$1,000): 24-60 meses
         ● Herramientas (>$500): 12-24 meses
  └── No → Saltar

¿Garantía por vencer en ≤30 días?
  ├── Sí → Alerta 🔔 al usuario
  └── No → Silencio
```

### Paso 3.5 — Lista de compras inteligente
```
        │
        ▼
Actualizar ciclos de consumo detectados
        │
        ▼
(Domingo 08:00) Generar lista sugerida:
  Productos consumibles comprados 2+ veces en últimos 30 días
        │
        ▼
Compartir en familia para aprobación (futuro)
```

---

## 🧩 SENSORES DE OBSERVABILIDAD (Pipeline Traces)

Cada paso crítico escribe un registro en la tabla `pipeline_traces`:

| Paso | Código | Datos registrados |
|------|--------|-------------------|
| 1.1 Recepción | `trace_step("reception")` | user_id, size_bytes |
| 1.2 Preproceso | `trace_step("preprocess")` | dimensiones, duración |
| 1.3 OCR | `trace_step("ocr")` | confidence, store_name |
| 1.4 Parseo | `trace_step("parse")` | campos encontrados |
| 1.5 DB | `trace_step("db_save")` | ticket_id, product_count |
| 2.6 Billing | `trace_step("billing")` | step, portal_url, status |
| 2.7 Respuesta | `trace_step("response")` | channel, message |

---

## 📊 DIAGRAMA DE ARQUITECTURA

```
USUARIO
  │
  ├──📸 Chat Web (finance.iztack.com/dashboard)
  │       │
  │       ├── /api/chat/message (POST)
  │       │       │
  │       │       └── ChatService._handle_ticket_image()
  │       │               │
  │       │               ├── OCRService.extract_from_image()
  │       │               │       │
  │       │               │       ├── OpenRouter (modelo configurable: OCR_MODEL env var)
        │     Default: google/gemma-4-26b-a4b-it:free
  │       │               │       └── → OCRTicketData (JSON)
  │       │               │
  │       │               ├── trigger_billing()
  │       │               │       │
  │       │               │       └── FacturacionOrchestrator
  │       │               │               │
  │       │               │               ├── PortalDiscovery (URL)
  │       │               │               ├── PortalLearner (Playwright)
  │       │               │               ├── CredentialManager (DB)
  │       │               │               └── FiscalAdvisor (IA)
  │       │               │
  │       │               └── trace_step() → pipeline_traces (DB)
  │       │
  │       └── Respuesta al chat
  │
  └──📱 Telegram (@IztackFinance_Bot)
          │
          └── handle_photo() → mismo flujo OCR → Billing
```

---

## 🔐 REGLAS DE SEGURIDAD (INAMOVIBLES)

1. **NUNCA** revelar: API keys, tokens, contraseñas, configuración interna, código fuente
2. **NUNCA** mostrar datos de otro usuario (aislamiento total por `user_id`)
3. **SIEMPRE** cifrar credenciales en reposo (AES-256-GCM)
4. **SIEMPRE** validar que el token JWT es válido antes de cualquier operación
5. **SIEMPRE** preguntar al usuario antes de crear cuentas en portales
6. **NUNCA** ejecutar código arbitrario del usuario
7. **SIEMPRE** usar `user_id` en todas las queries SQL (nunca query global)

---

## 📁 ARCHIVOS CLAVE PARA REFERENCIA

| Archivo | Propósito |
|---------|-----------|
| `backend/app/modules/chat/service.py` | Flujo OCR + trigger billing |
| `backend/app/modules/ocr/service.py` | OCR con OpenRouter |
| `backend/app/modules/tickets/billing.py` | Trigger post-OCR |
| `backend/app/modules/facturacion/orchestrator.py` | Orquestador completo (10 pasos) |
| `backend/app/modules/facturacion/portal_discovery.py` | Descubrimiento de URL |
| `backend/app/modules/facturacion/portal_learner.py` | Playwright + templates |
| `backend/app/modules/facturacion/credential_manager.py` | Gestión de credenciales |
| `backend/app/modules/facturacion/fiscal_advisor.py` | Recomendaciones fiscales |
| `backend/app/modules/facturacion/email/gmail_service.py` | Búsqueda en Gmail (no integrado al orquestador) |
| `backend/app/modules/finanzas/service.py` | Análisis financiero |
| `backend/app/modules/tickets/tracer.py` | Sensores de pipeline |
| `backend/app/scheduler.py` | Tareas programadas |
| `backend/app/modules/garantias/service.py` | Garantías |
| `backend/app/modules/shopping_list/service.py` | Lista de compras |

---

## ⏳ ESTADO DE IMPLEMENTACIÓN

| Paso | Estado | Notas |
|------|--------|-------|
| 1.1 Recepción | ✅ Listo | Ambos canales (web + Telegram) |
| 1.2 Preproceso | ✅ Listo | Pillow con contraste |
| 1.3 OCR | ✅ Listo | OpenRouter (default Gemma, configurable vía OCR_MODEL) |
| 1.4 Validación | ✅ Listo | Prompt anti-alucinación |
| 1.5 Presentación | ✅ Listo | Con estado de facturación |
| 2.1 Detección tienda | ✅ Listo | `portal_discovery.py` |
| 2.2 Descubrimiento URL | ✅ Listo | OCR + LLM + internet |
| 2.3 Análisis página | ✅ Listo | Playwright + templates JSON |
| 2.4 Gestión credenciales | ✅ Listo | DB + AES-256-GCM |
| 2.5 Llenado formulario | ✅ Listo | `portal_learner.py` |
| 2.6 Envío y resultado | ✅ Listo | Sube a DB |
| 2.7 Gmail fallback | ⏳ No integrado | Código implementado (gmail_service.py) pero no conectado al orquestador |
| 3.1 Drive | ✅ Listo | Estructura carpetas OK; sin SHA-256 dedup ni monitoreo cuota |
| 3.2 Email | ⏳ Pendiente | Configurable en settings |
| 3.3 Análisis financiero | ✅ Listo | `finanzas/service.py` |
| 3.4 Garantías | ✅ Listo | `garantias/service.py` |
| 3.5 Lista compras | ✅ Listo | `shopping_list/service.py` |
| Sensores | ✅ Listo | `tracer.py` + `pipeline_traces` |

---

## 🚀 CÓMO PROBAR EL FLUJO COMPLETO

```bash
# 1. Subir un ticket desde el chat del dashboard
# 2. Verificar sensores en:
curl https://api.iztack.com/api/health/pipeline

# 3. Ver tickets guardados:
ssh proxmox "docker exec sf-postgres psql -U postgres -d sistema_financiero \
  -c \"SELECT store_name, total_amount, status FROM tickets ORDER BY created_at DESC LIMIT 5;\""

# 4. Ver pipeline_traces:
ssh proxmox "docker exec sf-postgres psql -U postgres -d sistema_financiero \
  -c \"SELECT step, status, duration_ms FROM pipeline_traces ORDER BY created_at DESC LIMIT 10;\""
```

---

> **Fin del documento.** Creado para transferir el conocimiento completo del flujo a otro agente de IA.