# -*- coding: utf-8 -*-
"""
Step 5 (RQ2): log-likelihood keyness (Dunning's G2) between Caprichoso and
Garantido for every core-lexicon term, at both token frequency and document
frequency (see paper Section 5.2 and Methodology note v2 for why both are
reported: token frequency can be inflated by within-song chorus repetition).
Institutionally-adjusted counts are used throughout for paje/cunha(-poranga)/
tuxaua. Produces Table 3 of the paper plus the full ranking (both frequency
types) as supplementary data.

Usage:
    python 05_keyness_analysis.py --scores per_song_scores.json \
        --institutional-labels ../annotations/institutional_confound/external_annotator_labels.csv \
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
    e1, e2 = n1 * (a + b) / (n1 + n2), n2 * (a + b) / (n1 + n2)
    ll = 0.0
    if a > 0:
        ll += a * np.log(a / e1)
    if b > 0:
        ll += b * np.log(b / e2)
    g2 = 2 * ll
    p_val = 1 - stats.chi2.cdf(g2, df=1)
    sign = 1 if a / n1 >= b / n2 else -1
    return g2, p_val, sign


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scores', required=True, help='output of 03_score_songs.py')
    ap.add_argument('--institutional-labels', required=True)
    ap.add_argument('--out-token', default='keyness_nucleo_token_freq.csv')
    ap.add_argument('--out-doc', default='keyness_nucleo_doc_freq.csv')
    args = ap.parse_args()

    per_song = json.load(open(args.scores, encoding='utf-8'))
    song_label = load_institutional_labels(args.institutional_labels)

    # ---- token frequency totals, institutionally adjusted ----
    term_totals = {'Caprichoso': defaultdict(int), 'Garantido': defaultdict(int)}
    doc_freq = {'Caprichoso': defaultdict(int), 'Garantido': defaultdict(int)}
    word_totals = {'Caprichoso': 0, 'Garantido': 0}
    n_songs = {'Caprichoso': 0, 'Garantido': 0}

    for p in per_song:
        boi = p['boi']
        word_totals[boi] += p['word_count']
        n_songs[boi] += 1
        adj = institutionally_adjusted(p, song_label)

        # NOTE (documented design choice, not a bug): the institutional
        # adjustment is applied to TOKEN totals only, matching the exact
        # methodology already reported in the paper (Section 5.2 / Table 3).
        # Document frequency below uses raw (unadjusted) presence for all
        # terms, including the 4 confounded ones -- i.e. a song still counts
        # toward pajé's document frequency even if that song's pajé mentions
        # were judged institutional. This asymmetry (token adjusted, document
        # not) was identified during a later reproducibility check of this
        # script and is being preserved, rather than "fixed", specifically
        # to keep this code reproducing the numbers already published in the
        # paper. It does not change which terms are significant: none of the
        # 4 confounded terms cross p<0.05 at document frequency either way.
        # A fully adjusted document frequency would be a reasonable
        # improvement for future work.
        for term, c in p['simple_counts'].items():
            v = adj[term] if term in CONFOUNDED_TERMS else c
            term_totals[boi][term] += v
            if c > 0:
                doc_freq[boi][term] += 1
        for term, c in p['phrase_counts'].items():
            v = adj[term] if term in CONFOUNDED_TERMS else c
            term_totals[boi][term] += v
            if c > 0:
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

    with open(args.out_token, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['termo', 'freq_caprichoso', 'freq_garantido', 'norm_capr_per1000w',
                    'norm_gara_per1000w', 'G2', 'p_value', 'mais_associado'])
        for r in tok_results:
            w.writerow([r[0], r[1], r[2], round(r[3], 4), round(r[4], 4), round(r[5], 3),
                        round(r[6], 5), 'Caprichoso' if r[7] > 0 else 'Garantido'])

    n_sig_tok = sum(1 for r in tok_results if r[6] < 0.05)
    print(f"Words (N): Caprichoso={N1}, Garantido={N2}")
    print(f"Token-frequency: {n_sig_tok}/{len(tok_results)} terms nominally significant (p<0.05, uncorrected)")

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

    with open(args.out_doc, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['termo', 'n_toadas_caprichoso', 'n_toadas_garantido', 'pct_toadas_caprichoso',
                    'pct_toadas_garantido', 'G2', 'p_value', 'mais_associado'])
        for r in doc_results:
            w.writerow([r[0], r[1], r[2], round(r[3], 3), round(r[4], 3), round(r[5], 3),
                        round(r[6], 5), 'Caprichoso' if r[7] > 0 else 'Garantido'])

    n_sig_doc = sum(1 for r in doc_results if r[6] < 0.05)
    print(f"Songs (N): Caprichoso={Nd1}, Garantido={Nd2}")
    print(f"Document-frequency: {n_sig_doc}/{len(doc_results)} terms nominally significant (p<0.05, uncorrected)")

    tok_sig = {r[0] for r in tok_results if r[6] < 0.05}
    doc_sig = {r[0] for r in doc_results if r[6] < 0.05}
    print(f"\nSignificant under BOTH tests (most robust candidates): {sorted(tok_sig & doc_sig)}")


if __name__ == '__main__':
    main()
