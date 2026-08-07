# Contexto del proyecto — WL Stonveil LLC

Este archivo da contexto completo a Claude para continuar asistiendo con el proyecto Amazon FBA Wholesale de Wilson Salazar.

---

## Perfil del usuario

- **Nombre:** Wilson Salazar
- **País:** Colombia (no residente EE.UU., sin SSN)
- **Experiencia:** Emprendedor nuevo en Amazon FBA, tomando curso de formación
- **Idioma preferido:** Español
- **Email:** wilsonsalazarortiz@gmail.com
- **Empresa:** WL Stonveil LLC (en proceso de formación)

---

## El negocio

- **Modelo:** Amazon FBA Wholesale (comprar a mayoristas, revender en Amazon)
- **Herramienta de research:** SmartScout (plan de pago)
- **Herramienta de datos históricos:** Keepa API (€49/mes mínimo)
- **Socia:** Su esposa — estructura Manager-Managed (Wilson = Member/dueño, esposa = Manager designada)

---

## Decisiones tomadas

| Decisión | Valor |
|---|---|
| Nombre LLC | WL Stonveil LLC |
| Estado de registro | **Florida** (decisión tomada, antes se evaluó Wyoming) |
| Servicio de formación | **Bizee Plan Estándar** — $324 total ($199 Bizee + $125 fee FL) |
| Registered Agent | Incluido en Bizee año 1, $119/año desde año 2 |
| Virtual Address | Incluido en Bizee 1er mes, luego servicio externo ~$10–15/mes |
| Teléfono EE.UU. | Google Voice (gratis, requiere VPN IP americana al registrar) |
| Cuenta bancaria | Wise Business o Relay (primera opción, friendly no residentes) |
| Prep Center | Florida (a definir proveedor) |
| Código NAICS | 455219 / 541613 / 454110 (confirmar con CPA cuál usar en SS-4) |

---

## ¿Por qué Florida y no Wyoming?

- El Prep Center opera en Florida → mismo estado simplifica todo
- Resale Certificate más directo al estar registrado en FL
- Evita Foreign LLC Registration (~$125 extra) + doble reporte anual
- Bizee opera en todos los estados, no solo Wyoming
- Costo: $324 formación vs $303 Wyoming (solo $21 más)
- Contra: reporte anual FL ~$138/año vs Wyoming $60/año

---

## Roadmap — 5 fases

### Fase 1: Registrar la LLC en Florida (Semana 1)
1. Elegir nombre — verificar en sunbiz.org
2. Contratar Bizee Plan Estándar ($324)
3. Filing Articles of Organization (incluido Bizee, sunbiz.org)
4. Redactar Operating Agreement — estructura Manager-Managed
5. Obtener número teléfono EE.UU. — Google Voice (VPN necesaria al registrar)
6. Obtener Virtual Mailbox — 1er mes incluido en Bizee, luego Anytime Mailbox/PostScan Mail

### Fase 2: Obtener EIN del IRS (Semanas 2–4)
1. Completar SS-4 — Bizee lo gestiona (incluido). Pide código NAICS (usar 455219 o consultar CPA)
2. Esperar procesamiento IRS (4–6 semanas sin Bizee, más rápido con Bizee)
3. Recibir EIN Confirmation Letter

### Fase 3: Abrir cuenta bancaria (Semanas 4–6, tras tener EIN)
1. Primera opción: Wise Business o Relay
2. Segunda opción: Mercury o Airwallex
3. Documentos: Articles of Organization + EIN Letter + Pasaporte + Dirección RA

### Fase 4: Amazon Seller Central + documentos legales (Semana 6+)
1. Registrar cuenta Seller Central ($39.99/mes)
2. Completar verificación de identidad
3. Completar W-8BEN (formulario fiscal para no residentes)
4. Obtener Florida Resale Certificate (gratis, floridarevenue.com)
5. Contratar Prep Center en Florida (a definir)

### Fase 5: Cumplimiento anual (ongoing)
1. Florida Annual Report — ~$138/año, vence antes del 1 de mayo en sunbiz.org
2. Form 5472 + 1120 — presentar ante IRS con CPA ($25,000 multa si no se presenta)
3. Renovar Registered Agent — Bizee $119/año desde año 2

---

## Presupuesto estimado total: ~$1,140 USD

| Concepto | Presup. |
|---|---|
| Registered Agent | $87.50 |
| Articles of Organization (FL) | $125.00 |
| EIN (servicio) | $100.00 |
| Amazon Seller Central | $39.99 |
| Florida Annual Report | $138.00 |
| CPA / Form 5472 | $550.00 |
| Otros | $100.00 |

---

## Conceptos clave ya explicados a Wilson

- **EIN** — número fiscal de la LLC, equivalente al NIT en Colombia
- **SS-4** — formulario IRS para solicitar el EIN
- **RA (Registered Agent)** — dirección legal en el estado de registro
- **Virtual Mailbox** — dirección comercial física para bancos y Amazon (diferente al RA)
- **Operating Agreement** — documento interno que define estructura de la LLC
- **W-8BEN** — formulario que declara que Wilson es no residente para efectos fiscales
- **Form 5472 + 1120** — declaración anual obligatoria para LLC de extranjero, multa $25,000
- **Resale Certificate** — exime de pagar Sales Tax al comprar a mayoristas
- **Nexus** — presencia fiscal en un estado; el proveedor solo cobra Sales Tax donde tiene nexus
- **BSR** — Best Seller Rank, velocidad de ventas de un producto en Amazon
- **ASIN** — Amazon Standard Identification Number, ID único de producto
- **NAICS** — código de clasificación industrial, se pide en SS-4 y apertura bancaria
- **ITIN** — número fiscal personal para no residentes; no es inmediatamente necesario, el CPA lo dirá
- **Manager-Managed LLC** — Wilson es Member (dueño), esposa es Manager (operadora)
- **Foreign LLC** — registro de LLC en un estado distinto al de formación (se evitó eligiendo FL)
- **CPA** — Contador público especializado en no residentes con LLC, indispensable para Form 5472

---

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `roadmap.html` | Dashboard HTML standalone con roadmap, tracker de costos, notas y contactos. Persistencia via localStorage (key: `wlstonveil_v2`). Dark theme. |
| `analizador/analizar.py` | Script Python: lee CSV de SmartScout, consulta Keepa API, genera reporte HTML con score por producto |
| `analizador/muestra_smartscout.csv` | 10 productos de muestra (marcas de botellas de agua) para pruebas |

---

## Pendientes importantes

- [ ] Consultar CPA antes de iniciar: confirmar código NAICS, estructura fiscal, si necesita ITIN
- [ ] Confirmar con CPA si el Prep Center en FL genera obligación de reporte adicional
- [ ] Elegir proveedor de Prep Center en Florida
- [ ] Elegir servicio de Virtual Mailbox para mes 2 en adelante
- [ ] Registrar número Google Voice (requiere VPN con IP americana)

---

## Tono y estilo para Claude

- Responder siempre en **español**
- Wilson es nuevo en el tema — explicar conceptos desde cero cuando los mencione
- Verificar precios directamente en sitios oficiales antes de afirmar costos exactos
- Siempre recomendar consultar CPA para decisiones fiscales y legales
- El roadmap (`roadmap.html`) es el artefacto principal — mantenerlo actualizado con cada decisión
