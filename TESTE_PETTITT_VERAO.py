import os
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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

# 2. Processamento filtrando apenas "LST_20"
def get_annual_data_filtered(folder_path):
    files = sorted([f for f in os.listdir(folder_path)
                    if f.startswith('LST_20') and f.endswith('.tif')])

    data_list = []
    years = []

    for file in files:
        year_str = file.split('LST_')[1][:4]
        years.append(int(year_str))

        full_path = os.path.join(folder_path, file)
        with rasterio.open(full_path) as src:
            img = src.read(1)
            img = np.where(img == src.nodata, np.nan, img)
            # Caso os dados precisem de fator de escala (ex: Kelvin para Celsius), ajuste aqui
            data_list.append(np.nanmean(img))

    return pd.DataFrame({'Ano': years, 'Media': data_list}).sort_values('Ano')

# --- CONFIGURAÇÃO DE CAMINHO ---
caminho_drive = '/content/drive/MyDrive/MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/VERÃO'

# --- EXECUÇÃO ---
df_final = get_annual_data_filtered(caminho_drive)
idx, p_val, U_stats = pettitt_test(df_final['Media'].values)
ano_ruptura = df_final.iloc[idx]['Ano']

# --- VISUALIZAÇÃO MELHORADA ---
plt.figure(figsize=(16, 8)) # Aumentamos a largura para caber todos os anos

ax = plt.gca()

# Plotagem principal
plt.plot(df_final['Ano'], df_final['Media'], marker='o', ls='-', color='#1f77b4', linewidth=2, markersize=8, label='Média LST')

# Linha de Ruptura
plt.axvline(x=ano_ruptura, color='red', linestyle='--', linewidth=2, label=f'Ruptura Detectada ({ano_ruptura})')

# Configurações do Eixo X: Mostrar TODOS os anos
plt.xticks(df_final['Ano'], rotation=45)

# Configurações do Eixo Y: Mais detalhes nos valores
# O locator MaxNLocator(20) tenta colocar até 20 divisões no eixo Y
ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=20))

# Estética
plt.title(f'Análise de Ruptura de Pettitt - Verão\n(P-valor: {p_val:.4f})', fontsize=14, fontweight='bold')
plt.xlabel('Ano', fontsize=12)
plt.ylabel('Valor Médio (LST)', fontsize=12)
plt.legend(loc='best')
plt.grid(True, which='both', linestyle='--', alpha=0.5)

# Adicionar os valores numéricos acima de cada ponto para facilitar a leitura
for i, txt in enumerate(df_final['Media']):
    plt.annotate(f"{txt:.2f}", (df_final['Ano'].iloc[i], df_final['Media'].iloc[i]),
                 textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)

plt.tight_layout()
plt.show()

# Exibição da tabela para conferência acadêmica
print("\n--- TABELA DE DADOS REPRODUZÍVEL ---")
print(df_final.to_string(index=False))