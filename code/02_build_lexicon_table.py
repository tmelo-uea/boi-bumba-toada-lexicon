# -*- coding: utf-8 -*-
"""
Step 2 of the lexicon-scoring pipeline: assign every candidate term to its
final two-axis classification (etymological origin x semantic domain) and
tier (core/extended/excluded/toponymic-control/afro-identity), and merge in
the frequencies computed by 01_build_lexicon_frequencies.py. This is where
the curatorial decisions described in the paper (Methodology section, and
data/lexicon_methodology.md) are made explicit and machine-readable.

Usage:
    python 02_build_lexicon_table.py --freq freq_v2.json \
        --cobra-mitica-by-song cobra_mitica_by_song.json \
        --out lexicon_v2.csv
"""
import json, csv, argparse

ap = argparse.ArgumentParser()
ap.add_argument('--freq', required=True, help='output of 01_build_lexicon_frequencies.py')
ap.add_argument('--cobra-mitica-by-song', required=True,
                help='JSON mapping "Boi|||Toada" -> count of adjudicated-mythical cobra occurrences')
ap.add_argument('--out', default='lexicon_v2.csv')
args = ap.parse_args()

d = json.load(open(args.freq, encoding='utf-8'))
tf, df, pf, pdf = d['token_freq'], d['doc_freq'], d['phrase_freq'], d['phrase_doc_freq']

cobra_mit = json.load(open(args.cobra_mitica_by_song, encoding='utf-8'))
cobra_docs = len(cobra_mit)
cobra_tok_c = sum(v for k, v in cobra_mit.items() if k.startswith('Caprichoso|||'))
cobra_tok_g = sum(v for k, v in cobra_mit.items() if k.startswith('Garantido|||'))
cobra_doc_c = sum(1 for k in cobra_mit if k.startswith('Caprichoso|||'))
cobra_doc_g = sum(1 for k in cobra_mit if k.startswith('Garantido|||'))

def T(term):
    return tf.get(term, {'total':0,'Caprichoso':0,'Garantido':0})
def D(term):
    return df.get(term, {'total':0,'Caprichoso':0,'Garantido':0})
def P(pid):
    return pf.get(pid, {'total':0,'Caprichoso':0,'Garantido':0})
def PD(pid):
    return pdf.get(pid, {'total':0,'Caprichoso':0,'Garantido':0})

# cada linha: forma, variantes, origem_etim, estatuto_ref, dominio, tier, subtipo_entidade,
#             (freq_tok_tot, freq_tok_c, freq_tok_g), (freq_doc_tot, freq_doc_c, freq_doc_g), nota
rows = []

def add(forma, variantes, origem, estatuto, dominio, tier, subtipo, tok, doc, nota):
    rows.append([forma, variantes, origem, estatuto, dominio, tier, subtipo,
                 tok[0], tok[1], tok[2], doc[0], doc[1], doc[2], nota])

# ---- NUCLEO: lexico indigena Tupi-Nheengatu ----
add('pajé','pajé;paje','Tupi/Nheengatu','lexema comum / item oficial do Festival','Ritual, cura e cosmologia','nucleo','',
    (T('pajé')['total'],T('pajé')['Caprichoso'],T('pajé')['Garantido']),
    (D('pajé')['total'],D('pajé')['Caprichoso'],D('pajé')['Garantido']),
    'CONFUNDIDOR INSTITUCIONAL: tambem item oficial avaliado no Festival; nao segregado automaticamente (ver limitacoes)')

add('cunhã (isolado)','cunhã;cunha','Tupi/Nheengatu','lexema comum / item oficial quando parte de Cunhã-Poranga','Personagens, identidades e papéis sociais','nucleo','',
    (T('cunhã')['total'],T('cunhã')['Caprichoso'],T('cunhã')['Garantido']),
    (D('cunhã')['total'],D('cunhã')['Caprichoso'],D('cunhã')['Garantido']),
    'excluidas ocorrencias que fazem parte de "cunhã-poranga" (contadas separadamente como unidade)')

add('cunhã-poranga (unidade)','cunhã-poranga;cunha poranga','Tupi/Nheengatu','expressão multipalavra / item oficial do Festival','Personagens, identidades e papéis sociais','nucleo','',
    (P('cunha_poranga')['total'],P('cunha_poranga')['Caprichoso'],P('cunha_poranga')['Garantido']),
    (PD('cunha_poranga')['total'],PD('cunha_poranga')['Caprichoso'],PD('cunha_poranga')['Garantido']),
    'CONFUNDIDOR INSTITUCIONAL: item oficial avaliado no Festival')

add('poranga (isolado)','poranga','Tupi/Nheengatu','lexema comum / qualificativo','Personagens, identidades e papéis sociais','nucleo','',
    (T('poranga')['total'],T('poranga')['Caprichoso'],T('poranga')['Garantido']),
    (D('poranga')['total'],D('poranga')['Caprichoso'],D('poranga')['Garantido']),
    'excluidas ocorrencias de "cunhã-poranga" (contadas separadamente)')

add('tuxaua','tuxaua','Tupi/Nheengatu','lexema comum / item oficial coletivo ("Tuxauas")','Personagens, identidades e papéis sociais','nucleo','',
    (T('tuxaua')['total'],T('tuxaua')['Caprichoso'],T('tuxaua')['Garantido']),
    (D('tuxaua')['total'],D('tuxaua')['Caprichoso'],D('tuxaua')['Garantido']),
    'CONFUNDIDOR INSTITUCIONAL: "Tuxauas" e item oficial coletivo do Festival')

add('tupã','tupã;tupa','Tupi/Nheengatu','entidade nomeada','Ritual, cura e cosmologia','nucleo','divindade / ser cosmológico',
    (T('tupã')['total'],T('tupã')['Caprichoso'],T('tupã')['Garantido']),
    (D('tupã')['total'],D('tupã')['Caprichoso'],D('tupã')['Garantido']),
    'nao generalizar como divindade comum a todos os povos indigenas')

add('curumim','curumim','Tupi/Nheengatu','lexema comum','Personagens, identidades e papéis sociais','nucleo','',
    (T('curumim')['total'],T('curumim')['Caprichoso'],T('curumim')['Garantido']),
    (D('curumim')['total'],D('curumim')['Caprichoso'],D('curumim')['Garantido']), '')

add('maracá','maracá;maraca','Tupi/Nheengatu','lexema comum','Cultura material e artefatos / Ritual, cura e cosmologia','nucleo','',
    (T('maracá')['total'],T('maracá')['Caprichoso'],T('maracá')['Garantido']),
    (D('maracá')['total'],D('maracá')['Caprichoso'],D('maracá')['Garantido']),
    'multirrotulo: artefato + funcao ritual')

add('sacaca','sacaca','Tupi/Nheengatu','lexema comum','Ritual, cura e cosmologia','nucleo','',
    (T('sacaca')['total'],T('sacaca')['Caprichoso'],T('sacaca')['Garantido']),
    (D('sacaca')['total'],D('sacaca')['Caprichoso'],D('sacaca')['Garantido']), '')

add('pajelança','pajelança;pajelanca','Tupi/Nheengatu','lexema comum','Ritual, cura e cosmologia','nucleo','',
    (T('pajelança')['total'],T('pajelança')['Caprichoso'],T('pajelança')['Garantido']),
    (D('pajelança')['total'],D('pajelança')['Caprichoso'],D('pajelança')['Garantido']), '')

add('taba','taba','Tupi/Nheengatu','lexema comum','Paisagem, território, assentamento e organização social','nucleo','',
    (T('taba')['total'],T('taba')['Caprichoso'],T('taba')['Garantido']),
    (D('taba')['total'],D('taba')['Caprichoso'],D('taba')['Garantido']),
    'reclassificado de "cultura material" (taba = assentamento, nao artefato)')

add('arumã','arumã;aruma','Tupi/Nheengatu','lexema comum','Flora','nucleo','',
    (T('arumã')['total'],T('arumã')['Caprichoso'],T('arumã')['Garantido']),
    (D('arumã')['total'],D('arumã')['Caprichoso'],D('arumã')['Garantido']), '')

add('muiraquitã','muiraquitã','Tupi/Nheengatu','lexema comum','Cultura material e artefatos','nucleo','',
    (T('muiraquitã')['total'],T('muiraquitã')['Caprichoso'],T('muiraquitã')['Garantido']),
    (D('muiraquitã')['total'],D('muiraquitã')['Caprichoso'],D('muiraquitã')['Garantido']), '')

add('igarapé','igarapé;igarape','Tupi/Nheengatu','lexema comum','Paisagem, ecossistemas e hidrografia','nucleo','',
    (T('igarapé')['total'],T('igarapé')['Caprichoso'],T('igarapé')['Garantido']),
    (D('igarapé')['total'],D('igarapé')['Caprichoso'],D('igarapé')['Garantido']), '')

add('kariwa','kariwa;cariua','Tupi/Nheengatu','lexema comum','Personagens, identidades e papéis sociais','nucleo','',
    (T('kariwa')['total'],T('kariwa')['Caprichoso'],T('kariwa')['Garantido']),
    (D('kariwa')['total'],D('kariwa')['Caprichoso'],D('kariwa')['Garantido']), '')

# ---- NUCLEO: mitologia (com origem corrigida p/ Tupi/Nheengatu onde aplicavel) ----
add('curupira','curupira','Tupi/Nheengatu','entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (T('curupira')['total'],T('curupira')['Caprichoso'],T('curupira')['Garantido']),
    (D('curupira')['total'],D('curupira')['Caprichoso'],D('curupira')['Garantido']),
    'origem corrigida de "portugues regionalizado" para Tupi/Nheengatu')

add('boiúna','boiúna;boiuna','Tupi/Nheengatu','entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (T('boiúna')['total'],T('boiúna')['Caprichoso'],T('boiúna')['Garantido']),
    (D('boiúna')['total'],D('boiúna')['Caprichoso'],D('boiúna')['Garantido']),
    'origem corrigida para Tupi/Nheengatu; sinonimo de cobra grande, mas mantido como forma canonica distinta')

add('boiaçu','boiaçu;boiacu','Tupi/Nheengatu','entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (T('boiaçu')['total'],T('boiaçu')['Caprichoso'],T('boiaçu')['Garantido']),
    (D('boiaçu')['total'],D('boiaçu')['Caprichoso'],D('boiaçu')['Garantido']),
    'origem corrigida para Tupi/Nheengatu')

add('cobra grande (mítica, adjudicada)','cobra;cobras;cobra grande;cobra-grande','Português regionalizado amazônico','entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (cobra_tok_c+cobra_tok_g, cobra_tok_c, cobra_tok_g),
    (cobra_docs, cobra_doc_c, cobra_doc_g),
    'contagem = apenas ocorrencias de "cobra" classificadas como miticas apos dupla-anotacao cega + adjudicacao (kappa=0.136 bruto; 91.2% concordancia pos-adjudicacao). Ver cobra_final_labels.json')

add('anhangá','anhangá;anhanga','Tupi/Nheengatu','entidade nomeada','Ritual, cura e cosmologia','nucleo','espírito / força cosmológica',
    (T('anhangá')['total'],T('anhangá')['Caprichoso'],T('anhangá')['Garantido']),
    (D('anhangá')['total'],D('anhangá')['Caprichoso'],D('anhangá')['Garantido']), '')

add('jurupari','jurupari','Tupi/Nheengatu','entidade nomeada','Ritual, cura e cosmologia / Entidades míticas','nucleo','contextual: entidade/ancestral/complexo ritual (nao resolvido por toada)',
    (T('jurupari')['total'],T('jurupari')['Caprichoso'],T('jurupari')['Garantido']),
    (D('jurupari')['total'],D('jurupari')['Caprichoso'],D('jurupari')['Garantido']),
    'polissemico; anotacao contextual completa fica para trabalho futuro (fora do escopo do prazo)')

add('mapinguari','mapinguari','indígena (etimologia a confirmar)','entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (T('mapinguari')['total'],T('mapinguari')['Caprichoso'],T('mapinguari')['Garantido']),
    (D('mapinguari')['total'],D('mapinguari')['Caprichoso'],D('mapinguari')['Garantido']),
    'origem etimologica precisa nao confirmada em fonte especifica')

add('iara','iara;uiara;yara','Tupi/Nheengatu','entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (T('iara')['total'],T('iara')['Caprichoso'],T('iara')['Garantido']),
    (D('iara')['total'],D('iara')['Caprichoso'],D('iara')['Garantido']), '')

add('boitatá','boitatá;boitata','Tupi/Nheengatu','entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (T('boitatá')['total'],T('boitatá')['Caprichoso'],T('boitatá')['Garantido']),
    (D('boitatá')['total'],D('boitatá')['Caprichoso'],D('boitatá')['Garantido']), '')

add('caipora','caipora','Tupi/Nheengatu','entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (T('caipora')['total'],T('caipora')['Caprichoso'],T('caipora')['Garantido']),
    (D('caipora')['total'],D('caipora')['Caprichoso'],D('caipora')['Garantido']), '')

add('matinta perera (unidade)','matinta perera;matinta-pereira;matintaperêra','Português regionalizado amazônico','expressão multipalavra / entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (P('matinta_perera')['total'],P('matinta_perera')['Caprichoso'],P('matinta_perera')['Garantido']),
    (PD('matinta_perera')['total'],PD('matinta_perera')['Caprichoso'],PD('matinta_perera')['Garantido']), '')

add('matinta (isolado)','matinta','Português regionalizado amazônico','lexema comum','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (T('matinta')['total'],T('matinta')['Caprichoso'],T('matinta')['Garantido']),
    (D('matinta')['total'],D('matinta')['Caprichoso'],D('matinta')['Garantido']),
    'excluidas ocorrencias de "matinta perera" (contadas separadamente)')

add('cobra norato/honorato (unidade)','cobra norato;cobra honorato;homem-cobra honorato','Português regionalizado amazônico','expressão multipalavra / entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (P('cobra_norato')['total'],P('cobra_norato')['Caprichoso'],P('cobra_norato')['Garantido']),
    (PD('cobra_norato')['total'],PD('cobra_norato')['Caprichoso'],PD('cobra_norato')['Garantido']),
    'lenda especifica, distinta de cobra grande generica')

# ---- NUCLEO: etnonimos ----
add('tupinambá','tupinambá;tupinamba','Etnônimo','etnônimo','Povos e etnônimos','nucleo','',
    (T('tupinambá')['total'],T('tupinambá')['Caprichoso'],T('tupinambá')['Garantido']),
    (D('tupinambá')['total'],D('tupinambá')['Caprichoso'],D('tupinambá')['Garantido']), '')

add('sateré (isolado)','sateré;satere','Etnônimo','etnônimo','Povos e etnônimos','nucleo','',
    (T('sateré')['total'],T('sateré')['Caprichoso'],T('sateré')['Garantido']),
    (D('sateré')['total'],D('sateré')['Caprichoso'],D('sateré')['Garantido']),
    'excluidas ocorrencias de "Sateré-Mawé" (contadas separadamente como unidade)')

add('mawé (isolado)','mawé;mawe','Etnônimo','etnônimo','Povos e etnônimos','nucleo','',
    (T('mawé')['total'],T('mawé')['Caprichoso'],T('mawé')['Garantido']),
    (D('mawé')['total'],D('mawé')['Caprichoso'],D('mawé')['Garantido']),
    'excluidas ocorrencias de "Sateré-Mawé" (contadas separadamente)')

add('sateré-mawé (unidade)','sateré-mawé;satere mawe','Etnônimo','expressão multipalavra / etnônimo','Povos e etnônimos','nucleo','',
    (P('satere_mawe')['total'],P('satere_mawe')['Caprichoso'],P('satere_mawe')['Garantido']),
    (PD('satere_mawe')['total'],PD('satere_mawe')['Caprichoso'],PD('satere_mawe')['Garantido']), '')

add('yanomami','yanomami','Etnônimo','etnônimo','Povos e etnônimos','nucleo','',
    (T('yanomami')['total'],T('yanomami')['Caprichoso'],T('yanomami')['Garantido']),
    (D('yanomami')['total'],D('yanomami')['Caprichoso'],D('yanomami')['Garantido']), '')

add('parintintin','parintintin','Etnônimo','etnônimo','Povos e etnônimos','nucleo','',
    (T('parintintin')['total'],T('parintintin')['Caprichoso'],T('parintintin')['Garantido']),
    (D('parintintin')['total'],D('parintintin')['Caprichoso'],D('parintintin')['Garantido']),
    'CUIDADO: distinto de "parintins" (toponimo) - correspondencia exata de palavra, sem stemming')

add('mura','mura','Etnônimo','etnônimo (validação contextual)','Povos e etnônimos','nucleo','',
    (T('mura')['total'],T('mura')['Caprichoso'],T('mura')['Garantido']),
    (D('mura')['total'],D('mura')['Caprichoso'],D('mura')['Garantido']),
    'validacao contextual completa nao realizada (fora do escopo do prazo)')

# ---- NUCLEO: paisagem/hidrografia/toponimia ----
add('igapó','igapó;igapo','Tupi/Nheengatu','lexema comum','Paisagem, ecossistemas e hidrografia','nucleo','',
    (T('igapó')['total'],T('igapó')['Caprichoso'],T('igapó')['Garantido']),
    (D('igapó')['total'],D('igapó')['Caprichoso'],D('igapó')['Garantido']),
    'origem corrigida para Tupi/Nheengatu')

add('beiradão','beiradão;beiradao','Português regionalizado amazônico','lexema comum','Paisagem, ecossistemas e hidrografia','nucleo','',
    (T('beiradão')['total'],T('beiradão')['Caprichoso'],T('beiradão')['Garantido']),
    (D('beiradão')['total'],D('beiradão')['Caprichoso'],D('beiradão')['Garantido']),
    'mais marcado regionalmente que barranco/remanso; nucleo condicional a uso ribeirinho')

add('paranã','paranã;parana','Tupi/Nheengatu','lexema comum','Paisagem, ecossistemas e hidrografia','nucleo','',
    (T('paranã')['total'],T('paranã')['Caprichoso'],T('paranã')['Garantido']),
    (D('paranã')['total'],D('paranã')['Caprichoso'],D('paranã')['Garantido']), '')

add('tupinambarana','tupinambarana','Topônimo','topônimo','Toponímia e hidronímia','nucleo','',
    (T('tupinambarana')['total'],T('tupinambarana')['Caprichoso'],T('tupinambarana')['Garantido']),
    (D('tupinambarana')['total'],D('tupinambarana')['Caprichoso'],D('tupinambarana')['Garantido']), '')

add('javari','javari','Topônimo','topônimo (validação contextual)','Toponímia e hidronímia','nucleo','',
    (T('javari')['total'],T('javari')['Caprichoso'],T('javari')['Garantido']),
    (D('javari')['total'],D('javari')['Caprichoso'],D('javari')['Garantido']),
    'validacao contextual completa nao realizada (fora do escopo do prazo)')

add('andirá','andirá;andira','Topônimo','topônimo (validação contextual)','Toponímia e hidronímia','nucleo','',
    (T('andirá')['total'],T('andirá')['Caprichoso'],T('andirá')['Garantido']),
    (D('andirá')['total'],D('andirá')['Caprichoso'],D('andirá')['Garantido']),
    'pode ser rio, territorio ou parte de outro nome proprio; validacao contextual completa fora do escopo')

add('vitória-régia (unidade)','vitória-régia;vitoria regia','Português (denominação regional)','expressão multipalavra','Flora / Entidades míticas (conforme contexto)','nucleo','',
    (P('vitoria_regia')['total'],P('vitoria_regia')['Caprichoso'],P('vitoria_regia')['Garantido']),
    (PD('vitoria_regia')['total'],PD('vitoria_regia')['Caprichoso'],PD('vitoria_regia')['Garantido']),
    'movido de ampliado para nucleo; forma canonica corrigida para "vitoria-regia"; pode ser flora ou referencia a lenda')

add('pirarucu','pirarucu','Tupi/Nheengatu','lexema comum','Fauna','nucleo','',
    (T('pirarucu')['total'],T('pirarucu')['Caprichoso'],T('pirarucu')['Garantido']),
    (D('pirarucu')['total'],D('pirarucu')['Caprichoso'],D('pirarucu')['Garantido']),
    'movido de ampliado para nucleo (referente faunistico fortemente especifico da Amazonia)')

add('tucupi','tucupi','Tupi/Nheengatu','lexema comum','Alimentação, subsistência e extrativismo','nucleo','',
    (T('tucupi')['total'],T('tucupi')['Caprichoso'],T('tucupi')['Garantido']),
    (D('tucupi')['total'],D('tucupi')['Caprichoso'],D('tucupi')['Garantido']),
    'movido de ampliado para nucleo')

add('tipiti','tipiti','Tupi/Nheengatu','lexema comum','Cultura material e artefatos','nucleo','',
    (T('tipiti')['total'],T('tipiti')['Caprichoso'],T('tipiti')['Garantido']),
    (D('tipiti')['total'],D('tipiti')['Caprichoso'],D('tipiti')['Garantido']),
    'movido de ampliado para nucleo')

# ---- CONTROLE: toponimia autorreferencial (fora do indice principal) ----
add('parintins','parintins','Topônimo','topônimo (autorreferencial)','Toponímia e hidronímia','controle_toponimico','',
    (T('parintins')['total'],T('parintins')['Caprichoso'],T('parintins')['Garantido']),
    (D('parintins')['total'],D('parintins')['Caprichoso'],D('parintins')['Garantido']),
    'quase tautologico (corpus e inteiramente do Festival de Parintins); reportar como subindice separado, com e sem este termo')

add('amazônia','amazônia;amazônico','Português regionalizado amazônico','topônimo/bioma (autorreferencial)','Toponímia e hidronímia','controle_toponimico','',
    (T('amazônia')['total'] if 'amazônia' in tf else 0, tf.get('amazônia',{}).get('Caprichoso',0), tf.get('amazônia',{}).get('Garantido',0)),
    (df.get('amazônia',{}).get('total',0), df.get('amazônia',{}).get('Caprichoso',0), df.get('amazônia',{}).get('Garantido',0)),
    'separado de "amazonas"; quase tautologico')

add('amazonas','amazonas','Topônimo','topônimo (autorreferencial)','Toponímia e hidronímia','controle_toponimico','',
    (tf.get('amazonas',{}).get('total',0), tf.get('amazonas',{}).get('Caprichoso',0), tf.get('amazonas',{}).get('Garantido',0)),
    (df.get('amazonas',{}).get('total',0), df.get('amazonas',{}).get('Caprichoso',0), df.get('amazonas',{}).get('Garantido',0)),
    'separado de "amazonia"; quase tautologico')

# ---- AMPLIADO ----
add('xamã','xamã;xama','Antropológico/globalizado','lexema comum','Ritual, cura e cosmologia','ampliado','',
    (T('xamã')['total'],T('xamã')['Caprichoso'],T('xamã')['Garantido']),
    (D('xamã')['total'],D('xamã')['Caprichoso'],D('xamã')['Garantido']),
    'tratado separado de "paje" (confirmado pelos dois especialistas); indicador de mudanca discursiva ao longo das decadas')

add('caboclo','caboclo;caboclos;cabocla','Português regionalizado amazônico','lexema comum (identitário)','Personagens, identidades e papéis sociais','ampliado','',
    (T('caboclo')['total'],T('caboclo')['Caprichoso'],T('caboclo')['Garantido']),
    (D('caboclo')['total'],D('caboclo')['Caprichoso'],D('caboclo')['Garantido']),
    'central para identidade amazonica mas nao exclusiva; interpretar com cautela')

add('ribeirinho','ribeirinho','Português regionalizado amazônico','lexema comum','Personagens, identidades e papéis sociais','ampliado','',
    (T('ribeirinho')['total'],T('ribeirinho')['Caprichoso'],T('ribeirinho')['Garantido']),
    (D('ribeirinho')['total'],D('ribeirinho')['Caprichoso'],D('ribeirinho')['Garantido']), '')

add('seringueiro','seringueiro','Português regionalizado amazônico','lexema comum','Personagens, identidades e papéis sociais','ampliado','',
    (T('seringueiro')['total'],T('seringueiro')['Caprichoso'],T('seringueiro')['Garantido']),
    (D('seringueiro')['total'],D('seringueiro')['Caprichoso'],D('seringueiro')['Garantido']), '')

add('tapuio','tapuio','Tupi/Nheengatu','lexema comum (identitário)','Personagens, identidades e papéis sociais','ampliado','',
    (T('tapuio')['total'],T('tapuio')['Caprichoso'],T('tapuio')['Garantido']),
    (D('tapuio')['total'],D('tapuio')['Caprichoso'],D('tapuio')['Garantido']),
    'origem corrigida para Tupi; carga historica/identitaria variavel, possiveis usos pejorativos')

add('onça','onça;onca','Domínio amplo (não exclusivo)','lexema comum','Fauna','ampliado','',
    (T('onça')['total'],T('onça')['Caprichoso'],T('onça')['Garantido']),
    (D('onça')['total'],D('onça')['Caprichoso'],D('onça')['Garantido']), '')

add('jacaré','jacaré;jacare','Tupi/Nheengatu','lexema comum','Fauna','ampliado','',
    (T('jacaré')['total'],T('jacaré')['Caprichoso'],T('jacaré')['Garantido']),
    (D('jacaré')['total'],D('jacaré')['Caprichoso'],D('jacaré')['Garantido']),
    'origem corrigida para Tupi/Nheengatu; nao exclusiva da amazonia por isso mantido em ampliado')

add('boto (animal)','boto','Português regionalizado amazônico','lexema comum','Fauna','ampliado','',
    (T('boto')['total'],T('boto')['Caprichoso'],T('boto')['Garantido']),
    (D('boto')['total'],D('boto')['Caprichoso'],D('boto')['Garantido']),
    'excluidas ocorrencias de "boto encantado"/"homem-boto" (ver nucleo); split parcial - nomes proprios como "Boto Malino"/"Boto Tucuxi" nao foram separados automaticamente (limitacao)')

add('boto encantado (unidade)','boto encantado;homem-boto','Português regionalizado amazônico','expressão multipalavra / entidade nomeada','Entidades míticas e encantados','nucleo','entidade narrativa/encantado',
    (P('boto_encantado')['total'],P('boto_encantado')['Caprichoso'],P('boto_encantado')['Garantido']),
    (PD('boto_encantado')['total'],PD('boto_encantado')['Caprichoso'],PD('boto_encantado')['Garantido']),
    'split parcial de "boto" (ver nota em boto-animal)')

add('arara','arara','Tupi/Nheengatu','lexema comum','Fauna','ampliado','',
    (T('arara')['total'],T('arara')['Caprichoso'],T('arara')['Garantido']), (D('arara')['total'],D('arara')['Caprichoso'],D('arara')['Garantido']),
    'origem corrigida para Tupi/Nheengatu')

add('sucuri','sucuri;sucurijú','Tupi/Nheengatu','lexema comum','Fauna','ampliado','',
    (T('sucuri')['total'],T('sucuri')['Caprichoso'],T('sucuri')['Garantido']), (D('sucuri')['total'],D('sucuri')['Caprichoso'],D('sucuri')['Garantido']),
    'origem corrigida para Tupi/Nheengatu')

add('tucano','tucano','Tupi/Nheengatu','lexema comum','Fauna','ampliado','',
    (T('tucano')['total'],T('tucano')['Caprichoso'],T('tucano')['Garantido']), (D('tucano')['total'],D('tucano')['Caprichoso'],D('tucano')['Garantido']),
    'origem corrigida para Tupi/Nheengatu')

add('guaraná','guaraná;guarana','Tupi/Nheengatu','lexema comum','Flora / Alimentação e extrativismo','ampliado','',
    (T('guaraná')['total'],T('guaraná')['Caprichoso'],T('guaraná')['Garantido']), (D('guaraná')['total'],D('guaraná')['Caprichoso'],D('guaraná')['Garantido']),
    'origem corrigida para Tupi/Nheengatu; multirrotulo flora+economia')

add('açaí','açaí;acai','Tupi/Nheengatu','lexema comum','Flora / Alimentação e extrativismo','ampliado','',
    (T('açaí')['total'],T('açaí')['Caprichoso'],T('açaí')['Garantido']), (D('açaí')['total'],D('açaí')['Caprichoso'],D('açaí')['Garantido']),
    'origem corrigida para Tupi/Nheengatu')

add('seringueira','seringueira','Português regionalizado amazônico','lexema comum','Flora','ampliado','',
    (T('seringueira')['total'],T('seringueira')['Caprichoso'],T('seringueira')['Garantido']), (D('seringueira')['total'],D('seringueira')['Caprichoso'],D('seringueira')['Garantido']), '')

add('castanheira','castanheira','Português regionalizado amazônico','lexema comum (ambíguo)','Flora','ampliado','',
    (T('castanheira')['total'],T('castanheira')['Caprichoso'],T('castanheira')['Garantido']), (D('castanheira')['total'],D('castanheira')['Caprichoso'],D('castanheira')['Garantido']),
    'forma isolada e generica; ideal seria contar so "castanheira-do-para" (nao verificado)')

add('mandioca','mandioca;macaxeira','Tupi/Tupinambá','lexema comum','Alimentação, subsistência e extrativismo','ampliado','',
    (T('mandioca')['total'],T('mandioca')['Caprichoso'],T('mandioca')['Garantido']), (D('mandioca')['total'],D('mandioca')['Caprichoso'],D('mandioca')['Garantido']),
    'origem corrigida para Tupi/Tupinambá; mantido ampliado por difusao pan-brasileira')

add('canoa','canoa','Origem indígena americana / empréstimo antigo (a confirmar)','lexema comum','Cultura material e artefatos','ampliado','',
    (T('canoa')['total'],T('canoa')['Caprichoso'],T('canoa')['Garantido']), (D('canoa')['total'],D('canoa')['Caprichoso'],D('canoa')['Garantido']),
    'origem corrigida: termo pan-americano de uso geral no portugues, nao "portugues regionalizado amazonico"')

add('maloca','maloca;oca','Indígena (etimologia a confirmar)','lexema comum','Cultura material e artefatos','ampliado','',
    (T('maloca')['total'],T('maloca')['Caprichoso'],T('maloca')['Garantido']), (D('maloca')['total'],D('maloca')['Caprichoso'],D('maloca')['Garantido']),
    'origem corrigida: pan-indigena, nao exclusivamente Tupi/Nheengatu')

add('cocar','cocar','Português / empréstimo europeu','lexema comum','Cultura material e artefatos','ampliado','',
    (T('cocar')['total'],T('cocar')['Caprichoso'],T('cocar')['Garantido']), (D('cocar')['total'],D('cocar')['Caprichoso'],D('cocar')['Garantido']),
    'CORRECAO IMPORTANTE: nao e de origem indigena, ao contrario do que constava na v1')

add('encantaria','encantaria','Português regionalizado amazônico','categoria cosmológica (não é entidade)','Ritual, cura e cosmologia','ampliado','',
    (T('encantaria')['total'],T('encantaria')['Caprichoso'],T('encantaria')['Garantido']), (D('encantaria')['total'],D('encantaria')['Caprichoso'],D('encantaria')['Garantido']), '')

add('várzea','várzea;varzea','Português de uso geral (sentido ecológico regional no contexto)','lexema comum','Paisagem, ecossistemas e hidrografia','ampliado','',
    (T('várzea')['total'],T('várzea')['Caprichoso'],T('várzea')['Garantido']), (D('várzea')['total'],D('várzea')['Caprichoso'],D('várzea')['Garantido']),
    'movido de nucleo para ampliado (termo de uso geomorfologico amplo, nao exclusivo)')

add('remanso','remanso','Português de uso geral','lexema comum','Paisagem, ecossistemas e hidrografia','ampliado','',
    (T('remanso')['total'],T('remanso')['Caprichoso'],T('remanso')['Garantido']), (D('remanso')['total'],D('remanso')['Caprichoso'],D('remanso')['Garantido']),
    'movido de nucleo para ampliado')

add('barranco','barranco','Português de uso geral','lexema comum','Paisagem, ecossistemas e hidrografia','ampliado','',
    (T('barranco')['total'],T('barranco')['Caprichoso'],T('barranco')['Garantido']), (D('barranco')['total'],D('barranco')['Caprichoso'],D('barranco')['Garantido']),
    'movido de nucleo para ampliado')

add('furo','furo','Português de uso geral (acepção hidrográfica regional)','lexema comum (ambíguo)','Paisagem, ecossistemas e hidrografia','ampliado','',
    (T('furo')['total'],T('furo')['Caprichoso'],T('furo')['Garantido']), (D('furo')['total'],D('furo')['Caprichoso'],D('furo')['Garantido']),
    'movido de nucleo para ampliado; contar como feicao hidrografica so com contexto de rio/lago/canal')

# ---- EXCLUIDO da contagem simples (genericos demais) ----
for forma,var,dom,nota in [
    ('pescador','pescador','Personagens, identidades e papéis sociais','termo generico demais para indicador lexical autonomo de regionalismo'),
    ('farinha','farinha','Alimentação, subsistência e extrativismo','generico; contar so em "farinha d’agua"/"farinha de mandioca" (nao verificado)'),
    ('flecha','flecha;flechas','Cultura material e artefatos','vocabulo pan-cultural, alto risco de falso positivo metaforico'),
    ('cura','cura','Ritual, cura e cosmologia','generico demais; usar so em coocorrencia com pajelanca'),
    ('espírito','espírito;espirito','Ritual, cura e cosmologia','termo religioso generico, sem especificidade amazonica'),
    ('ancestral','ancestral','Ritual, cura e cosmologia','termo contemporaneo generico, muito usado em discursos identitarios'),
]:
    add(forma, var, 'Português de uso geral', 'lexema comum genérico', dom, 'excluido_generico', '',
        (T(forma)['total'],T(forma)['Caprichoso'],T(forma)['Garantido']),
        (D(forma)['total'],D(forma)['Caprichoso'],D(forma)['Garantido']), nota)

# ---- EXCLUIDO: colonial/auto tradicional e institucional do festival ----
add('sinhá','sinhá;sinha','Colonial/nordestino incorporado ao auto','lexema comum','Vocabulário do auto tradicional','excluido','',
    (T('sinhá')['total'],T('sinhá')['Caprichoso'],T('sinhá')['Garantido']), (D('sinhá')['total'],D('sinhá')['Caprichoso'],D('sinhá')['Garantido']),
    'movido de ampliado para excluido: nao mede indigeneidade/regionalidade amazonica')

add('sinhazinha','sinhazinha','Colonial/nordestino incorporado ao auto','item oficial do Festival (personagem do auto)','Vocabulário do auto tradicional','excluido','',
    (T('sinhazinha')['total'],T('sinhazinha')['Caprichoso'],T('sinhazinha')['Garantido']), (D('sinhazinha')['total'],D('sinhazinha')['Caprichoso'],D('sinhazinha')['Garantido']),
    'movido de ampliado para excluido: "Sinhazinha da Fazenda" e item oficial estrutural do auto, mesma logica de marujada/toada')

for forma,var,dom,tier,nota in [
    ('marujada','marujada','Vocabulário institucional do Festival','excluido','item oficial/jargao do festival'),
    ('batucada','batucada','Vocabulário institucional do Festival','excluido','item oficial/jargao do festival'),
    ('arena','arena','Vocabulário institucional do Festival','excluido',''),
    ('toada','toada','Vocabulário institucional do Festival','excluido','marcador de genero, nao de regionalismo'),
    ('garrote','garrote','Vocabulário do auto tradicional','excluido','camada colonial-pastoril do auto'),
    ('vaqueirada','vaqueirada','Vocabulário do auto tradicional','excluido',''),
    ('arquibancada','arquibancada','Vocabulário institucional do Festival','excluido',''),
    ('torcedor','torcedor','Vocabulário institucional do Festival','excluido',''),
    ('bumbá','bumbá;bumba','Vocabulário institucional do Festival','excluido','marcador de genero'),
    ('galera','galera','Vocabulário institucional do Festival','excluido',''),
    ('amo','amo','Vocabulário do auto tradicional','excluido','personagem do auto - fazendeiro'),
    ('fazenda','fazenda','Vocabulário do auto tradicional','excluido',''),
]:
    origem = 'Colonial/nordestino incorporado ao auto' if 'auto' in dom else 'Vocabulário institucional do Festival'
    add(forma, var, origem, 'item oficial/estrutural do festival', dom, tier, '',
        (T(forma)['total'],T(forma)['Caprichoso'],T(forma)['Garantido']),
        (D(forma)['total'],D(forma)['Caprichoso'],D(forma)['Garantido']), nota)

# ---- CATEGORIA SEPARADA: afro-amazonico / identitario (fora do indice indigena) ----
add('málúù dúdú','málúù;dúdú;málúù dúdú','Iorubá / matriz africana','expressão multipalavra / item de toada específica','Vocabulário identitário do Caprichoso / matriz afro-brasileira','afro_identitario_separado','',
    (P('maluu_dudu')['total'],P('maluu_dudu')['Caprichoso'],P('maluu_dudu')['Garantido']),
    (PD('maluu_dudu')['total'],PD('maluu_dudu')['Caprichoso'],PD('maluu_dudu')['Garantido']),
    'REMOVIDO do indice indigena/regional principal (v1 continha erro: nao e Tupi/Nheengatu). Concentrado em poucas toadas (refrao repetido) - ver freq documental muito menor que freq de token')

with open(args.out, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['forma_canonica','variantes','origem_etimologica','estatuto_referencial','dominio_eixo2',
                'tier','subtipo_entidade','freq_token_total','freq_token_caprichoso','freq_token_garantido',
                'freq_doc_total','freq_doc_caprichoso','freq_doc_garantido','nota'])
    for row in rows:
        w.writerow(row)

print(f"Total de linhas: {len(rows)}")
from collections import Counter
print(Counter(r[5] for r in rows))
