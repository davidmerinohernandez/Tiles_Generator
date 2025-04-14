import rasterio
from pyproj import Proj, Transformer


"""

Script para obtener las coordenadas límite de la ortofoto del Ministerio utilizada y así poder dividirla en base a coordenadas

"""



# Ruta a tu archivo de ortofoto GeoTIFF
ruta_ortofoto = r'C:\Users\david\PycharmProjects\tiles\PNOA_MA_OF_ETRS89_HU30_h25_0533_2.tif'

# Abrir el archivo GeoTIFF para obtener los límites
with rasterio.open(ruta_ortofoto) as src:
    bounds = src.bounds
    crs = src.crs  # Sistema de referencia espacial del archivo

    # Crear un transformador para convertir al sistema WGS84
    transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)

    # Transformar las coordenadas
    west, south = transformer.transform(bounds.left, bounds.bottom)
    east, north = transformer.transform(bounds.right, bounds.top)

# Formato requerido
print(f"# Coordenadas de la foto de entrenamiento")
print(f"west = {west}  # Longitud oeste.")
print(f"south = {south}  # Latitud sur.")
print(f"east = {east}  # Longitud este.")
print(f"north = {north}  # Latitud norte.")
