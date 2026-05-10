# --- 1. Instalação das bibliotecas necessárias ---
!pip install pymannkendall rasterio

# --- 2. Bibliotecas ---
import os
import numpy as np
import rasterio
import pymannkendall as mk
from glob import glob
import matplotlib.pyplot as plt
from google.colab import drive

# --- 3. Montar o Google Drive ---
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- 4. Caminho dos dados ---
input_folder = '/content/drive/MyDrive/MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/INVERNO'

# --- 5. Função de Processamento de Significância ---
def processar_significancia_independente(ano_ini, ano_fim, sufixo_saida):
    # Listar e filtrar arquivos
    arquivos = sorted(glob(os.path.join(input_folder, '*.tif')))
    files_periodo = []

    for f in arquivos:
        # Extrai apenas os números do nome do arquivo para identificar o ano
        nome_arq = os.path.basename(f)
        ano_str = "".join(filter(str.isdigit, nome_arq))
        if ano_str:
            ano = int(ano_str)
            if ano_ini <= ano <= ano_fim:
                files_periodo.append(f)

    if not files_periodo:
        print(f"Atenção: Nenhum arquivo encontrado para o período {ano_ini}-{ano_fim}")
        return None

    print(f"\nIniciando Período {ano_ini}-{ano_fim} ({len(files_periodo)} imagens)")

    # Carregar metadados e criar o stack (pilha)
    with rasterio.open(files_periodo[0]) as src:
        meta = src.meta.copy()
        height, width = src.height, src.width

    stack = []
    for f in files_periodo:
        with rasterio.open(f) as src:
            data = src.read(1).astype(np.float32)
            data[data <= 0] = np.nan  # Tratamento de NoData
            stack.append(data)

    stack_array = np.stack(stack, axis=0)
    p_map = np.full((height, width), np.nan, dtype=np.float32)

    # Cálculo Pixel a Pixel
    for i in range(height):
        for j in range(width):
            pixel_series = stack_array[:, i, j]
            # Remove NaNs para o teste
            clean_series = pixel_series[~np.isnan(pixel_series)]

            # O Mann-Kendall precisa de pelo menos 4-5 anos para ter validade
            if len(clean_series) > 5:
                try:
                    # Executa o teste e extrai o p-valor
                    res = mk.original_test(clean_series)
                    p_map[i, j] = res.p
                except:
                    continue

        # Barra de progresso simples
        if i % 100 == 0:
            print(f"Linha {i}/{height} processada...")

    # Criar Mapa Binário de Significância (p < 0.05)
    # 1 = Mudança Significativa | 0 = Mudança não comprovada
    sig_map = np.where(p_map < 0.05, 1, 0).astype(np.uint8)
    sig_map[np.isnan(p_map)] = 0  # Garante NoData como 0

    # Salvar o GeoTIFF final
    output_path = os.path.join(input_folder, f'Mapa_Significancia_ Inverno_{sufixo_saida}.tif')
    meta.update(dtype=rasterio.uint8, count=1, nodata=0)

    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(sig_map, 1)

    print(f"Arquivo salvo com sucesso: {output_path}")
    return sig_map

# --- 6. Execução dos dois blocos independentes ---

# Mapa do Período 1 (2000-2013)
mapa_sig_p1 = processar_significancia_independente(2000, 2013, "2000_2013")

# Mapa do Período 2 (2014-2024)
mapa_sig_p2 = processar_significancia_independente(2014, 2024, "2014_2024")

# --- 7. Visualização Final Comparativa ---
if mapa_sig_p1 is not None and mapa_sig_p2 is not None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    ax1.imshow(mapa_sig_p1, cmap='RdYlGn_r')
    ax1.set_title(f"Significância Estatística Inverno (2000-2013)\n(p < 0.05)")

    ax2.imshow(mapa_sig_p2, cmap='RdYlGn_r')
    ax2.set_title(f"Significância Estatística Inverno (2014-2024)\n(p < 0.05)")

    plt.tight_layout()
    plt.show()