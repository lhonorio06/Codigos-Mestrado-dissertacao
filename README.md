# O Clima Urbano do Rio de Janeiro (RJ)
## Desdobramentos da produção do espaço urbano na termografia de superfície

**Lucas Honorio Gomes Ferreira**  
Dissertação de Mestrado — Programa de Pós-Graduação em Geografia (PPGEO-UERJ)  
Orientador: Prof. Dr. Antonio Carlos da Silva Oscar Júnior  
Instituto de Geografia — Universidade do Estado do Rio de Janeiro  
Rio de Janeiro, 2025

---

## Sobre esta pesquisa

Este repositório reúne todos os códigos utilizados na dissertação de mestrado que investigou como os processos de reestruturação urbana da cidade do Rio de Janeiro, ocorridos sob a justificativa da realização de megaeventos esportivos — Pan-Americano 2007, Copa do Mundo 2014 e Jogos Olímpicos 2016 —, produziram alterações no campo térmico da cidade.

A análise combinou referenciais críticos da geografia urbana com técnicas de geoprocessamento e sensoriamento remoto, processando **239 imagens Landsat** ao longo de **25 anos (2000–2024)**, nas condições sazonais de verão e inverno, com resolução espacial de 30 metros.

O resultado central demonstrou empiricamente que infraestruturas construídas sem política de mitigação climática — como o Parque Olímpico e o Estádio Nilton Santos — produziram especializações térmicas mensuráveis e persistentes no campo termal urbano. Em contraste, áreas com contrapartida ambiental efetiva — como o Complexo Radical de Deodoro e o Parque de Madureira — não apresentaram aquecimento estatisticamente significativo.

> *"O clima é uma construção social"* — Sant'Anna Neto (2012)

---

## Estrutura do repositório

Os 21 arquivos estão organizados em dois grupos por plataforma de execução:

### Google Earth Engine — JavaScript (`.js`)
Processamento orbital e geração dos produtos de Temperatura de Superfície Continental (TSC):

| Arquivo | Descrição |
|---|---|
| `LANDSAT_5_7_VERAO.js` | TSC de verão 2000–2013 (Landsat 5/7) |
| `LANDSAT_5_7_INVERNO.js` | TSC de inverno 2000–2013 (Landsat 5/7) |
| `LANDSAT_8_VERAO.js` | TSC de verão 2014–2024 (Landsat 8) |
| `LANDSAT_8_INVERNO.js` | TSC de inverno 2014–2024 (Landsat 8) |

### Google Colab — Python (`.py`)
Análise estatística sobre os rasters exportados:

| Arquivo | Descrição |
|---|---|
| `LANDSAT_5_7_VERAO_MEDIANA.py` | Mediana de referência — verão 2000–2013 |
| `LANDSAT_5_7_INVERNO_MEDIANA.py` | Mediana de referência — inverno 2000–2013 |
| `LANDSAT_5_7_VERAO_TENDENCIA_MANN_KENDALL.py` | Tendência temporal pixel a pixel — verão 2000–2013 |
| `LANDSAT_5_7_INVERNO_TENDENCIA_MANN_KENDALL.py` | Tendência temporal pixel a pixel — inverno 2000–2013 |
| `LANDSAT_8_VERAO_TENDENCIA_MANN_KENDALL.py` | Tendência temporal pixel a pixel — verão 2014–2024 |
| `LANDSAT_8_INVERNO_TENDENCIA_MANN_KENDALL.py` | Tendência temporal pixel a pixel — inverno 2014–2024 |
| `LANDSAT_5_7_VERAO_CURVATURA_SEN_SLOPE.py` | Magnitude de mudança térmica (°C/ano) — verão 2000–2013 |
| `LANDSAT_5_7_INVERNO_CURVATURA_SEN_SLOPE.py` | Magnitude de mudança térmica (°C/ano) — inverno 2000–2013 |
| `LANDSAT_8_VERAO_CURVATURA_SEN_SLOPE.py` | Magnitude de mudança térmica (°C/ano) — verão 2014–2024 |
| `LANDSAT_8_INVERNO_CURVATURA_SEN_SLOPE.py` | Magnitude de mudança térmica (°C/ano) — inverno 2014–2024 |
| `SIGNIFICANCIA_VERAO_MANN_KENDALL.py` | Mapas binários de significância estatística — verão |
| `SIGNIFICANCIA_INVERNO_MANN_KENDALL.py` | Mapas binários de significância estatística — inverno |
| `TESTE_PETTITT_VERAO.py` | Detecção de ruptura temporal — verão |
| `TESTE_PETTITT_INVERNO.py` | Detecção de ruptura temporal — inverno |
| `BLOXSPOT_VERAO.py` | Variabilidade térmica por Área de Planejamento — verão |
| `BLOXSPOT_INVERNO.py` | Variabilidade térmica por Área de Planejamento — inverno |

---

## Fluxo metodológico

```
[GEE — JavaScript]
Landsat 5/7/8 → Máscara de nuvens → NDVI → Emissividade → TSC → Mediana anual → GeoTIFF

[Google Colab — Python]
GeoTIFF → Mann-Kendall (tendência) → Sen's Slope (magnitude) → Significância (p < 0,05)
        → Pettitt (ruptura temporal) → Boxplots por AP → Buffer 500m × infraestruturas
```

**Ordem recomendada de execução:**
1. Scripts GEE (`.js`) — processamento orbital
2. Scripts de mediana (`*_MEDIANA.py`)
3. Scripts de tendência (`*_TENDENCIA_MANN_KENDALL.py`)
4. Scripts de magnitude (`*_CURVATURA_SEN_SLOPE.py`)
5. Scripts de significância (`SIGNIFICANCIA_*.py`)
6. Scripts de ruptura (`TESTE_PETTITT_*.py`)
7. Scripts de boxplot (`BLOXSPOT_*.py`)

---

## Dados utilizados

Os dados matriciais (GeoTIFF) e vetoriais utilizados nesta pesquisa **não estão incluídos neste repositório** por limitação de tamanho.

- **Imagens Landsat:** disponíveis publicamente na plataforma [Google Earth Engine](https://earthengine.google.com/), coleções Landsat Collection 2 Level-2 (USGS).
- **Vetores das Áreas de Planejamento:** disponibilizados pelo [Instituto Pereira Passos (IPP)](https://www.data.rio/) — Prefeitura do Rio de Janeiro.
- **Dados processados intermediários:** armazenados em repositório privado no Google Drive. Disponíveis mediante solicitação ao autor.

---

## Nota metodológica

Os scripts de Curvatura de Sen (`*_CURVATURA_SEN_SLOPE.py`) utilizam regressão linear simples como aproximação da estimativa de tendência, opção metodológica adequada ao número reduzido de observações por estação (n = 11). Essa escolha está declarada e justificada na seção 4.3 da dissertação.

Os códigos foram desenvolvidos pelo autor e aprimorados com auxílio do Gemini (Google), em conformidade com as práticas emergentes de uso de Inteligência Artificial em pesquisa científica — conforme declarado na seção de metodologia da dissertação.

---

## Bibliotecas Python

```
rasterio
numpy
pandas
matplotlib
seaborn
scipy
pymannkendall
geopandas
fiona
shapely
```

---

## Como citar

```
FERREIRA, Lucas Honorio Gomes. O Clima Urbano do Rio de Janeiro (RJ):
desdobramentos da produção do espaço urbano na termografia de superfície.
2025. Dissertação (Mestrado em Geografia) — Instituto de Geografia,
Universidade do Estado do Rio de Janeiro, Rio de Janeiro, 2025.
Códigos disponíveis em: https://github.com/lhonorio06/Codigos-Mestrado-dissertacao
```

---

## Contato

**Lucas Honorio Gomes Ferreira**  
Programa de Pós-Graduação em Geografia — UERJ  
Secretaria de Estado do Ambiente e Sustentabilidade — SEAS/RJ  
GitHub: [@lhonorio06](https://github.com/lhonorio06)
