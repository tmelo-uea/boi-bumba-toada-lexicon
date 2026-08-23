# -*- coding: utf-8 -*-
"""
Step 5 (RQ1): log-likelihood keyness (Dunning's G2) between Caprichoso and
Garantido for every core-lexicon term, at both token frequency and document
frequency (see paper Section 5.2 and Methodology note v2 for why both are
reported: token frequency can be inflated by within-song chorus repetition).
Institutionally-adjusted counts are used by default for paje/cunha(-poranga)/
tuxaua; --unadjusted retains their raw counts for sensitivity analysis.
Benjamini--Hochberg false-discovery-rate correction is applied
separately to the 46 token-frequency and 46 document-frequency tests.
Produces Table 3 of the paper plus the full rankings as supplementary data.

Usage:
    python 05_keyness_analysis.py --scores per_song_scores.json \
        --institutional-labels ../annotations/institutional_confound/chatgpt_labels.csv \
        --out-token keyness_nucleo_token_freq.csv \
        --out-doc keyness_nucleo_doc_freq.csv
"""
import json, csv, argparse, unicodedata
from collections import defaultdict
import numpy as np
from scipy import stats


def norm(s):
    s = unicodedata.normalize('NFD', s.strip().lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


CONFOUNDED_TERMS = ['pajé', 'cunhã', 'cunha_poranga', 'tuxaua']


def load_institutional_labels(path):
    song_label = {}
    with open(path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            key = (row['termo'], row['boi'], row['toada'])
            song_label[key] = norm(row['classificacao (preencher)'])
    return song_label


def institutionally_adjusted(p, song_label):
    """Return {term: adjusted_count} for the 4 confounded terms in one song."""
    boi, title = p['boi'], p['title']
    lbl_paje = song_label.get(('pajé', boi, title), 'sem_anotacao')
    lbl_cunha = song_label.get(('cunhã (isolado)', boi, title), 'sem_anotacao')
    lbl_cp = song_label.get(('cunhã-poranga', boi, title), 'sem_anotacao')
    lbl_tux = song_label.get(('tuxaua', boi, title), 'sem_anotacao')
    return {
        'pajé': 0 if lbl_paje == 'institucional' else p['simple_counts']['pajé'],
        'cunhã': 0 if lbl_cunha == 'institucional' else p['simple_counts']['cunhã'],
        'cunha_poranga': 0 if lbl_cp == 'institucional' else p['phrase_counts']['cunha_poranga'],
        'tuxaua': 0 if lbl_tux == 'institucional' else p['simple_counts']['tuxaua'],
    }


def log_likelihood_g2(a, b, n1, n2):
    if a + b == 0:
        return 0.0, 1.0, 0
    # Full 2x2 likelihood-ratio test. The complement cells are essential:
    #                term present    term absent
    # Caprichoso          a             n1-a
    # Garantido           b             n2-b
    observed = np.array([[a, n1 - a], [b, n2 - b]], dtype=float)
    expected = np.outer(observed.sum(axis=1), observed.sum(axis=0)) / observed.sum()
    positive = observed > 0
    g2 = 2 * np.sum(observed[positive] * np.log(observed[positive] / expected[positive]))
    # Survival function is numerically stable for very small p-values.
    p_val = stats.chi2.sf(g2, df=1)
    sign = 1 if a / n1 >= b / n2 else -1
    return g2, p_val, sign


def benjamini_hochberg(p_values):
    """Return BH-adjusted q-values in the original input order."""
    m = len(p_values)
    order = sorted(range(m), key=p_values.__getitem__)
    q_values = [1.0] * m
    running_min = 1.0
    for rank, idx in reversed(list(enumerate(order, start=1))):
        running_min = min(running_min, p_values[idx] * m / rank)
        q_values[idx] = running_min
    return q_values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scores', required=True, help='output of 03_score_songs.py')
    ap.add_argument('--institutional-labels', required=True)
    ap.add_argument('--out-token', default='keyness_nucleo_token_freq.csv')
    ap.add_argument('--out-doc', default='keyness_nucleo_doc_freq.csv')
    ap.add_argument('--unadjusted', action='store_true',
                    help='retain institutional uses of paje/cunha(-poranga)/tuxaua')
    args = ap.parse_args()

    per_song = json.load(open(args.scores, encoding='utf-8'))
    song_label = load_institutional_labels(args.institutional_labels)

    # ---- token frequency totals ----
    term_totals = {'Caprichoso': defaultdict(int), 'Garantido': defaultdict(int)}
    doc_freq = {'Caprichoso': defaultdict(int), 'Garantido': defaultdict(int)}
    word_totals = {'Caprichoso': 0, 'Garantido': 0}
    n_songs = {'Caprichoso': 0, 'Garantido': 0}

    for p in per_song:
        boi = p['boi']
        word_totals[boi] += p['word_count']
        n_songs[boi] += 1
        adj = institutionally_adjusted(p, song_label)

        for term, c in p['simple_counts'].items():
            v = adj[term] if term in CONFOUNDED_TERMS and not args.unadjusted else c
            term_totals[boi][term] += v
            if v > 0:
                doc_freq[boi][term] += 1
        for term, c in p['phrase_counts'].items():
            v = adj[term] if term in CONFOUNDED_TERMS and not args.unadjusted else c
            term_totals[boi][term] += v
            if v > 0:
                doc_freq[boi][term] += 1
        term_totals[boi]['cobra_grande'] += p['cobra_mitica']
        if p['cobra_mitica'] > 0:
            doc_freq[boi]['cobra_grande'] += 1

    # ---- token-frequency keyness ----
    N1, N2 = word_totals['Caprichoso'], word_totals['Garantido']
    all_terms = sorted(set(term_totals['Caprichoso']) | set(term_totals['Garantido']))
    tok_results = []
    for term in all_terms:
        a, b = term_totals['Caprichoso'].get(term, 0), term_totals['Garantido'].get(term, 0)
        if a + b == 0:
            continue
        g2, p_val, sign = log_likelihood_g2(a, b, N1, N2)
        tok_results.append((term, a, b, a / N1 * 1000, b / N2 * 1000, g2, p_val, sign))
    tok_results.sort(key=lambda r: -r[5])
    tok_q = benjamini_hochberg([r[6] for r in tok_results])

    with open(args.out_token, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['termo', 'freq_caprichoso', 'freq_garantido', 'norm_capr_per1000w',
                    'norm_gara_per1000w', 'G2', 'p_value', 'q_value_bh', 'mais_associado'])
        for r, q in zip(tok_results, tok_q):
            w.writerow([r[0], r[1], r[2], round(r[3], 4), round(r[4], 4), round(r[5], 3),
                        f'{r[6]:.10g}', f'{q:.10g}',
                        'Caprichoso' if r[7] > 0 else 'Garantido'])

    n_sig_tok = sum(1 for r in tok_results if r[6] < 0.05)
    n_fdr_tok = sum(1 for q in tok_q if q < 0.05)
    print(f"Words (N): Caprichoso={N1}, Garantido={N2}")
    print(f"Token-frequency: {n_sig_tok}/{len(tok_results)} terms nominally significant (p<0.05, uncorrected)")
    print(f"Token-frequency: {n_fdr_tok}/{len(tok_results)} terms significant after BH FDR (q<0.05)")

    # ---- document-frequency keyness ----
    Nd1, Nd2 = n_songs['Caprichoso'], n_songs['Garantido']
    doc_results = []
    for term in all_terms:
        a, b = doc_freq['Caprichoso'].get(term, 0), doc_freq['Garantido'].get(term, 0)
        if a + b == 0:
            continue
        g2, p_val, sign = log_likelihood_g2(a, b, Nd1, Nd2)
        doc_results.append((term, a, b, a / Nd1 * 100, b / Nd2 * 100, g2, p_val, sign))
    doc_results.sort(key=lambda r: -r[5])
    doc_q = benjamini_hochberg([r[6] for r in doc_results])

    with open(args.out_doc, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['termo', 'n_toadas_caprichoso', 'n_toadas_garantido', 'pct_toadas_caprichoso',
                    'pct_toadas_garantido', 'G2', 'p_value', 'q_value_bh', 'mais_associado'])
        for r, q in zip(doc_results, doc_q):
            w.writerow([r[0], r[1], r[2], round(r[3], 3), round(r[4], 3), round(r[5], 3),
                        f'{r[6]:.10g}', f'{q:.10g}',
                        'Caprichoso' if r[7] > 0 else 'Garantido'])

    n_sig_doc = sum(1 for r in doc_results if r[6] < 0.05)
    n_fdr_doc = sum(1 for q in doc_q if q < 0.05)
    print(f"Songs (N): Caprichoso={Nd1}, Garantido={Nd2}")
    print(f"Document-frequency: {n_sig_doc}/{len(doc_results)} terms nominally significant (p<0.05, uncorrected)")
    print(f"Document-frequency: {n_fdr_doc}/{len(doc_results)} terms significant after BH FDR (q<0.05)")

    tok_sig = {r[0] for r, q in zip(tok_results, tok_q) if q < 0.05}
    doc_sig = {r[0] for r, q in zip(doc_results, doc_q) if q < 0.05}
    print(f"\nBH-significant under BOTH tests: {sorted(tok_sig & doc_sig)}")


if __name__ == '__main__':
    main()
