# Projeto de Análise de Temperatura de Superfície (LST) — Rio de Janeiro

Este repositório reúne o fluxo completo da dissertação para análise de **Temperatura de Superfície Continental (LST/TSC)** no município do Rio de Janeiro, com foco nas **Áreas de Planejamento (AP 1 a AP 5)**, separando as estações de **verão** e **inverno** e dois períodos históricos:

- **Período 1:** 2000–2013 (Landsat 5/7)
- **Período 2:** 2014–2024 (Landsat 8, com ajuste pontual no verão e uso complementar de Landsat 9 em 2024)

## 1) Organização técnica do projeto

Os scripts estão divididos em duas plataformas:

- **Arquivos `.js`** → desenvolvidos para execução no **Google Earth Engine (GEE Code Editor)**.
- **Arquivos `.py`** → desenvolvidos para execução no **Google Colab**, com leitura/gravação no **Google Drive**.

## 2) Fluxo metodológico geral

1. **GEE (JavaScript):**
   - Seleção de imagens Landsat por estação e ano;
   - Máscara de nuvens/sombra e cálculo da LST;
   - Geração de medianas anuais/sazonais e exportação de GeoTIFFs/CSVs.

2. **Colab (Python):**
   - Leitura dos rasters exportados;
   - Análises estatísticas por pixel e por AP:
     - Mann-Kendall (tendência),
     - “Curvatura de Sen” (inclinação/taxa anual),
     - Significância (p-valor < 0,05),
     - Pettitt (ponto de ruptura),
     - Boxplots comparativos entre períodos.

---

## 3) Pré-requisitos

## 3.1 Google Earth Engine (para `.js`)

- Conta ativa no Earth Engine;
- Assets vetoriais disponíveis (ex.: limite do município e APs);
- Permissão para exportar para Google Drive.

## 3.2 Google Colab (para `.py`)

- Conta Google com Drive montado no Colab;
- Bibliotecas instaladas via `pip` conforme cada notebook/script (ex.: `rasterio`, `numpy`, `matplotlib`, `pymannkendall`, `geopandas`, `fiona`, `seaborn`, `scipy`).

> **Importante:** os caminhos de pasta (`/content/drive/MyDrive/...`) e nomes de arquivos devem ser ajustados para a sua estrutura real no Drive.

---

## 4) Procedimento detalhado por arquivo

Abaixo, cada arquivo é explicado com objetivo, entrada, processamento e saída.

## 4.1 Scripts GEE (JavaScript)

### `LANDSAT_5_7_VERAO.js`
**Objetivo:** Processar LST de verão para 2000–2013 com Landsat 5/7, incluindo anos “BOM”, “RESGATE” e “CRÍTICO”.

**Procedimentos principais:**
1. Define AOI a partir do asset das APs.
2. Aplica máscara de nuvens/sombra por `QA_PIXEL`.
3. Calcula NDVI, emissividade e LST.
4. Cria máscara urbana (`NDVI < 0.6`) para remover maciços.
5. Para cada ano:
   - ajusta janela temporal (normal ou ampliada);
   - gera composição RGB mediana;
   - gera LST mediana (full e urbana);
   - exporta imagens e estatísticas por AP.
6. Exporta tabelas de qualidade temporal e dados para boxplot.

**Saídas típicas:**
- GeoTIFF/visualização RGB por ano;
- LST full e LST urbana por ano;
- CSV de datas/sensores e CSV para boxplot.

---

### `LANDSAT_5_7_INVERNO.js`
**Objetivo:** Processar LST de inverno para 2000–2013 com estratégia de “resgate” em anos críticos.

**Procedimentos principais:**
1. Define AOI/APs e pasta de exportação.
2. Usa máscara de qualidade (`QA_PIXEL`) e calcula LST com NDVI + emissividade.
3. Separa anos com janela padrão de inverno e anos com janela ampliada de resgate.
4. Para cada ano:
   - cria RGB de inspeção;
   - calcula LST mediana;
   - exporta RGB, LST full e LST urbana;
   - calcula estatísticas por AP (mediana, mínimo, máximo);
   - guarda metadados de datas/sensores.
5. Exporta tabelas finais para controle de qualidade e análises estatísticas.

**Saídas típicas:**
- Imagens por ano (RGB e LST);
- CSV de status/quantidade de cenas;
- CSV de estatísticas por AP.

---

### `LANDSAT_8_VERAO.js`
**Objetivo:** Construir série de verão (2014–2024) para Landsat 8, com ajustes de consistência temporal.

**Procedimentos principais:**
1. Carrega limite do Rio e APs.
2. Mascara nuvens/sombras e aplica fatores de escala de reflectância/temperatura.
3. Calcula LST por imagem (NDVI → FVC → emissividade → LST).
4. Gera medianas anuais sazonais de verão (janela dezembro–março).
5. Inclui ajuste pontual:
   - adiciona imagem específica de 2024 (Landsat 9);
   - força imagem específica para 2018 (Landsat 8) e substitui ocorrência padrão do ano.
6. Calcula mediana geral multi-anual, gera gráficos de série temporal geral e por AP, e exporta resultados.

**Saídas típicas:**
- Mediana LST verão 2014–2024;
- Séries temporais (gráficos e tabelas no GEE);
- Exportações para Drive.

---

### `LANDSAT_8_INVERNO.js`
**Objetivo:** Construir série de inverno (2014–2024) para Landsat 8.

**Procedimentos principais:**
1. Carrega município e APs.
2. Mascaramento de nuvens/sombras + escalonamento de bandas.
3. Cálculo de LST por imagem.
4. Para cada ano, calcula mediana de inverno (junho–setembro).
5. Filtra anos sem imagem válida.
6. Calcula mediana geral, gera série temporal média do município e série por AP.
7. Exporta produtos para Drive.

**Saídas típicas:**
- Mediana LST inverno 2014–2024;
- Gráficos temporais;
- GeoTIFF exportado.

---

## 4.2 Scripts Colab (Python)

### A) Medianas, tendência e inclinação — Landsat 5/7 (2000–2013)

#### `LANDSAT_5_7_VERAO_MEDIANA.py`
- Consolida rasters anuais de verão em mediana de referência do período 2000–2013.
- Lê GeoTIFFs do Drive, empilha matrizes e salva mediana final.

#### `LANDSAT_5_7_INVERNO_MEDIANA.py`
- Mesmo procedimento do arquivo anterior, mas para inverno 2000–2013.

#### `LANDSAT_5_7_VERAO_TENDENCIA_MANN_KENDALL.py`
- Aplica teste de Mann-Kendall por pixel para identificar direção da tendência térmica no verão.
- Saída principal: raster com **Tau de Kendall**.

#### `LANDSAT_5_7_INVERNO_TENDENCIA_MANN_KENDALL.py`
- Equivalente ao anterior para inverno.

#### `LANDSAT_5_7_VERAO_CURVATURA_SEN_SLOPE.py`
- Estima taxa anual de variação térmica por pixel (inclinação “Sen slope”, implementada por regressão linear em vários scripts).
- Saída principal: raster em °C/ano.

#### `LANDSAT_5_7_INVERNO_CURVATURA_SEN_SLOPE.py`
- Equivalente ao anterior para inverno.

---

### B) Medianas, tendência e inclinação — Landsat 8 (2014–2024)

#### `LANDSAT_8_VERAO_TENDENCIA_MANN_KENDALL.py`
- Mann-Kendall por pixel para verão do período Landsat 8.
- Saída: raster de Tau de Kendall.

#### `LANDSAT_8_INVERNO_TENDENCIA_MANN_KENDALL.py`
- Mann-Kendall por pixel para inverno do período Landsat 8.

#### `LANDSAT_8_VERAO_CURVATURA_SEN_SLOPE.py`
- Estima inclinação térmica por pixel no verão (°C/ano).

#### `LANDSAT_8_INVERNO_CURVATURA_SEN_SLOPE.py`
- Estima inclinação térmica por pixel no inverno.

---

### C) Significância estatística (Mann-Kendall p-valor)

#### `SIGNIFICANCIA_VERAO_MANN_KENDALL.py`
- Calcula p-valor por pixel via Mann-Kendall para dois blocos temporais:
  - 2000–2013
  - 2014–2024
- Gera mapas binários de significância (`1` para p < 0,05; `0` caso contrário).

#### `SIGNIFICANCIA_INVERNO_MANN_KENDALL.py`
- Mesmo procedimento do arquivo anterior para inverno.

---

### D) Ruptura temporal (Pettitt)

#### `TESTE_PETTITT_VERAO.py`
- Calcula média anual espacial da LST (um valor por ano) e aplica teste de Pettitt.
- Retorna ano de ruptura, p-valor e gráfico temporal com linha de quebra.

#### `TESTE_PETTITT_INVERNO.py`
- Mesma lógica para série de inverno.

---

### E) Boxplots comparativos por AP

#### `BLOXSPOT_VERAO.py`
- Extrai pixels por AP a partir dos rasters de verão.
- Compara distribuição da LST entre períodos (2000–2013 vs 2014–2024).
- Gera boxplots e resumo de medianas/aumento por AP.

#### `BLOXSPOT_INVERNO.py`
- Mesmo procedimento para inverno.

---

## 5) Ordem recomendada de execução

### Etapa 1 — GEE (produção dos rasters)
1. Executar `LANDSAT_5_7_VERAO.js`
2. Executar `LANDSAT_5_7_INVERNO.js`
3. Executar `LANDSAT_8_VERAO.js`
4. Executar `LANDSAT_8_INVERNO.js`

### Etapa 2 — Colab (análises derivadas)
1. Gerar medianas de referência (`*_MEDIANA.py`)
2. Rodar tendências (`*_TENDENCIA_MANN_KENDALL.py`)
3. Rodar inclinação (`*_CURVATURA_SEN_SLOPE.py`)
4. Rodar mapas de significância (`SIGNIFICANCIA_*`)
5. Rodar ruptura temporal (`TESTE_PETTITT_*`)
6. Rodar boxplots comparativos (`BLOXSPOT_*`)

---

## 6) Estrutura de dados esperada no Google Drive

Sugestão de organização (ajuste conforme sua realidade):

- `MESTRADO/01. DADOS/AP/` → vetores (KML/shape das APs)
- `MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/VERÃO/`
- `MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/INVERNO/`
- Pastas de saída do GEE para Landsat 8 verão/inverno

**Boa prática:** padronizar nomes dos GeoTIFFs com ano explícito (ex.: `..._2018.tif`) para facilitar filtros automáticos nos scripts.

---

## 7) Observações importantes para reprodutibilidade

- Ajuste os caminhos de entrada/saída no início de cada script Python.
- Verifique CRS/projeção dos vetores AP antes de mascarar rasters (`to_crs`).
- Alguns scripts usam critérios de nuvem e janelas temporais específicas para “resgate” de anos com baixa qualidade.
- Em alguns códigos, o termo “Curvatura de Sen” é operacionalizado por regressão linear como aproximação de inclinação temporal.
- Para resultados comparáveis entre execuções, fixe semente aleatória em rotinas com amostragem de pixels (quando aplicável).

---

## 8) Produtos finais gerados no projeto

- Mapas de mediana de LST por estação/período;
- Mapas de tendência (Tau de Kendall);
- Mapas de inclinação anual (°C/ano);
- Mapas de significância estatística (p < 0,05);
- Gráficos e tabelas de ruptura temporal (Pettitt);
- Boxplots e resumos de mediana por AP (comparação entre períodos).

---

## 9) Como citar este repositório no texto da dissertação

Você pode descrever o repositório como:

> “Fluxo metodológico híbrido GEE + Google Colab para processamento da LST, análise de tendência temporal e comparação espacial por Áreas de Planejamento no município do Rio de Janeiro (2000–2024).”
