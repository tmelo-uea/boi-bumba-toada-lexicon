# -*- coding: utf-8 -*-
"""
Step 1 of the lexicon-scoring pipeline: compute token and document frequency
for every core-lexicon term and multi-word phrase, per boi, across the corpus.

INPUT (not included in this repository -- see README section "Reproducing from
raw lyrics"): a JSON file with one record per toada, each containing at least
{"boi": ..., "title": ..., "lyric": <full lyric text>}. This is the same
structure as our internal `catalogo_completo.json`, which is not published here
because it contains full copyrighted lyric text (see paper Section 8). Contact
the authors to request it for research purposes, or substitute your own
similarly-structured corpus.

OUTPUT: freq_v2.json -- token/document frequency per term and per multi-word
phrase, split by boi. This file (already generated) is provided in
`data/analysis_results/` for reference even though the raw-text input is not.

Usage:
    python 01_build_lexicon_frequencies.py --corpus path/to/catalogo_completo.json \
        --cobra-labels ../annotations/cobra/final_adjudicated_labels.json \
        --cobra-occurrences path/to/cobra_occurrences.json \
        --out freq_v2.json
"""
import json, re, csv, argparse
from collections import defaultdict

# ---------------------------------------------------------------
# Multi-word expressions (counted as a single unit, not as the sum of their
# component tokens -- see paper Section 4.1 / Methodology note v2, item 3).
# ---------------------------------------------------------------
PHRASES = {
    'cunha_poranga':   r'cunh[ãa]\s*[-]?\s*poranga',
    'satere_mawe':     r'sater[ée]\s*[-]?\s*maw[ée]',
    'matinta_perera':  r'matinta\s*[-]?\s*perer?[aeê]',
    'cobra_norato':    r'(cobra|homem)[\s-]cobra[\s-]?(norato|honorato)|cobra[\s-](norato|honorato)',
    'vitoria_regia':   r'vit[óo]ria[\s-]r[ée]gia',
    'boto_encantado':  r'(boto\s+encantado|homem[\s-]boto)',
    'maluu_dudu':      r'm[áa]l[úu][ùu]\s*[-]?\s*d[úu]d[úu]',
}

# ---------------------------------------------------------------
# Simple (single-token) terms. Regular Portuguese plurals ("s") are matched
# automatically by count_simple() below; do not add explicit "...s" variants
# here unless the plural is irregular (e.g. ends in -ão), as that would cause
# double counting. See README "Known limitation" note on -ão plurals.
# ---------------------------------------------------------------
SIMPLE_TERMS = {
 'pajé': ['pajé','paje'], 'cunhã': ['cunhã','cunha'], 'poranga': ['poranga'],
 'tuxaua': ['tuxaua'], 'tupã': ['tupã','tupa'], 'curumim': ['curumim'],
 'maracá': ['maracá','maraca'], 'sacaca': ['sacaca'],
 'pajelança': ['pajelança','pajelanca'], 'taba': ['taba'],
 'arumã': ['arumã','aruma'], 'muiraquitã': ['muiraquitã'],
 'igarapé': ['igarapé','igarape'], 'kariwa': ['kariwa','cariua'],
 'curupira': ['curupira'], 'boiúna': ['boiúna','boiuna'],
 'boiaçu': ['boiaçu','boiacu'], 'anhangá': ['anhangá','anhanga'],
 'jurupari': ['jurupari'], 'mapinguari': ['mapinguari'],
 'iara': ['iara','uiara','yara'], 'boitatá': ['boitatá','boitata'],
 'caipora': ['caipora'], 'matinta': ['matinta','matintaperêra'],
 'tupinambá': ['tupinambá','tupinamba'], 'sateré': ['sateré','satere'],
 'mawé': ['mawé','mawe'], 'yanomami': ['yanomami'],
 'parintintin': ['parintintin'], 'mura': ['mura'],
 'igapó': ['igapó','igapo'], 'várzea': ['várzea','varzea'],
 'remanso': ['remanso'], 'barranco': ['barranco'],
 'beiradão': ['beiradão','beiradao'], 'paranã': ['paranã','parana'],
 'furo': ['furo'], 'parintins': ['parintins'],
 'tupinambarana': ['tupinambarana'], 'javari': ['javari'],
 'andirá': ['andirá','andira'], 'xamã': ['xamã','xama'],
 'caboclo': ['caboclo','cabocla'], 'ribeirinho': ['ribeirinho'],
 'seringueiro': ['seringueiro'], 'pescador': ['pescador'],
 'tapuio': ['tapuio'], 'onça': ['onça','onca'], 'jacaré': ['jacaré','jacare'],
 'boto': ['boto'], 'arara': ['arara'], 'sucuri': ['sucuri','sucurijú'],
 'tucano': ['tucano'], 'pirarucu': ['pirarucu'], 'guaraná': ['guaraná','guarana'],
 'açaí': ['açaí','acai'], 'seringueira': ['seringueira'],
 'castanheira': ['castanheira'], 'mandioca': ['mandioca','macaxeira'],
 'tucupi': ['tucupi'], 'farinha': ['farinha'], 'canoa': ['canoa'],
 'maloca': ['maloca','oca'], 'cocar': ['cocar'], 'flecha': ['flecha'],
 'tipiti': ['tipiti'], 'cura': ['cura'], 'espírito': ['espírito','espirito'],
 'ancestral': ['ancestral'], 'encantaria': ['encantaria'],
 'sinhá': ['sinhá','sinha'], 'sinhazinha': ['sinhazinha'],
 'marujada': ['marujada'], 'batucada': ['batucada'], 'arena': ['arena'],
 'toada': ['toada'], 'garrote': ['garrote'], 'vaqueirada': ['vaqueirada'],
 'arquibancada': ['arquibancada'], 'torcedor': ['torcedor'],
 'bumbá': ['bumbá','bumba'], 'galera': ['galera'], 'amo': ['amo'],
 'fazenda': ['fazenda'],
 'amazônia': ['amazônia','amazonia','amazônico','amazonico'],
 'amazonas': ['amazonas'],
}


def norm_txt(s):
    return s.lower()


def find_phrase_spans(text_lower, pattern):
    return [m.span() for m in re.finditer(pattern, text_lower)]


def count_simple(text_lower, variants):
    # Drop variants that are just another variant + "s": count_simple already
    # matches the regular plural automatically, so keeping both would double count.
    base_set = set(variants)
    dedup = [v for v in variants if not (v.endswith('s') and v[:-1] in base_set)]
    total = 0
    for v in dedup:
        pat = r'\b' + re.escape(v) + (r's?' if not v.endswith('s') else '') + r'\b'
        total += len(re.findall(pat, text_lower))
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True, help='catalogo_completo.json (not published; request from authors)')
    ap.add_argument('--cobra-labels', required=True, help='final_adjudicated_labels.json')
    ap.add_argument('--cobra-occurrences', required=True, help='cobra_occurrences.json (context snippets; also not published in full)')
    ap.add_argument('--out', default='freq_v2.json')
    args = ap.parse_args()

    rows = json.load(open(args.corpus, encoding='utf-8'))
    cobra_final = json.load(open(args.cobra_labels, encoding='utf-8'))
    cobra_occ = json.load(open(args.cobra_occurrences, encoding='utf-8'))

    mitica_idxs = {int(k) for k, v in cobra_final.items() if v == 'mitica'}
    cobra_mitica_by_song = defaultdict(int)
    for i in mitica_idxs:
        o = cobra_occ[i]
        cobra_mitica_by_song[(o['boi'], o['title'])] += 1

    token_freq = defaultdict(lambda: {'total': 0, 'Caprichoso': 0, 'Garantido': 0})
    doc_freq = defaultdict(lambda: {'total': 0, 'Caprichoso': 0, 'Garantido': 0})
    phrase_freq = defaultdict(lambda: {'total': 0, 'Caprichoso': 0, 'Garantido': 0})
    phrase_doc_freq = defaultdict(lambda: {'total': 0, 'Caprichoso': 0, 'Garantido': 0})

    for r in rows:
        boi = r['boi']
        text = norm_txt(r['lyric'])
        masked = text

        for pid, pat in PHRASES.items():
            spans = find_phrase_spans(masked, pat)
            cnt = len(spans)
            if cnt > 0:
                phrase_freq[pid]['total'] += cnt
                phrase_freq[pid][boi] += cnt
                phrase_doc_freq[pid]['total'] += 1
                phrase_doc_freq[pid][boi] += 1
                masked = re.sub(pat, ' § ', masked)

        for term, variants in SIMPLE_TERMS.items():
            c = count_simple(masked, variants)
            if c > 0:
                token_freq[term]['total'] += c
                token_freq[term][boi] += c
                doc_freq[term]['total'] += 1
                doc_freq[term][boi] += 1

    json.dump({'token_freq': token_freq, 'doc_freq': doc_freq,
               'phrase_freq': phrase_freq, 'phrase_doc_freq': phrase_doc_freq},
              open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print("=== Multi-word phrases (token_freq / doc_freq) ===")
    for pid in PHRASES:
        print(f"  {pid}: tokens={phrase_freq[pid]['total']} "
              f"(C={phrase_freq[pid]['Caprichoso']},G={phrase_freq[pid]['Garantido']}) "
              f"| docs={phrase_doc_freq[pid]['total']}")

    capr_cobra = sum(v for (b, t), v in cobra_mitica_by_song.items() if b == 'Caprichoso')
    gara_cobra = sum(v for (b, t), v in cobra_mitica_by_song.items() if b == 'Garantido')
    print(f"\ncobra grande (adjudicated mythical): total={capr_cobra + gara_cobra} "
          f"(C={capr_cobra},G={gara_cobra}) | docs={len(cobra_mitica_by_song)}")


if __name__ == '__main__':
    main()
