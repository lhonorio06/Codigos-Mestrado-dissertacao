import os
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import re

# 1. Função Matemática do Teste de Pettitt
def pettitt_test(data):
    n = len(data)
    k = np.zeros(n)
    for i in range(n):
        k[i] = np.sum(np.sign(data[i] - data))
    U = np.cumsum(k)
    loc = np.argmax(np.abs(U))
    K_max = np.max(np.abs(U))
    p_value = 2 * np.exp((-6 * (K_max**2)) / (n**3 + n**2))
    return loc, p_value, U

# 2. Processamento para a pasta de INVERNO
def get_annual_data_inverno(folder_path):
    # Procura especificamente pelo seu novo padrão de nome
    files = sorted([f for f in os.listdir(folder_path)
                    if 'LST_INV_20' in f and f.endswith('.tif')])

    if not files:
        print("Aviso: Nenhum arquivo 'LST_INV_20*.tif' encontrado!")
        return pd.DataFrame()

    data_list = []
    years = []

    for file in files:
        # Extrai o ano (os 4 dígitos após '20')
        match = re.search(r'20\d{2}', file)
        if match:
            year_int = int(match.group())
            years.append(year_int)

            full_path = os.path.join(folder_path, file)
            with rasterio.open(full_path) as src:
                img = src.read(1)
                # Tratamento de NoData
                img = np.where(img == src.nodata, np.nan, img)
                # Opcional: Se os dados estiverem em Kelvin, pode converter para Celsius aqui
                # img = img - 273.15
                data_list.append(np.nanmean(img))

    return pd.DataFrame({'Ano': years, 'Media': data_list}).sort_values('Ano')

# --- CONFIGURAÇÃO DE CAMINHO ---
caminho_inverno = '/content/drive/MyDrive/MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/INVERNO'

# --- EXECUÇÃO ---
df_inverno = get_annual_data_inverno(caminho_inverno)

if not df_inverno.empty:
    # Aplicação do teste
    idx, p_val, U_stats = pettitt_test(df_inverno['Media'].values)
    ano_ruptura = df_inverno.iloc[idx]['Ano']

    # --- VISUALIZAÇÃO GRÁFICA ---
    plt.figure(figsize=(18, 9))
    ax = plt.gca()

    # Plotagem principal (Cor roxa/azulada para inverno)
    plt.plot(df_inverno['Ano'], df_inverno['Media'], marker='o', ls='-', color='#6a3d9a',
             linewidth=2.5, markersize=9, label='Média LST Inverno')

    # Linha de Ruptura
    plt.axvline(x=ano_ruptura, color='#e31a1c', linestyle='--', linewidth=3,
                label=f'Ponto de Ruptura ({ano_ruptura})')

    # Configurações do Eixo X: Todos os anos
    plt.xticks(df_inverno['Ano'], rotation=45, fontsize=10)

    # Configurações do Eixo Y: Escala bem detalhada
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=25))

    # Estética
    plt.title(f'Teste de Pettitt: Série Temporal de Inverno\n(P-valor: {p_val:.4f})', fontsize=16, fontweight='bold')
    plt.xlabel('Ano', fontsize=13)
    plt.ylabel('Temperatura / Valor Médio LST', fontsize=13)
    plt.legend(loc='upper left', fontsize=11)
    plt.grid(True, which='both', linestyle=':', alpha=0.6)

    # Adicionar os valores numéricos acima de cada ponto
    for i, txt in enumerate(df_inverno['Media']):
        plt.annotate(f"{txt:.2f}", (df_inverno['Ano'].iloc[i], df_inverno['Media'].iloc[i]),
                     textcoords="offset points", xytext=(0,12), ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.show()

    # Tabela detalhada no console
    print("\n--- RESULTADOS INVERNO ---")
    print(df_inverno.to_string(index=False))
else:
    print("Erro crítico: O DataFrame não foi gerado. Verifique os nomes dos arquivos no Drive.")