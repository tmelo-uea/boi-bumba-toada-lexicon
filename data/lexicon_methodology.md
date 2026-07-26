# Léxico regional-amazônico v2 — nota metodológica

Consolida as mudanças da v1 (lexico_mestre.csv) para a v2 (lexico_mestre_v2.csv), incorporando
o parecer do especialista em cultura de Parintins (parecer_revisao_lexico.md) e a validação por
dupla-anotação cega do termo "cobra" (anotacao_cobra_cega_preenchida.csv).

## 1. Estrutura em dois eixos (mudança estrutural)

A coluna única "origem_eixo1" da v1 misturava origem etimológica com tipo referencial. Na v2,
isso vira duas colunas:

- `origem_etimologica`: Tupi/Nheengatu, outra língua indígena, iorubá/matriz africana,
  português, português regionalizado amazônico, empréstimo europeu, indígena (etimologia a
  confirmar).
- `estatuto_referencial`: lexema comum, etnônimo, topônimo, item oficial do Festival, entidade
  nomeada, expressão multipalavra.

Também foi adicionada a coluna `subtipo_entidade`, aplicada às entidades míticas, com 5 subtipos
em vez de uma oposição binária divindade/personagem: divindade/ser cosmológico; espírito/força da
mata ou das águas; ancestral/herói cultural; entidade narrativa/encantado; complexo ritual ou
categoria cosmológica.

## 2. Correção crítica: "málúù dúdú" removido do léxico indígena

Na v1, "málúù" e "dúdú" foram contados como dois tokens Tupi/Nheengatu (151 + 149 = ~300
ocorrências), fortemente concentrados no Caprichoso. A revisão identificou que a expressão é na
verdade **iorubá** (matriz africana), usada em uma toada específica do Caprichoso, e que a
contagem de ~300 vinha quase toda da repetição do refrão de **apenas 3 toadas distintas**
(frequência documental = 3; frequência de token = 149 como unidade).

Isso foi removido do índice indígena/regional principal (`nucleo`) e movido para uma categoria
própria — `afro_identitario_separado` — fora do cálculo de regionalismo indígena. Sem essa
correção, o índice estaria artificialmente inflado para o Caprichoso.

## 3. Expressões multipalavra contadas como unidade

Termos que antes eram somados como tokens separados agora são detectados como frase e contados
uma vez, evitando dupla contagem:

| Unidade | Tokens que eram somados na v1 | Ocorrências reais (unidade) |
|---|---|---|
| cunhã-poranga | cunhã (284) + poranga (149) | 136 |
| sateré-mawé | sateré (86) + mawé (82) | 53 |
| matinta perera | matinta (~21) | 4 |
| cobra norato/honorato | (incluído em "cobra") | 7 |
| vitória-régia | vitória (56) | 6 |
| boto encantado / homem-boto | (incluído em "boto") | 1 |

Após mascarar essas frases, os termos isolados (`cunhã (isolado)`, `poranga (isolado)`, `sateré
(isolado)`, `mawé (isolado)`, `matinta (isolado)`) foram recontados sem os componentes já
capturados na unidade — ex: "poranga" isolado cai de 149 para 13 ocorrências reais (quase todo o
uso de "poranga" no corpus é dentro de "cunhã-poranga").

**Limitação conhecida:** a divisão de "boto" é parcial — só capturamos as formas literais "boto
encantado" e "homem-boto". Nomes próprios de botos específicos da mitologia (ex: "Boto Malino",
"Boto Tucuxi", vistos no corpus) continuam contados dentro de "boto (animal)", não migrados para
o núcleo mítico. Resolver isso exigiria o mesmo tipo de leitura contextual feita para "cobra".

## 4. "Cobra": validação por dupla-anotação cega

O termo "cobra"/"cobras" (114 ocorrências) foi classificado independentemente por mim e por um
colega com familiaridade na cultura de Parintins, sem que a segunda pessoa visse a primeira
classificação (ver `instrucoes_anotacao_cobra.md`).

- **Concordância bruta**: 81,5% (66/81 itens comparáveis, após deduplicar refrões repetidos)
- **Cohen's kappa**: 0,136 (baixo — a concordância bruta é inflada pelo desbalanceamento de
  classes; a maioria das respostas cai em "mítica")
- Revisão manual das 15 discordâncias mostrou que a maior parte era inconsistência minha (mesma
  frase repetida classificada de forma diferente em passagens diferentes da mesma toada), não
  ambiguidade genuína
- **Distribuição final pós-adjudicação**: 104 míticas (91,2%), 7 animal (6,1%), 3 metáfora
  (2,6%)

O léxico v2 usa **apenas as 104 ocorrências mítica-adjudicadas** para a entrada "cobra grande",
não o total bruto de 114. O kappa baixo é reportado como limitação metodológica explícita — a
classificação mítica/animal/metáfora, embora conceitualmente sólida, não é trivialmente
reprodutível mesmo entre dois leitores cuidadosos.

## 5. Frequência documental além de frequência de token

Cada termo agora tem duas contagens: `freq_token` (ocorrências brutas) e `freq_doc` (número de
toadas distintas em que aparece). Isso corrige o viés de refrões repetidos — o caso extremo é
"málúù dúdú": 149 tokens, mas só 3 toadas. Recomenda-se usar frequência documental como medida
principal nas comparações Caprichoso×Garantido e década×década, com frequência de token como
métrica secundária.

## 6. Correções de origem etimológica

Cerca de 15 termos tinham origem etimológica incorreta na v1 (marcados como "português
regionalizado amazônico" quando são de fato Tupi/Nheengatu): curupira, boiúna, boiaçu, igapó,
jacaré, arara, sucuri, tucano, guaraná, açaí, tucupi, tipiti, tapuio. "Mandioca" foi corrigida
para Tupi/Tupinambá. Duas correções na direção oposta: "cocar" **não** é de origem indígena (é
empréstimo europeu que descreve um artefato associado a representações indígenas), e "canoa" é
termo pan-americano de uso geral, não regionalismo amazônico específico.

## 7. Mudanças de camada (tier)

- **Para núcleo**: pirarucu, tipiti, tucupi, vitória-régia (forma canônica também corrigida para
  "vitória-régia", com variante sem hífen)
- **De núcleo para ampliado**: várzea, remanso, barranco, furo (termos de uso geral, não
  exclusivos da Amazônia, sem marca regional forte o suficiente para núcleo)
- **De ampliado para excluído**: sinhá e sinhazinha (a v1 tinha as duas em "ampliado"; a revisão
  argumentou que, principalmente "Sinhazinha da Fazenda" sendo item oficial estrutural do auto,
  a mesma lógica aplicada a marujada/toada deveria valer aqui)
- **Para excluído (genérico)**: pescador, farinha, flecha, cura, espírito, ancestral — termos
  frequentes mas genéricos demais para funcionar como indicador lexical autônomo de regionalismo
  sem regra de coocorrência contextual (não implementada nesta versão)
- **Nova camada `controle_toponimico`**: Parintins, Amazônia e Amazonas saem do índice principal
  e formam um subíndice à parte — são quase tautológicos num corpus inteiramente dedicado ao
  Festival de Parintins. Recomenda-se reportar os resultados principais com e sem esses termos
  (análise de sensibilidade).

## 8. Confundidor institucional — anotação enviada para revisão externa

Pajé, cunhã(-poranga) e tuxaua(s) são simultaneamente léxico indígena/regional **e** itens
oficiais avaliados no Festival de Parintins (constam na lista de quesitos julgados). O especialista
recomendou uma "análise de sensibilidade que retire menções claramente institucionais".

Não existe um sinal textual confiável para distinguir automaticamente "pajé" usado como referência
cultural/ritual de "pajé" usado como referência ao item avaliado — ambos usam exatamente a mesma
palavra, no mesmo tipo de contexto poético. Por isso, ao contrário dos outros itens desta nota, esta
correção não foi resolvida por regra automática: foi preparado um pacote de anotação manual (mesmo
formato usado para "cobra") cobrindo as 306 toadas distintas em que os três termos aparecem (pajé:
160 toadas; cunhã isolado: 73; cunhã-poranga: 41; tuxaua: 32), com um exemplo de contexto
representativo por toada, para classificação em institucional / cultural_ritual / indeterminado.

Arquivos: `instrucoes_anotacao_institucional.md` + `anotacao_institucional_cega.csv`, enviados
para o mesmo colega que validou a classificação de "cobra". Espera-se, com base no kappa baixo
observado em "cobra" (0,136), que esta distinção também produza concordância limitada — isso será
reportado com a mesma transparência, não como falha do método. Enquanto a resposta não retorna, o
léxico v2 mantém pajé/cunhã(-poranga)/tuxaua no núcleo sem segregação institucional, com a nota
"CONFUNDIDOR INSTITUCIONAL" sinalizando que a leitura desses números deve considerar essa mistura.

## 9. Termos candidatos não incluídos (sugestão do especialista)

Busca adicional recomendada, sem inclusão automática nesta versão: cunhantã, jaci, guaraci/kwaracy,
paneiro, cuia, tacape, zarabatana, urucum, jenipapo, sapopema, pupunha, tucumã, cupuaçu, tambaqui,
tucunaré, tracajá, mãe-d'água. Não verificados por falta de tempo — ficam como próximo passo se
houver janela antes do prazo do artigo completo (28/ago).
