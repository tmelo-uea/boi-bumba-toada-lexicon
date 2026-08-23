# -*- coding: utf-8 -*-
"""
Step 4 (exploratory RQ2): temporal-pattern analysis. Computes core-lexicon
density by boi and decade and a per-toada linear regression of density on
album year. Produces Table 2 of the paper.

Usage:
    python 04_temporal_analysis.py --scores per_song_scores.json \
        --out-density density_by_decade.csv --out-trend trend_results.json
"""
import json, csv, argparse
import numpy as np
from scipy import stats
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument('--scores', required=True, help='output of 03_score_songs.py')
ap.add_argument('--out-density', default='density_by_decade.csv')
ap.add_argument('--out-trend', default='trend_results.json')
args = ap.parse_args()

per_song = json.load(open(args.scores, encoding='utf-8'))

with_year = [p for p in per_song if p['year'] and 1989 <= p['year'] <= 2026]
print(f"N com ano valido: {len(with_year)}")

# ---------------------------------------------------------------
# 1. Densidade por boi (nucleo por 1000 palavras), raw vs ajustado
# ---------------------------------------------------------------
def density_stats(items, key):
    wc = sum(p['word_count'] for p in items)
    nc = sum(p[key] for p in items)
    return nc / wc * 1000 if wc else 0, nc, wc, len(items)

print("\n=== Densidade global (nucleo por 1000 palavras) ===")
for boi in ['Caprichoso', 'Garantido']:
    items = [p for p in with_year if p['boi'] == boi]
    d_raw, nc_raw, wc, n = density_stats(items, 'nucleo_raw')
    d_adj, nc_adj, _, _ = density_stats(items, 'nucleo_adj')
    print(f"  {boi}: raw={d_raw:.2f}/1000w (n_hits={nc_raw}, n_songs={n}, words={wc}) | ajustado={d_adj:.2f}/1000w (n_hits={nc_adj})")

# ---------------------------------------------------------------
# 2. Por decada
# ---------------------------------------------------------------
def decade(y):
    return (y // 10) * 10

print("\n=== Densidade por decada e boi (ajustado) ===")
decade_data = defaultdict(list)
for p in with_year:
    decade_data[(p['boi'], decade(p['year']))].append(p)

decades = sorted(set(decade(p['year']) for p in with_year))
rows_table = []
for boi in ['Caprichoso', 'Garantido']:
    for d in decades:
        items = decade_data.get((boi, d), [])
        if not items:
            continue
        d_raw, nc_raw, wc, n = density_stats(items, 'nucleo_raw')
        d_adj, nc_adj, _, _ = density_stats(items, 'nucleo_adj')
        print(f"  {boi} {d}s: n={n} songs, raw={d_raw:.2f}/1000w, ajustado={d_adj:.2f}/1000w")
        rows_table.append([boi, d, n, wc, nc_raw, round(d_raw,3), nc_adj, round(d_adj,3)])

with open(args.out_density, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['boi','decada','n_toadas','n_palavras','nucleo_raw_hits','densidade_raw_por_1000w',
                'nucleo_adj_hits','densidade_adj_por_1000w'])
    w.writerows(rows_table)

# ---------------------------------------------------------------
# 3. Teste de tendencia temporal (regressao linear ano -> densidade por musica, por boi)
#    Usamos densidade por musica (nucleo_adj / word_count * 1000) como variavel dependente
# ---------------------------------------------------------------
print("\n=== Tendencia temporal (regressao linear: ano -> densidade ajustada por musica) ===")
trend_results = {}
for boi in ['Caprichoso', 'Garantido']:
    items = [p for p in with_year if p['boi'] == boi and p['word_count'] > 0]
    years = np.array([p['year'] for p in items])
    dens = np.array([p['nucleo_adj'] / p['word_count'] * 1000 for p in items])
    slope, intercept, r, pval, se = stats.linregress(years, dens)
    trend_results[boi] = {'slope': slope, 'r': r, 'p': pval, 'n': len(items)}
    direction = 'aumento' if slope > 0 else 'queda'
    sig = 'SIGNIFICATIVO' if pval < 0.05 else 'nao significativo'
    print(f"  {boi}: slope={slope:+.4f} pontos/ano ({direction}), r={r:.3f}, p={pval:.4f} [{sig}], n={len(items)}")

json.dump(trend_results, open(args.out_trend, 'w', encoding='utf-8'), indent=1)
print(f"\nSaved: {args.out_density}, {args.out_trend}")
