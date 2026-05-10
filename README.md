# Universidade do Estado do Rio de Janeiro (UERJ) / Programa de Pós-Graduação em Geografia (PPGEO-UERJ)

## O Clima Urbano do Rio de Janeiro (RJ): desdobramentos da produção do espaço urbano na termografia de superfície.
**Análise da Temperatura de Superfície Continental (LST/TSC) no Município do Rio de Janeiro (2000–2024) com Google Earth Engine e Google Colab**

> **Nota de adequação ABNT:** este README foi reorganizado em estrutura acadêmico-técnica para uso como base de **Apêndice Metodológico** da dissertação, seguindo convenções de redação técnica compatíveis com ABNT (seções numeradas, objetivo, materiais, métodos, resultados esperados e reprodutibilidade).

---

## 1 INTRODUÇÃO

Este repositório reúne rotinas de processamento e análise da Temperatura de Superfície Continental (LST/TSC) para o município do Rio de Janeiro, com recorte nas Áreas de Planejamento (AP 1 a AP 5), considerando duas estações do ano (verão e inverno) e dois períodos históricos de análise:

- **Período 1:** 2000–2013 (Landsat 5/7);
- **Período 2:** 2014–2024 (Landsat 8, com ajuste pontual usando Landsat 9 no verão de 2024).

A execução metodológica está dividida entre:

- **Google Earth Engine (GEE)** para processamento orbital e geração de produtos intermediários/finais;
- **Google Colab** para análises estatísticas e testes de tendência/ruptura sobre os rasters exportados.

---

## 2 OBJETIVOS

### 2.1 Objetivo geral

Implementar um fluxo reprodutível para estimar, comparar e interpretar a evolução espaço-temporal da LST no município do Rio de Janeiro entre 2000 e 2024.

### 2.2 Objetivos específicos

a) Gerar composições sazonais de LST para verão e inverno;
b) Avaliar tendência temporal por pixel (Mann-Kendall);
c) Estimar inclinação/taxa de mudança térmica anual (Sen slope/ajuste linear);
d) Delimitar significância estatística das tendências (p < 0,05);
e) Identificar possíveis pontos de ruptura temporal (Teste de Pettitt);
f) Comparar a variabilidade térmica entre APs e entre períodos (boxplots).

---

## 3 MATERIAIS, DADOS E FERRAMENTAS

### 3.1 Plataformas computacionais

- **Google Earth Engine Code Editor** (scripts `.js`);
- **Google Colab** (scripts `.py`, com montagem do Google Drive).

### 3.2 Fontes de dados

- Coleções Landsat Collection 2 Level-2 (Landsat 5, 7, 8 e apoio pontual Landsat 9, conforme script);
- Vetores de limite municipal e APs (assets GEE/KML no Drive, conforme etapa).

### 3.3 Bibliotecas Python utilizadas

`rasterio`, `numpy`, `matplotlib`, `pymannkendall`, `scipy`, `geopandas`, `fiona`, `pandas`, `seaborn`.

---

## 4 PROCEDIMENTOS METODOLÓGICOS

## 4.1 Etapa A — Processamento no GEE (JavaScript)

### 4.1.1 `LANDSAT_5_7_VERAO.js`
**Finalidade:** gerar LST de verão para 2000–2013 (Landsat 5/7), com classes de qualidade anual (BOM/RESGATE/CRÍTICO).

**Procedimentos:**
1. Define área de estudo via asset das APs;
2. Aplica máscara de nuvens/sombra usando `QA_PIXEL`;
3. Calcula NDVI, emissividade e LST;
4. Aplica máscara urbana (`NDVI < 0.6`);
5. Executa loop anual com janela sazonal padrão ou ampliada (resgate);
6. Exporta RGB, LST full e LST urbana;
7. Exporta tabelas (datas/sensores e dados para boxplot).

**Produtos gerados:** imagens por ano + tabelas CSV.

### 4.1.2 `LANDSAT_5_7_INVERNO.js`
**Finalidade:** gerar LST de inverno para 2000–2013 com tratamento de anos críticos.

**Procedimentos:**
1. Configuração de AOI, APs e pasta de saída;
2. Máscara de qualidade e cálculo de LST;
3. Definição de anos com janela padrão e janela de resgate;
4. Exportação anual (RGB, LST full e LST urbana);
5. Estatísticas por AP (mediana, mínimo e máximo);
6. Exportação de metadados de cenas.

**Produtos gerados:** imagens anuais e tabelas de controle/estatística.

### 4.1.3 `LANDSAT_8_VERAO.js`
**Finalidade:** construir série de verão 2014–2024 para Landsat 8 com ajustes de consistência temporal.

**Procedimentos:**
1. Carrega limite municipal e APs;
2. Aplica máscara de nuvens/sombras e fatores de escala;
3. Calcula LST por imagem (NDVI → FVC → emissividade → LST);
4. Gera mediana sazonal por ano (dezembro–março);
5. Inclui imagem pontual Landsat 9 (2024);
6. Força substituição de imagem de 2018 por cena específica;
7. Gera mediana geral, gráficos e exportações.

**Produtos gerados:** série sazonal, mediana geral, gráficos e rasters exportados.

### 4.1.4 `LANDSAT_8_INVERNO.js`
**Finalidade:** construir série de inverno 2014–2024 para Landsat 8.

**Procedimentos:**
1. Carrega geometrias de estudo;
2. Aplica máscara atmosférica/qualidade;
3. Calcula LST por imagem;
4. Compõe mediana anual de inverno (junho–setembro);
5. Filtra anos sem cena válida;
6. Produz mediana geral e séries temporais (geral e por AP);
7. Exporta resultados.

**Produtos gerados:** mediana multi-anual, gráficos e GeoTIFF.

---

## 4.2 Etapa B — Processamento estatístico no Colab (Python)

### 4.2.1 Grupo “MEDIANA”

- `LANDSAT_5_7_VERAO_MEDIANA.py`: consolida rasters anuais de verão (2000–2013) em mediana de referência;
- `LANDSAT_5_7_INVERNO_MEDIANA.py`: consolida rasters anuais de inverno (2000–2013) em mediana de referência.

### 4.2.2 Grupo “TENDÊNCIA MANN-KENDALL”

- `LANDSAT_5_7_VERAO_TENDENCIA_MANN_KENDALL.py`: tendência por pixel (Tau) para verão 2000–2013;
- `LANDSAT_5_7_INVERNO_TENDENCIA_MANN_KENDALL.py`: tendência por pixel (Tau) para inverno 2000–2013;
- `LANDSAT_8_VERAO_TENDENCIA_MANN_KENDALL.py`: tendência por pixel (Tau) para verão 2014–2024;
- `LANDSAT_8_INVERNO_TENDENCIA_MANN_KENDALL.py`: tendência por pixel (Tau) para inverno 2014–2024.

### 4.2.3 Grupo “CURVATURA / SEN SLOPE”

- `LANDSAT_5_7_VERAO_CURVATURA_SEN_SLOPE.py`: taxa anual de mudança térmica (°C/ano) no verão 2000–2013;
- `LANDSAT_5_7_INVERNO_CURVATURA_SEN_SLOPE.py`: taxa anual de mudança térmica (°C/ano) no inverno 2000–2013;
- `LANDSAT_8_VERAO_CURVATURA_SEN_SLOPE.py`: taxa anual de mudança térmica no verão 2014–2024;
- `LANDSAT_8_INVERNO_CURVATURA_SEN_SLOPE.py`: taxa anual de mudança térmica no inverno 2014–2024.

> Observação metodológica: em parte dos scripts, a inclinação foi operacionalizada por regressão linear como aproximação prática da tendência (rotulada como “Sen slope”).

### 4.2.4 Grupo “SIGNIFICÂNCIA”

- `SIGNIFICANCIA_VERAO_MANN_KENDALL.py`: gera mapas binários de significância para verão (2000–2013 e 2014–2024);
- `SIGNIFICANCIA_INVERNO_MANN_KENDALL.py`: gera mapas binários de significância para inverno (2000–2013 e 2014–2024).

Critério adotado: `p < 0,05` = pixel com evidência estatística de mudança.

### 4.2.5 Grupo “RUPTURA TEMPORAL (PETTITT)”

- `TESTE_PETTITT_VERAO.py`: estima ano provável de ruptura na série média espacial de verão;
- `TESTE_PETTITT_INVERNO.py`: estima ano provável de ruptura na série média espacial de inverno.

### 4.2.6 Grupo “BOXPLOT POR AP”

- `BLOXSPOT_VERAO.py`: extrai amostras por AP e compara distribuição térmica entre 2000–2013 e 2014–2024 (verão);
- `BLOXSPOT_INVERNO.py`: mesmo procedimento para inverno.

---

## 5 ORDEM RECOMENDADA DE EXECUÇÃO

### 5.1 Fase GEE
1. `LANDSAT_5_7_VERAO.js`
2. `LANDSAT_5_7_INVERNO.js`
3. `LANDSAT_8_VERAO.js`
4. `LANDSAT_8_INVERNO.js`

### 5.2 Fase Colab
1. Scripts de mediana (`*_MEDIANA.py`)
2. Scripts de tendência (`*_TENDENCIA_MANN_KENDALL.py`)
3. Scripts de inclinação (`*_CURVATURA_SEN_SLOPE.py`)
4. Scripts de significância (`SIGNIFICANCIA_*`)
5. Scripts de ruptura (`TESTE_PETTITT_*`)
6. Scripts de boxplot (`BLOXSPOT_*`)

---

## 6 PADRÃO DE ORGANIZAÇÃO DOS DADOS NO GOOGLE DRIVE

Estrutura sugerida:

- `MESTRADO/01. DADOS/AP/`
- `MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/VERÃO/`
- `MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/INVERNO/`
- Pastas de saída específicas dos exports do GEE (verão/inverno, L5/7 e L8).

Recomendação: usar nomenclatura padronizada com ano explícito no nome do arquivo (`*_YYYY.tif`) para facilitar filtros e automação.

---

## 7 CRITÉRIOS DE QUALIDADE E REPRODUTIBILIDADE

a) Conferir CRS dos vetores e rasters antes de mascaramento espacial;
b) Revisar thresholds de nuvem e janelas sazonais por ano;
c) Validar presença de dados em anos críticos (resgate);
d) Ajustar caminhos de entrada/saída em todos os scripts Colab;
e) Documentar versão de bibliotecas em execução final;
f) Fixar semente aleatória quando houver amostragem para boxplot.

---

## 8 PRODUTOS TÉCNICOS ESPERADOS

- Mapas de mediana sazonal da LST;
- Mapas de tendência (Tau de Kendall);
- Mapas de inclinação temporal (°C/ano);
- Mapas de significância estatística (p < 0,05);
- Gráficos e tabelas de ruptura (Pettitt);
- Boxplots por AP e tabelas de comparação entre períodos.

---

## 9 LIMITAÇÕES METODOLÓGICAS

- Dependência da disponibilidade/qualidade de cenas Landsat por ano e estação;
- Diferenças entre sensores e cobertura de nuvens podem exigir ajustes anuais;
- A interpretação da inclinação como “Sen slope” deve observar a implementação adotada em cada script.

---

## 10 SUGESTÃO DE USO NA DISSERTAÇÃO (FORMATO ABNT)

Este README pode ser incorporado como:

- **APÊNDICE A — Protocolo computacional de processamento da LST no GEE e Colab**.

Modelo de citação textual sugerida:

> APÊNDICE A apresenta o protocolo de processamento digital e análise estatística aplicado à LST no município do Rio de Janeiro, abrangendo as etapas de extração orbital, composição sazonal, tendência temporal, significância e detecção de rupturas.

---

## 11 CONTATO E MANUTENÇÃO

Para manutenção do fluxo:

1. Atualizar paths e assets antes de cada nova execução;
2. Registrar alterações em versionamento (`git`);
3. Preservar padronização de nomenclatura entre anos/estações/sensores.
