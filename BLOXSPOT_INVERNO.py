# 1. Instalação de dependências
!pip install fiona -q

import rasterio
from rasterio.mask import mask
import geopandas as gpd
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import numpy as np
import fiona
from google.colab import drive

# 2. Montar o Google Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

fiona.drvsupport.supported_drivers['KML'] = 'rw'

# 3. Caminhos (Verifique se o nome da pasta é MEDIANA ou MEDIANAS)
folder_path = r'/content/drive/MyDrive/MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/INVERNO'
kml_path = r'/content/drive/MyDrive/MESTRADO/01. DADOS/AP/APs_Rio.kml'

# 4. Carregar APs e preparar rótulos via "codap"
aps = gpd.read_file(kml_path, driver='KML')
# O codap no KML é a chave oficial (1, 2, 3, 4, 5)
aps['AP_Label'] = aps['codap'].apply(lambda x: f"AP {x}")

def extrair_dados_por_periodo(ano_inicio, ano_fim):
    dados_acumulados = []
    arquivos = [f for f in os.listdir(folder_path) if f.startswith('LST_INV_20') and f.endswith('.tif')]

    # Dicionário de contagem para diagnóstico da AP 5
    contagem_diagnostico = {f"AP {i}": 0 for i in range(1, 6)}

    for arquivo in arquivos:
        ano_str = "".join(filter(str.isdigit, arquivo))
        if not ano_str: continue
        ano = int(ano_str)

        if ano_inicio <= ano <= ano_fim:
            with rasterio.open(os.path.join(folder_path, arquivo)) as src:
                # Reprojeção para garantir que o polígono caia no lugar certo do raster
                aps_reproj = aps.to_crs(src.crs)

                for _, linha in aps_reproj.iterrows():
                    label = linha['AP_Label']
                    try:
                        out_image, _ = mask(src, [linha['geometry']], crop=True)
                        pixels = out_image[0].flatten()
                        pixels = pixels[~np.isnan(pixels)]
                        pixels = pixels[pixels > 0]

                        if len(pixels) > 0:
                            contagem_diagnostico[label] += len(pixels)

                            # Amostragem para manter o boxplot limpo e estatisticamente válido
                            if len(pixels) > 4000:
                                pixels = np.random.choice(pixels, 4000, replace=False)

                            for p in pixels:
                                dados_acumulados.append({'AP': label, 'LST': p})
                    except:
                        continue

    print(f"\n--- Relatório de Coleta ({ano_inicio}-{ano_fim}) ---")
    for ap, qtd in contagem_diagnostico.items():
        print(f"{ap}: {qtd} pixels encontrados.")

    return pd.DataFrame(dados_acumulados)

# 5. Processamento
print("Iniciando extração... Por favor, aguarde.")
df_base = extrair_dados_por_periodo(2000, 2013)
df_pos = extrair_dados_por_periodo(2014, 2024)

# 6. GERAÇÃO DO BOXPLOT E RESUMO
if not df_base.empty and not df_pos.empty:
    # --- GRÁFICOS ---
    plt.rcParams.update({'font.size': 12})
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharey=True)
    ordem_aps = ['AP 1', 'AP 2', 'AP 3', 'AP 4', 'AP 5']

    sns.boxplot(x='AP', y='LST', data=df_base, ax=ax1, order=ordem_aps, color='skyblue', showfliers=True)
    ax1.set_title('Variabilidade Térmica (TSC) Inverno: 2000-2013', fontweight='bold')
    ax1.set_ylabel('Temperatura (°C)')
    ax1.grid(axis='y', alpha=0.3)

    sns.boxplot(x='AP', y='LST', data=df_pos, ax=ax2, order=ordem_aps, color='salmon', showfliers=True)
    ax2.set_title('Variabilidade Térmica (TSC) Inverno: 2014-2024', fontweight='bold')
    ax2.set_ylabel('Temperatura (°C)')
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.show()

    # --- RESUMO ESTATÍSTICO ---
    m1 = df_base.groupby('AP')['LST'].median()
    m2 = df_pos.groupby('AP')['LST'].median()

    # Garantir que todas as APs apareçam no resumo, mesmo que vazias
    resumo = pd.DataFrame(index=ordem_aps)
    resumo['2000-13'] = m1
    resumo['2014-24'] = m2
    resumo['Aumento'] = resumo['2014-24'] - resumo['2000-13']

    print("\n" + "="*40)
    print("   RESUMO PARA A DISSERTAÇÃO (Medianas)")
    print("="*40)
    print(resumo.round(4))
    print("="*40)

else:
    print("Erro: Dados não encontrados. Verifique os caminhos e arquivos.")