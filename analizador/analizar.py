"""
WL Stonveil LLC — Analizador de Oportunidades Wholesale FBA
Uso: python analizar.py --csv muestra_smartscout.csv --apikey TU_KEY_DE_KEEPA
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone

import pandas as pd

# ──────────────────────────────────────────
#  CRITERIOS DE SCORING (ajusta aquí después del curso)
# ──────────────────────────────────────────
CRITERIOS = {
    "bsr_min":          500,      # BSR mínimo aceptable (muy bajo = saturado)
    "bsr_max":          50_000,   # BSR máximo aceptable (muy alto = no rota)
    "sellers_min":      2,        # mínimo de sellers (1 = marca exclusiva, no aplica)
    "sellers_max":      10,       # máximo de sellers (más = guerra de precios)
    "precio_min":       15.0,     # precio mínimo para que el margen tenga sentido
    "margen_minimo":    0.15,     # margen bruto mínimo sobre el precio
    "roi_minimo":       0.20,     # ROI mínimo (20%)
    "costo_fba_pct":    0.33,     # estimado de fees FBA + Amazon (~33% del precio)
    "buybox_sellers_ok": 5,       # si hay ≤N sellers en buybox es señal positiva
}

# Pesos del score (deben sumar 100)
PESOS = {
    "bsr":         35,   # qué tan bien se vende
    "sellers":     25,   # qué tan poca competencia hay
    "precio":      20,   # si el precio es estable y tiene margen
    "buybox":      20,   # si el buy box rota entre sellers (vs. Amazon dominando)
}

# ──────────────────────────────────────────
#  FUNCIONES DE SCORING SIN API (modo demo)
# ──────────────────────────────────────────

def score_bsr(bsr: float) -> float:
    """0–100. Sweet spot: 1K–15K. Penaliza extremos."""
    if bsr <= 0:
        return 0
    if bsr < CRITERIOS["bsr_min"]:
        return 30  # demasiado popular, saturado
    if bsr <= 5_000:
        return 100
    if bsr <= 15_000:
        return 85
    if bsr <= 30_000:
        return 65
    if bsr <= CRITERIOS["bsr_max"]:
        return 40
    return 10  # muy lento, no rota

def score_sellers(sellers: int) -> float:
    """0–100. Ideal: 3–7 sellers. Pocos = exclusivo, muchos = guerra."""
    if sellers < CRITERIOS["sellers_min"]:
        return 20
    if sellers <= 4:
        return 100
    if sellers <= 7:
        return 85
    if sellers <= CRITERIOS["sellers_max"]:
        return 55
    return 20

def score_precio(precio: float) -> float:
    """0–100. Precio debe cubrir costos FBA y dejar margen."""
    if precio < CRITERIOS["precio_min"]:
        return 0
    costo_estimado_producto = precio * (1 - CRITERIOS["costo_fba_pct"]) * (1 - CRITERIOS["margen_minimo"])
    margen_real = (precio * (1 - CRITERIOS["costo_fba_pct"]) - costo_estimado_producto) / precio
    if margen_real >= 0.30:
        return 100
    if margen_real >= 0.20:
        return 80
    if margen_real >= CRITERIOS["margen_minimo"]:
        return 60
    return 20

def score_buybox_estimado(sellers: int) -> float:
    """Sin API real, estimamos la rotación del buy box por número de sellers."""
    if sellers == 1:
        return 10   # monopolio, difícil entrar
    if sellers <= CRITERIOS["buybox_sellers_ok"]:
        return 90   # pocos sellers, rotación probable
    if sellers <= 10:
        return 60
    return 25

def calcular_score_total(bsr, sellers, precio) -> dict:
    s_bsr     = score_bsr(bsr)
    s_sellers = score_sellers(sellers)
    s_precio  = score_precio(precio)
    s_buybox  = score_buybox_estimado(sellers)

    total = (
        s_bsr     * PESOS["bsr"]     / 100 +
        s_sellers * PESOS["sellers"] / 100 +
        s_precio  * PESOS["precio"]  / 100 +
        s_buybox  * PESOS["buybox"]  / 100
    )

    return {
        "score_total":   round(total, 1),
        "score_bsr":     round(s_bsr, 1),
        "score_sellers": round(s_sellers, 1),
        "score_precio":  round(s_precio, 1),
        "score_buybox":  round(s_buybox, 1),
    }

def clasificar(score: float) -> tuple[str, str]:
    if score >= 75:
        return "ALTA", "#3ecf8e"
    if score >= 50:
        return "MEDIA", "#f59e0b"
    return "BAJA", "#f87171"

# ──────────────────────────────────────────
#  MODO CON KEEPA API REAL
# ──────────────────────────────────────────

def enriquecer_con_keepa(asins: list[str], api_key: str) -> dict:
    """Consulta Keepa y retorna datos reales de BSR, precio y buy box por ASIN."""
    try:
        import keepa
    except ImportError:
        print("⚠️  Keepa no instalado. Ejecuta: pip install keepa")
        return {}

    print(f"\n🔍 Consultando Keepa para {len(asins)} ASINs...")
    api = keepa.Keepa(api_key)
    productos = api.query(asins, stats=90, buybox=True, history=True)

    datos = {}
    for p in productos:
        asin = p.get("asin", "")
        if not asin:
            continue

        # BSR promedio últimos 90 días
        bsr_hist = p.get("data", {}).get("SALES", [])
        bsr_validos = [x for x in bsr_hist if x and x > 0]
        bsr_promedio = int(sum(bsr_validos) / len(bsr_validos)) if bsr_validos else 0

        # Precio actual (NEW)
        precio_hist = p.get("data", {}).get("NEW", [])
        precios_validos = [x / 100 for x in precio_hist if x and x > 0]
        precio_actual = precios_validos[-1] if precios_validos else 0

        # Sellers en buy box
        stats = p.get("stats", {})
        sellers_buybox = stats.get("buyBoxSellerCount", 0) or 0

        # Estabilidad de precio (desviación estándar)
        if len(precios_validos) > 1:
            media = sum(precios_validos) / len(precios_validos)
            varianza = sum((x - media) ** 2 for x in precios_validos) / len(precios_validos)
            std_precio = math.sqrt(varianza)
            estabilidad_pct = round((std_precio / media) * 100, 1) if media > 0 else 0
        else:
            estabilidad_pct = 0

        datos[asin] = {
            "bsr_promedio_90d":   bsr_promedio,
            "precio_actual":      round(precio_actual, 2),
            "sellers_buybox":     sellers_buybox,
            "estabilidad_precio": estabilidad_pct,  # % de variación (menor = más estable)
        }
        print(f"   ✓ {asin} — BSR: {bsr_promedio:,} | Precio: ${precio_actual:.2f} | Sellers BB: {sellers_buybox}")

    return datos

# ──────────────────────────────────────────
#  LEER CSV DE SMARTSCOUT
# ──────────────────────────────────────────

COLUMN_MAP = {
    # SmartScout puede exportar con distintos nombres de columna
    "asin":     ["ASIN", "asin", "Asin"],
    "brand":    ["Brand", "brand", "Marca"],
    "title":    ["Title", "title", "Product Title", "Título"],
    "bsr":      ["BSR", "bsr", "Best Seller Rank", "Sales Rank"],
    "sellers":  ["Sellers", "sellers", "Seller Count", "# Sellers"],
    "price":    ["Price", "price", "Precio", "Buy Box Price"],
    "revenue":  ["Monthly Revenue", "Revenue", "revenue", "Ingresos"],
    "category": ["Category", "category", "Categoría"],
}

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for campo, posibles in COLUMN_MAP.items():
        for col in posibles:
            if col in df.columns:
                rename[col] = campo
                break
    return df.rename(columns=rename)

def leer_csv(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    df = normalizar_columnas(df)

    columnas_requeridas = ["asin", "bsr", "sellers", "price"]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        print(f"\n❌ El CSV no tiene las columnas requeridas: {faltantes}")
        print(f"   Columnas encontradas: {list(df.columns)}")
        sys.exit(1)

    df["bsr"]     = pd.to_numeric(df["bsr"],     errors="coerce").fillna(0)
    df["sellers"] = pd.to_numeric(df["sellers"], errors="coerce").fillna(0)
    df["price"]   = pd.to_numeric(df["price"],   errors="coerce").fillna(0)
    df["revenue"] = pd.to_numeric(df.get("revenue", pd.Series(dtype=float)), errors="coerce").fillna(0)

    return df

# ──────────────────────────────────────────
#  GENERAR REPORTE HTML
# ──────────────────────────────────────────

def generar_html(df_result: pd.DataFrame, modo: str, output_path: str):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    filas = ""
    for _, row in df_result.iterrows():
        opp, color = clasificar(row["score_total"])
        bsr_fmt = f"{int(row['bsr']):,}" if row['bsr'] > 0 else "—"
        precio_fmt = f"${row['price']:.2f}" if row['price'] > 0 else "—"
        revenue_fmt = f"${int(row.get('revenue', 0)):,}" if row.get('revenue', 0) > 0 else "—"
        brand = row.get("brand", "—")
        title = row.get("title", row["asin"])[:55] + ("…" if len(str(row.get("title", ""))) > 55 else "")

        filas += f"""
        <tr>
          <td><span class="asin">{row['asin']}</span></td>
          <td><strong>{brand}</strong><br><small>{title}</small></td>
          <td>{bsr_fmt}</td>
          <td>{int(row['sellers'])}</td>
          <td>{precio_fmt}</td>
          <td>{revenue_fmt}</td>
          <td>
            <div class="score-bar-wrap">
              <div class="score-bar" style="width:{row['score_total']}%;background:{color}"></div>
            </div>
            <span class="score-num" style="color:{color}">{row['score_total']}</span>
          </td>
          <td><span class="badge" style="background:{color}22;color:{color};border:1px solid {color}44">{opp}</span></td>
          <td>
            <small>BSR {row['score_bsr']} · Sellers {row['score_sellers']} · Precio {row['score_precio']} · BB {row['score_buybox']}</small>
          </td>
        </tr>"""

    altas  = len(df_result[df_result["score_total"] >= 75])
    medias = len(df_result[(df_result["score_total"] >= 50) & (df_result["score_total"] < 75)])
    bajas  = len(df_result[df_result["score_total"] < 50])

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Análisis Wholesale FBA — WL Stonveil LLC</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d0f12; color: #e8eaf0; font-size: 13px; }}
  header {{ background: #141720; border-bottom: 1px solid #252a38; padding: 16px 28px; display: flex; align-items: center; gap: 16px; }}
  .logo {{ width: 32px; height: 32px; background: linear-gradient(135deg,#4a8fff,#a78bfa); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; color: #fff; }}
  h1 {{ font-size: 15px; font-weight: 600; }}
  .sub {{ font-size: 11px; color: #8890a4; margin-top: 2px; }}
  .modo-badge {{ margin-left: auto; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600;
    background: {"rgba(62,207,142,.15)" if modo == "keepa" else "rgba(245,158,11,.15)"};
    color: {"#3ecf8e" if modo == "keepa" else "#f59e0b"};
    border: 1px solid {"#3ecf8e" if modo == "keepa" else "#f59e0b"}; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 24px 28px; }}
  .stats {{ display: flex; gap: 14px; margin-bottom: 24px; }}
  .stat {{ background: #141720; border: 1px solid #252a38; border-radius: 10px; padding: 16px 20px; flex: 1; }}
  .stat-label {{ font-size: 10px; color: #5c6478; text-transform: uppercase; letter-spacing: .6px; margin-bottom: 6px; }}
  .stat-val {{ font-size: 24px; font-weight: 700; }}
  .table-wrap {{ background: #141720; border: 1px solid #252a38; border-radius: 12px; overflow: hidden; }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{ padding: 12px 14px; text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: .6px; color: #5c6478; border-bottom: 1px solid #252a38; white-space: nowrap; }}
  tbody td {{ padding: 12px 14px; border-bottom: 1px solid #1c2030; vertical-align: middle; }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: #191d26; }}
  .asin {{ font-family: monospace; font-size: 11px; color: #4a8fff; }}
  small {{ color: #8890a4; font-size: 11px; }}
  .score-bar-wrap {{ height: 4px; background: #252a38; border-radius: 2px; margin-bottom: 4px; overflow: hidden; }}
  .score-bar {{ height: 100%; border-radius: 2px; }}
  .score-num {{ font-size: 13px; font-weight: 700; }}
  .badge {{ padding: 3px 10px; border-radius: 10px; font-size: 10px; font-weight: 700; }}
  .criteria {{ background: #141720; border: 1px solid #252a38; border-radius: 10px; padding: 16px 20px; margin-bottom: 24px; }}
  .criteria-title {{ font-size: 11px; color: #5c6478; text-transform: uppercase; letter-spacing: .6px; margin-bottom: 10px; }}
  .criteria-grid {{ display: flex; gap: 20px; flex-wrap: wrap; }}
  .crit-item {{ font-size: 12px; color: #8890a4; }}
  .crit-item strong {{ color: #e8eaf0; }}
  footer {{ text-align: center; padding: 20px; color: #5c6478; font-size: 11px; }}
</style>
</head>
<body>
<header>
  <div class="logo">WL</div>
  <div>
    <h1>Análisis de Oportunidades Wholesale FBA</h1>
    <div class="sub">WL Stonveil LLC · Generado el {fecha}</div>
  </div>
  <div class="modo-badge">{'Keepa API (datos reales)' if modo == 'keepa' else 'Modo demo (datos CSV)'}</div>
</header>
<div class="container">

  <div class="stats">
    <div class="stat"><div class="stat-label">Productos analizados</div><div class="stat-val" style="color:#4a8fff">{len(df_result)}</div></div>
    <div class="stat"><div class="stat-label">Oportunidad Alta ≥75</div><div class="stat-val" style="color:#3ecf8e">{altas}</div></div>
    <div class="stat"><div class="stat-label">Oportunidad Media 50–74</div><div class="stat-val" style="color:#f59e0b">{medias}</div></div>
    <div class="stat"><div class="stat-label">Descartar &lt;50</div><div class="stat-val" style="color:#f87171">{bajas}</div></div>
  </div>

  <div class="criteria">
    <div class="criteria-title">Criterios aplicados</div>
    <div class="criteria-grid">
      <div class="crit-item">BSR objetivo: <strong>{CRITERIOS['bsr_min']:,} – {CRITERIOS['bsr_max']:,}</strong></div>
      <div class="crit-item">Sellers: <strong>{CRITERIOS['sellers_min']} – {CRITERIOS['sellers_max']}</strong></div>
      <div class="crit-item">Precio mínimo: <strong>${CRITERIOS['precio_min']}</strong></div>
      <div class="crit-item">Margen mínimo: <strong>{int(CRITERIOS['margen_minimo']*100)}%</strong></div>
      <div class="crit-item">ROI mínimo: <strong>{int(CRITERIOS['roi_minimo']*100)}%</strong></div>
      <div class="crit-item">Fees FBA estimados: <strong>{int(CRITERIOS['costo_fba_pct']*100)}% del precio</strong></div>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>ASIN</th>
          <th>Producto</th>
          <th>BSR</th>
          <th>Sellers</th>
          <th>Precio</th>
          <th>Revenue/mes</th>
          <th>Score</th>
          <th>Oportunidad</th>
          <th>Detalle scores</th>
        </tr>
      </thead>
      <tbody>
        {filas}
      </tbody>
    </table>
  </div>
</div>
<footer>WL Stonveil LLC · Amazon FBA Wholesale · Herramienta interna</footer>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ Reporte generado: {output_path}")

# ──────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analizador Wholesale FBA — WL Stonveil LLC")
    parser.add_argument("--csv",    required=True,  help="Ruta al CSV exportado de SmartScout")
    parser.add_argument("--apikey", default="",     help="API Key de Keepa (opcional, sin ella usa datos del CSV)")
    parser.add_argument("--output", default="",     help="Ruta del reporte HTML de salida")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"❌ No se encontró el archivo: {args.csv}")
        sys.exit(1)

    output_path = args.output or args.csv.replace(".csv", "_reporte.html")

    print(f"\n{'='*55}")
    print("  WL Stonveil LLC — Analizador Wholesale FBA")
    print(f"{'='*55}")
    print(f"  CSV de entrada : {args.csv}")
    print(f"  Keepa API Key  : {'✓ Provista' if args.apikey else '✗ No provista (modo demo)'}")
    print(f"  Reporte salida : {output_path}")
    print(f"{'='*55}\n")

    df = leer_csv(args.csv)
    print(f"📊 {len(df)} productos cargados del CSV")

    modo = "demo"
    if args.apikey:
        asins = df["asin"].tolist()
        datos_keepa = enriquecer_con_keepa(asins, args.apikey)
        if datos_keepa:
            modo = "keepa"
            for asin, datos in datos_keepa.items():
                mask = df["asin"] == asin
                if datos["bsr_promedio_90d"] > 0:
                    df.loc[mask, "bsr"] = datos["bsr_promedio_90d"]
                if datos["precio_actual"] > 0:
                    df.loc[mask, "price"] = datos["precio_actual"]
                if datos["sellers_buybox"] > 0:
                    df.loc[mask, "sellers"] = datos["sellers_buybox"]

    print("\n🧮 Calculando scores...")
    scores = df.apply(
        lambda r: calcular_score_total(r["bsr"], int(r["sellers"]), r["price"]),
        axis=1
    )
    scores_df = pd.DataFrame(scores.tolist())
    df = pd.concat([df, scores_df], axis=1)
    df = df.sort_values("score_total", ascending=False)

    print("\n📋 Resultados:")
    print(f"{'ASIN':<12} {'Brand':<20} {'BSR':>8} {'Sellers':>8} {'Precio':>8} {'Score':>7} {'Oportunidad'}")
    print("-" * 80)
    for _, r in df.iterrows():
        opp, _ = clasificar(r["score_total"])
        brand = str(r.get("brand", "—"))[:18]
        print(f"{r['asin']:<12} {brand:<20} {int(r['bsr']):>8,} {int(r['sellers']):>8} {r['price']:>7.2f}  {r['score_total']:>6.1f}  {opp}")

    generar_html(df, modo, output_path)

if __name__ == "__main__":
    main()
