# -*- coding: utf-8 -*-
"""
Step 3 of the pipeline: compute, per toada, the raw and institutionally-adjusted
core-lexicon ("nucleo") occurrence count and word count. This is the input to
the exploratory temporal (RQ2) and keyness (RQ1) analyses (scripts 04 and 05).

INPUT: catalogo_completo.json (full lyric text; not published, see README) plus
files that ARE published in this repository (annotations/, lexicon data).

Usage:
    python 03_score_songs.py --corpus path/to/catalogo_completo.json \
        --cobra-labels ../annotations/cobra/final_adjudicated_labels.json \
        --cobra-occurrences path/to/cobra_occurrences.json \
        --institutional-labels ../annotations/institutional_confound/chatgpt_labels.csv \
        --out per_song_scores.json
"""
import json, re, csv, unicodedata, argparse
from collections import defaultdict


def norm(s):
    s = unicodedata.normalize('NFD', s.strip().lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


# Core-lexicon ("nucleo") term patterns only -- see data/lexicon_v2.csv for the
# full classification and data/lexicon_methodology.md for why each term is
# core vs. extended/excluded.
NUCLEO_SIMPLE = {
 'pajé': ['pajé', 'paje'], 'cunhã': ['cunhã', 'cunha'], 'poranga': ['poranga'], 'tuxaua': ['tuxaua'],
 'tupã': ['tupã', 'tupa'], 'curumim': ['curumim'], 'maracá': ['maracá', 'maraca'], 'sacaca': ['sacaca'],
 'pajelança': ['pajelança', 'pajelanca'], 'taba': ['taba'], 'arumã': ['arumã', 'aruma'],
 'muiraquitã': ['muiraquitã'], 'igarapé': ['igarapé', 'igarape'], 'kariwa': ['kariwa', 'cariua'],
 'curupira': ['curupira'], 'boiúna': ['boiúna', 'boiuna'], 'boiaçu': ['boiaçu', 'boiacu'],
 'anhangá': ['anhangá', 'anhanga'], 'jurupari': ['jurupari'], 'mapinguari': ['mapinguari'],
 'iara': ['iara', 'uiara', 'yara'], 'boitatá': ['boitatá', 'boitata'], 'caipora': ['caipora'],
 'matinta': ['matinta'], 'tupinambá': ['tupinambá', 'tupinamba'], 'sateré': ['sateré', 'satere'],
 'mawé': ['mawé', 'mawe'], 'yanomami': ['yanomami'], 'parintintin': ['parintintin'], 'mura': ['mura'],
 'igapó': ['igapó', 'igapo'], 'beiradão': ['beiradão', 'beiradao'], 'paranã': ['paranã', 'parana'],
 'tupinambarana': ['tupinambarana'], 'javari': ['javari'], 'andirá': ['andirá', 'andira'],
 'pirarucu': ['pirarucu'], 'tucupi': ['tucupi'], 'tipiti': ['tipiti'],
}
NUCLEO_PHRASES = {
 'cunha_poranga': r'cunh[ãa]\s*[-]?\s*poranga',
 'satere_mawe': r'sater[ée]\s*[-]?\s*maw[ée]',
 'matinta_perera': r'matinta\s*[-]?\s*perer?[aeê]',
 'cobra_norato': r'(cobra|homem)[\s-]cobra[\s-]?(norato|honorato)|cobra[\s-](norato|honorato)',
 'vitoria_regia': r'vit[óo]ria[\s-]r[ée]gia',
 'boto_encantado': r'(boto\s+encantado|homem[\s-]boto)',
}


def count_simple(text_lower, variants):
    base_set = set(variants)
    dedup = [v for v in variants if not (v.endswith('s') and v[:-1] in base_set)]
    total = 0
    for v in dedup:
        pat = r'\b' + re.escape(v) + (r's?' if not v.endswith('s') else '') + r'\b'
        total += len(re.findall(pat, text_lower))
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--cobra-labels', required=True)
    ap.add_argument('--cobra-occurrences', required=True)
    ap.add_argument('--institutional-labels', required=True,
                     help='the disclosed ChatGPT label CSV, e.g. '
                          'annotations/institutional_confound/chatgpt_labels.csv')
    ap.add_argument('--out', default='per_song_scores.json')
    args = ap.parse_args()

    rows = json.load(open(args.corpus, encoding='utf-8'))
    cobra_final = json.load(open(args.cobra_labels, encoding='utf-8'))
    cobra_occ = json.load(open(args.cobra_occurrences, encoding='utf-8'))

    song_label = {}
    with open(args.institutional_labels, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            key = (row['termo'], row['boi'], row['toada'])
            song_label[key] = norm(row['classificacao (preencher)'])

    mitica_idxs = {int(k) for k, v in cobra_final.items() if v == 'mitica'}
    cobra_mitica_by_song = defaultdict(int)
    for i in mitica_idxs:
        o = cobra_occ[i]
        cobra_mitica_by_song[(o['boi'], o['title'])] += 1

    per_song = []
    for r in rows:
        boi, title, year = r['boi'], r['title'], r['year']
        text_lower = r['lyric'].lower()
        word_count = len(re.findall(r'\b\w+\b', text_lower))
        masked = text_lower

        phrase_counts = {}
        for pid, pat in NUCLEO_PHRASES.items():
            spans = list(re.finditer(pat, masked))
            phrase_counts[pid] = len(spans)
            if spans:
                masked = re.sub(pat, ' § ', masked)

        simple_counts = {term: count_simple(masked, variants) for term, variants in NUCLEO_SIMPLE.items()}
        cobra_n = cobra_mitica_by_song.get((boi, title), 0)

        lbl_paje = song_label.get(('pajé', boi, title), 'sem_anotacao')
        lbl_cunha = song_label.get(('cunhã (isolado)', boi, title), 'sem_anotacao')
        lbl_cp = song_label.get(('cunhã-poranga', boi, title), 'sem_anotacao')
        lbl_tux = song_label.get(('tuxaua', boi, title), 'sem_anotacao')

        paje_adj = 0 if lbl_paje == 'institucional' else simple_counts['pajé']
        cunha_adj = 0 if lbl_cunha == 'institucional' else simple_counts['cunhã']
        cp_adj = 0 if lbl_cp == 'institucional' else phrase_counts['cunha_poranga']
        tux_adj = 0 if lbl_tux == 'institucional' else simple_counts['tuxaua']

        nucleo_raw = sum(simple_counts.values()) + sum(phrase_counts.values()) + cobra_n
        nucleo_adj = (nucleo_raw
                      - (simple_counts['pajé'] - paje_adj)
                      - (simple_counts['cunhã'] - cunha_adj)
                      - (phrase_counts['cunha_poranga'] - cp_adj)
                      - (simple_counts['tuxaua'] - tux_adj))

        per_song.append({
            'boi': boi, 'title': title, 'year': int(year) if year else None,
            'word_count': word_count, 'nucleo_raw': nucleo_raw, 'nucleo_adj': nucleo_adj,
            'simple_counts': simple_counts, 'phrase_counts': phrase_counts, 'cobra_mitica': cobra_n,
        })

    json.dump(per_song, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"Total toadas: {len(per_song)}")
    with_year = [p for p in per_song if p['year']]
    print(f"With confirmed year: {len(with_year)}")
    print(f"Sum nucleo_raw: {sum(p['nucleo_raw'] for p in per_song)}")
    print(f"Sum nucleo_adj: {sum(p['nucleo_adj'] for p in per_song)}")


if __name__ == '__main__':
    main()
