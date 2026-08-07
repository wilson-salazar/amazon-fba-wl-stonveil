# WL Stonveil LLC — Amazon FBA Wholesale

Repositorio del proyecto Amazon FBA Wholesale de **WL Stonveil LLC**, gestionado desde Colombia.

---

## ¿Qué hay en este repositorio?

| Archivo | Descripción |
|---|---|
| `roadmap.html` | Dashboard interactivo con el roadmap completo del proyecto |
| `analizador/analizar.py` | Script Python para analizar productos con SmartScout + Keepa |
| `analizador/muestra_smartscout.csv` | CSV de muestra para probar el analizador |
| `analizador/requirements.txt` | Dependencias Python del analizador |

---

## Cómo ver el Roadmap

El roadmap es un archivo HTML standalone — no necesita servidor ni instalación.

**Opción 1 — Directa (recomendada):**
1. Descarga `roadmap.html`
2. Ábrelo con doble clic en cualquier navegador (Chrome, Firefox, Safari)

**Opción 2 — Servidor local:**
```bash
npx serve .
```
Luego abre `http://localhost:3000/roadmap.html`

> El roadmap guarda el progreso automáticamente en el navegador (localStorage). Cada vez que lo abras recordará el estado anterior.

---

## Cómo usar el Analizador de Productos

### Requisitos
- Python 3.8+
- API Key de Keepa (desde €49/mes en keepa.com)

### Instalación
```bash
cd analizador
pip install -r requirements.txt
```

### Uso con CSV de SmartScout
```bash
python3 analizar.py --csv tu_archivo.csv --apikey TU_KEEPA_API_KEY
```

### Uso con CSV de muestra (sin API Key)
```bash
python3 analizar.py --csv muestra_smartscout.csv
```

Genera un reporte HTML con los productos clasificados por score (ALTA / MEDIA / BAJA oportunidad).

---

## Contexto del proyecto

- **Empresa:** WL Stonveil LLC
- **Estado de registro:** Florida (via Bizee Plan Estándar)
- **Modelo:** Amazon FBA Wholesale
- **Herramienta de research:** SmartScout
- **Fundador:** Wilson Salazar — Colombia (no residente EE.UU.)

Para contexto completo del proyecto, decisiones tomadas y guía para Claude, ver `CLAUDE.md`.
