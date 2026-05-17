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
path_lst = '/content/drive/MyDrive/MESTRADO/01. DADOS/00.DADOS_ARCGIS_MAPAS/VERAO_2014_2024/VERAO_MEDIANA_2014_2024.tif'
path_mag = '/content/drive/MyDrive/MESTRADO/01. DADOS/00.DADOS_ARCGIS_MAPAS/VERAO_2014_2024/VERAO_TEN_SEN_SLOPE_2014_2024.tif'
path_sig = '/content/drive/MyDrive/MESTRADO/01. DADOS/02.ANO A ANO MEDIANAS/SEM EXCLUSÃO/VERÃO/Mapa_Significancia_Verao_2014_2024.tif'
path_vet = '/content/drive/MyDrive/MESTRADO/01. DADOS/RESULTADOS_ESTATISTICOS/PONTOS/pontos.shp'
folder_output = '/content/drive/MyDrive/MESTRADO/01. DADOS/RESULTADOS_ESTATISTICOS/VERAO_2014_2024/'

# --- ETAPA 2: PROCESSAMENTO GEOGRÁFICO (BUFFER E CRS) ---
print("\n--- ETAPA 2: Tratando Projeções ---")
gdf_pontos = gpd.read_file(path_vet)

if gdf_pontos.crs is None:
    gdf_pontos.set_crs(epsg=31983, inplace=True)

gdf_pontos['original_geometry'] = gdf_pontos.geometry
distancia_metros = 500
gdf_pontos['geometry'] = gdf_pontos.geometry.buffer(distancia_metros)

with rasterio.open(path_sig) as src_sig:
    crs_raster = src_sig.crs
    gdf_pontos = gdf_pontos.to_crs(crs_raster)
    transform_sig = src_sig.transform

# --- ETAPA 3: EXTRAÇÃO ZONAL FILTRADA ---
print("\n--- ETAPA 3: Extraindo valores (Mantendo todos os pontos) ---")
resultados = []
geometrias_finais = []

with rasterio.open(path_sig) as sig_src, \
     rasterio.open(path_lst) as lst_src, \
     rasterio.open(path_mag) as mag_src:

    for idx, row in gdf_pontos.iterrows():
        # Valores padrão caso não haja significância
        lst_mediana = np.nan
        mag_mediana = np.nan
        p_count = 0
        dist_calc = np.nan
        c_x, c_y = np.nan, np.nan
        geom_ponto = row['original_geometry'] # Mantém o ponto original no shape se falhar

        try:
            out_img_sig, out_transform = mask(sig_src, [row.geometry], crop=True)
            out_img_lst, _ = mask(lst_src, [row.geometry], crop=True)
            out_img_mag, _ = mask(mag_src, [row.geometry], crop=True)

            valid_mask = (out_img_sig[0] == 1) & (out_img_lst[0] > -50)
            lst_values = out_img_lst[0][valid_mask]
            mag_values = out_img_mag[0][valid_mask]

            if len(lst_values) > 0:
                lst_mediana = np.nanmedian(lst_values)
                mag_mediana = np.nanmedian(mag_values)
                p_count = len(lst_values)

                rows, cols = np.where(valid_mask)
                xs, ys = rasterio.transform.xy(out_transform, rows, cols)
                centroid_sig = Point(np.mean(xs), np.mean(ys))

                dist_calc = row['original_geometry'].distance(centroid_sig)
                c_x, c_y = centroid_sig.x, centroid_sig.y
                geom_ponto = centroid_sig
            else:
                print(f"Nota: {row.get('Name', idx)} sem significância. Valores zerados.")

        except Exception as e:
            print(f"Erro no ponto {idx}: {e}")

        resultados.append({
            'Name': row['Name'] if 'Name' in row else f"Ponto_{idx}",
            'lst_verao': lst_mediana,
            'magnitude_slope': mag_mediana,
            'pixels_sig_count': p_count,
            'dist_pixel_sig': dist_calc,
            'coord_x_sig': c_x,
            'coord_y_sig': c_y
        })
        geometrias_finais.append(geom_ponto)

# --- ETAPA 4: DATAFRAME E CLASSIFICAÇÃO ---
df_final = pd.DataFrame(resultados)

# Preenche com 0 onde é NaN para as contagens e magnitudes (opcional, NaN é melhor para estatística)
# df_final['pixels_sig_count'] = df_final['pixels_sig_count'].fillna(0)

# Classes (O pd.cut lidará com NaNs automaticamente, deixando-os vazios)
bins_temp = [12, 20, 25, 30, 35, 40, 45, 100]
labels_temp = ['12-20', '20.1-25', '25.1-30', '30.1-35', '35.1-40', '40.1-45', '>45']
df_final['classe_temp'] = pd.cut(df_final['lst_verao'], bins=bins_temp, labels=labels_temp)

bins_mag = [-2.18, -1, -0.4, 0, 0.4, 1, 3]
labels_mag = ['-2.18 a -1', '-0.99 a -0.4', '-0.39 a 0', '0.1 a 0.4', '0.41 a 1', '1.1 a 3']
df_final['classe_mag'] = pd.cut(df_final['magnitude_slope'], bins=bins_mag, labels=labels_mag)

# --- ETAPA 5: SALVAMENTO ---
print("\n--- ETAPA 5: Salvando Resultados ---")

# Remove linhas totalmente vazias de gráficos para não dar erro
df_plot = df_final.dropna(subset=['lst_verao'])

if not df_plot.empty:
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_plot, x='classe_temp', y='magnitude_slope', hue='classe_temp', palette='Spectral_r', legend=False)
    plt.title('Magnitude vs LST (Apenas áreas com Significância)')
    plt.show()

gdf_sig_extraida = gpd.GeoDataFrame(df_final, geometry=geometrias_finais, crs=crs_raster)
gdf_sig_extraida.to_file(f'{folder_output}pixels_ZONAL_verao_COMPLETO.shp')
df_final.to_csv(f'{folder_output}TABELA_FINAL_ZONAL_VERAO_COMPLETA.csv', index=False, sep=';', encoding='utf-8-sig')

print(f"Concluído! Total de pontos processados: {len(df_final)}")
display(df_final)