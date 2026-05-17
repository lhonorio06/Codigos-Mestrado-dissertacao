import rasterio
from rasterio.mask import mask
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import Point
from google.colab import drive

# --- ETAPA 1: CONEXÃO E CAMINHOS ---
print("--- ETAPA 1: Conectando ao Google Drive ---")
drive.mount('/content/drive', force_remount=True)

# Definição dos caminhos
path_lst = '/content/drive/MyDrive/MESTRADO/01. DADOS/00.DADOS_ARCGIS_MAPAS/INVERNO_2014_2024/Cópia de mediana_lst_inverno_2014_2024.tif'
path_mag = '/content/drive/MyDrive/MESTRADO/01. DADOS/00.DADOS_ARCGIS_MAPAS/INVERNO_2014_2024/Cópia de Curvatura_Sen_Inverno_L8.tif'
path_sig = '/content/drive/MyDrive/MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/INVERNO/Mapa_Significancia_ Inverno_2014_2024.tif'
path_vet = '/content/drive/MyDrive/MESTRADO/01. DADOS/RESULTADOS_ESTATISTICOS/PONTOS/pontos.shp'
folder_output = '/content/drive/MyDrive/MESTRADO/01. DADOS/RESULTADOS_ESTATISTICOS/INVERNO_2014_2024/'

# --- ETAPA 2: PROCESSAMENTO GEOGRÁFICO (BUFFER E CRS) ---
print("\n--- ETAPA 2: Tratando Projeções e Áreas de Influência ---")
gdf_pontos = gpd.read_file(path_vet)

# Define o CRS original dos pontos (SIRGAS 2000 / UTM 23S) caso não esteja definido
if gdf_pontos.crs is None:
    gdf_pontos.set_crs(epsg=31983, inplace=True)

# Armazenamos a geometria original (pontos) para calcular distâncias depois
gdf_pontos['original_geometry'] = gdf_pontos.geometry

# Criamos o buffer de 500 metros (preciso, pois o CRS está em metros)
distancia_metros = 500
gdf_pontos['geometry'] = gdf_pontos.geometry.buffer(distancia_metros)

# Projetamos para o CRS do Raster (WGS 84)
with rasterio.open(path_sig) as src_sig:
    crs_raster = src_sig.crs
    gdf_pontos = gdf_pontos.to_crs(crs_raster)
    transform_sig = src_sig.transform

# --- ETAPA 3: EXTRAÇÃO ZONAL FILTRADA ---
print("\n--- ETAPA 3: Extraindo valores significativos dentro do Buffer ---")
resultados = []
geometrias_pixels_sig = []

with rasterio.open(path_sig) as sig_src, \
     rasterio.open(path_lst) as lst_src, \
     rasterio.open(path_mag) as mag_src:

    for idx, row in gdf_pontos.iterrows():
        try:
            # Recorte dos Rasters pelo Buffer
            out_img_sig, out_transform = mask(sig_src, [row.geometry], crop=True)
            out_img_lst, _ = mask(lst_src, [row.geometry], crop=True)
            out_img_mag, _ = mask(mag_src, [row.geometry], crop=True)

            # Máscara: Apenas pixels significativos (1) e com dados válidos
            valid_mask = (out_img_sig[0] == 1) & (out_img_lst[0] > -50)

            lst_values = out_img_lst[0][valid_mask]
            mag_values = out_img_mag[0][valid_mask]

            if len(lst_values) > 0:
                # Calculamos a mediana dos pixels significativos dentro do buffer
                lst_mediana = np.nanmedian(lst_values)
                mag_mediana = np.nanmedian(mag_values)

                # Identificamos a coordenada do pixel significativo mais próximo do centro para o Shapefile
                rows, cols = np.where(valid_mask)
                xs, ys = rasterio.transform.xy(out_transform, rows, cols)

                # Para manter compatibilidade com seu primeiro código (distância ao pixel sig)
                # Calculamos a distância do ponto original ao centro do conjunto de pixels significativos
                centroid_sig = Point(np.mean(xs), np.mean(ys))
                dist_calc = row['original_geometry'].distance(centroid_sig) # Nota: Aproximação em graus

                resultados.append({
                    'Name': row['Name'] if 'Name' in row else f"Ponto_{idx}",
                    'lst_inverno': lst_mediana,
                    'magnitude_slope': mag_mediana,
                    'pixels_sig_count': len(lst_values),
                    'dist_pixel_sig': dist_calc,
                    'coord_x_sig': centroid_sig.x,
                    'coord_y_sig': centroid_sig.y
                })
                geometrias_pixels_sig.append(centroid_sig)
            else:
                print(f"Ponto {row.get('Name', idx)}: Sem pixels significativos no raio de {distancia_metros}m")
        except Exception as e:
            continue

# --- ETAPA 4: DATAFRAME E CLASSIFICAÇÃO ---
df_final = pd.DataFrame(resultados)

# Classes de Temperatura
bins_temp = [12, 20, 25, 30, 35, 40, 45, 100]
labels_temp = ['12-20', '20.1-25', '25.1-30', '30.1-35', '35.1-40', '40.1-45', '>45']
df_final['classe_temp'] = pd.cut(df_final['lst_inverno'], bins=bins_temp, labels=labels_temp)

# Classes de Magnitude
bins_mag = [-2.18, -1, -0.4, 0, 0.4, 1, 3]
labels_mag = ['-2.18 a -1', '-0.99 a -0.4', '-0.39 a 0', '0.1 a 0.4', '0.41 a 1', '1.1 a 3']
df_final['classe_mag'] = pd.cut(df_final['magnitude_slope'], bins=bins_mag, labels=labels_mag)

# --- ETAPA 5: GERAÇÃO DE IMAGENS E SALVAMENTO ---
print("\n--- ETAPA 5: Gerando Gráficos e Arquivos de Saída ---")

# 1. Boxplot (Magnitude vs LST)
plt.figure(figsize=(12, 6))
sns.boxplot(data=df_final, x='classe_temp', y='magnitude_slope', hue='classe_temp', palette='Spectral_r', legend=False)
plt.title('Distribuição da Magnitude por Classe de LST (Zonal Inverno)')
plt.grid(axis='y', alpha=0.3)
plt.show()

# 2. Histograma de Distâncias
plt.figure(figsize=(10, 6))
sns.histplot(df_final['dist_pixel_sig'], bins=20, kde=True)
plt.title('Distância das Infraestruturas aos Clusters de Significância')
plt.xlabel('Distância (Graus)')
plt.show()

# 3. Salvando Shapefile (Localização dos pixels significativos extraídos)
gdf_sig_extraida = gpd.GeoDataFrame(df_final, geometry=geometrias_pixels_sig, crs=crs_raster)
gdf_sig_extraida.to_file(f'{folder_output}pixels_significancia_ZONAL_inverno.shp')

# 4. Salvando Tabela CSV
df_final.to_csv(f'{folder_output}TABELA_FINAL_ZONAL_INVERNO_2014_2024.csv', index=False, sep=';', encoding='utf-8-sig')

print(f"\nFINALIZADO!")
print(f"Tabela: {folder_output}TABELA_FINAL_ZONAL_INVERNO_2014_2024.csv")
print(f"Vetor: {folder_output}pixels_significancia_ZONAL_inverno.shp")

# Exibição Final
display(df_final)