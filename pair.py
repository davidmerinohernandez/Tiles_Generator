import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform, calculate_default_transform
from PIL import Image
import math
import os
import numpy as np


"""
Script utilizado para emparejar las teselas recortadas de OSM y de la ortofoto en pares que representen la misma zona.
Esto es necesario para poder entrenar el modelo Pix2Pix, pues necesita fotos emparejadas de la misma pero de diferente 
dominio (mapa y satélite).

Para emparejarlas, se utilizan las coordenadas asociadas a cada subimagen. Las coordenadas EPSG:4326.

"""

# Configuración
satellite_image_path = "PNOA_MA_OF_ETRS89_HU30_h25_0533_2.tif"
output_dir_paired = "TEST10K/test"
output_dir_map = "TEST10K/testB"
zoom = 18  # Nivel de zoom ajustado para mayor resolución
tile_size = 256

os.makedirs(output_dir_paired, exist_ok=True)

# Función para convertir tesela a coordenadas geográficas (EPSG:4326)
def tile_to_lonlat(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon = xtile / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ytile / n))))
    return lon, lat

# Calcular la resolución de la imagen satelital en metros por píxel
def calculate_satellite_resolution(sat_path):
    with rasterio.open(sat_path) as sat_ds:
        resolution = sat_ds.res[0]
        return resolution

# Reamuestrar los tiles del mapa para igualar la resolución de la imagen satelital
def resample_map_tile(map_img, target_resolution, current_zoom, target_zoom):
    scale_factor = 2 ** (target_zoom - current_zoom)
    new_size = (int(map_img.width * scale_factor), int(map_img.height * scale_factor))
    return map_img.resize(new_size, Image.BILINEAR)

# Crear los pares de imágenes
def create_paired_dataset():
    sat_resolution = calculate_satellite_resolution(satellite_image_path)

    with rasterio.open(satellite_image_path) as sat_ds:
        sat_crs = sat_ds.crs
        sat_bounds = sat_ds.bounds

        for filename in os.listdir(output_dir_map):
            if filename.endswith(".png"):
                parts = filename.replace(".png", "").split("_")
                x_tile = int(parts[1])
                y_tile = int(parts[2])

                # Convertir el identificador del tile a coordenadas geográficas (EPSG:4326)
                west, north = tile_to_lonlat(x_tile, y_tile, zoom)
                east, south = tile_to_lonlat(x_tile + 1, y_tile + 1, zoom)

                try:
                    # Reproyectar las coordenadas a la proyección de la imagen satelital
                    west, south = transform("EPSG:4326", sat_crs, [west], [south])
                    east, north = transform("EPSG:4326", sat_crs, [east], [north])
                    west, south, east, north = west[0], south[0], east[0], north[0]

                    # Verificar si las coordenadas están dentro de los límites de la imagen satelital
                    if (west < sat_bounds.left or east > sat_bounds.right or
                        south < sat_bounds.bottom or north > sat_bounds.top):
                        print(f"Tile fuera de límites: {filename}")
                        continue

                    # Extraer el tile correspondiente de la imagen satelital
                    window = from_bounds(west, south, east, north, sat_ds.transform)
                    sat_tile = sat_ds.read(window=window)

                    if sat_tile.size == 0:
                        print(f"Tile vacío: {filename}")
                        continue

                    # Normalizar y crear la imagen del tile satelital
                    sat_tile = sat_tile[:3, :, :]
                    sat_tile = (sat_tile - sat_tile.min()) / (sat_tile.max() - sat_tile.min()) * 255
                    sat_tile = sat_tile.clip(0, 255).astype("uint8")
                    sat_img = Image.fromarray(sat_tile.transpose(1, 2, 0), "RGB")

                    # Cargar el tile de mapa y reamuestrarlo
                    map_img = Image.open(os.path.join(output_dir_map, filename))
                    target_zoom = zoom + int(math.log2(sat_resolution / (156543.03 / (2 ** zoom))))
                    map_img_resampled = resample_map_tile(map_img, sat_resolution, zoom, target_zoom)

                    # Redimensionar la imagen del mapa al tamaño del tile de satélite
                    map_img_resampled = map_img_resampled.resize(sat_img.size, Image.BILINEAR)

                    # Crear la imagen emparejada
                    paired_img = Image.new("RGB", (sat_img.width * 2, sat_img.height))
                    paired_img.paste(map_img_resampled, (0, 0))
                    paired_img.paste(sat_img, (sat_img.width, 0))

                    paired_filename = os.path.join(output_dir_paired, f"paired_{x_tile}_{y_tile}.png")
                    paired_img.save(paired_filename)
                    print(f"Guardado par de imágenes: {paired_filename}")

                except Exception as e:
                    print(f"Error al procesar el tile {filename}: {e}")

create_paired_dataset()
print("Generación de dataset emparejado completada.")
