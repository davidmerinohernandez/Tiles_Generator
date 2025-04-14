import requests  # Biblioteca para hacer solicitudes HTTP.
from PIL import Image  # Biblioteca para manipulación de imágenes.
import math  # Biblioteca para operaciones matemáticas.
import time  # Biblioteca para manejar tiempos y pausas.
from io import BytesIO  # Para manejar datos binarios en memoria.
import os  # Para manejar archivos y directorios.


"""
Script para obtener las imágenes de OpenStreetMap de la misma zona que la ortofoto del Ministerio utilizada.

Se hacen recortes dentro de los límites de la ortofoto y al nivel de zoom correspondiente para que las teselas
que se recorten representen exactamente la misma zona que las de la ortofoto.

Para ello, se establecen los límites y se hacen peticiones a OSM y se van guardando los recortes.

"""


# Directorio de salida para guardar las imágenes de los tiles descargados.
output_dir_map = "TEST10K/testB"
# Nivel de zoom (18 proporciona una alta resolución).
zoom = 18
# Tamaño de cada tile (256x256 píxeles). Lo necesario para CycleGAN
tile_size = 256

# Límites de coordenadas geográficas para el área determinada.
#Coordenadas de la foto de entrenamiento
west1 = -4.0226988379  # Longitud oeste.
south1 = 40.4981463071  # Latitud sur.
east1 = -3.8524226497  # Longitud este.
north1 = 40.5851819323  # Latitud norte.

#Coordenadas de la foto de test
west = -4.0214781955931835  # Longitud oeste.
south = 40.58124215847196  # Latitud sur.
east = -3.8531985514076004  # Longitud este.
north = 40.66851442222403  # Latitud norte.

# Crea el directorio de salida si no existe.
os.makedirs(output_dir_map, exist_ok=True)

# Función para convertir coordenadas geográficas (longitud y latitud) a índices de teselas.
def lonlat_to_tile(lon, lat, zoom):
    """
    Convierte coordenadas geográficas (longitud y latitud) a coordenadas de tesela (x, y) para un nivel de zoom específico.

    Parámetros:
    - lon: Longitud.
    - lat: Latitud.
    - zoom: Nivel de zoom.

    Retorna:
    - xtile, ytile: Índices de la tesela en el mapa.
    """
    n = 2.0 ** zoom  # Cantidad total de teselas por dimensión a este nivel de zoom.
    # Cálculo del índice de tesela en la dirección horizontal (x).
    xtile = int((lon + 180.0) / 360.0 * n)
    # Cálculo del índice de tesela en la dirección vertical (y).
    ytile = int((1.0 - math.log(math.tan(math.radians(lat)) + 1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * n)
    return xtile, ytile

# Obtener los índices de las teselas necesarias para cubrir el área de interés.
x_min, y_min = lonlat_to_tile(west, north, zoom)
x_max, y_max = lonlat_to_tile(east, south, zoom)

# Encabezado para la solicitud HTTP (User-Agent personalizado).
headers = {"User-Agent": "MiAplicacionPython/1.0"}

# Descargar y guardar las teselas del mapa de OpenStreetMap (OSM).
for x in range(x_min, x_max + 1):
    for y in range(y_min, y_max + 1):
        # URL para descargar el tile específico.
        url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
        # Realiza la solicitud GET para descargar el tile.
        response = requests.get(url, headers=headers, timeout=10)

        # Verifica si la solicitud fue exitosa (código de estado 200).
        if response.status_code == 200:
            # Cargar la imagen del tile a partir de los datos binarios recibidos.
            tile_img = Image.open(BytesIO(response.content))

            # Reamuestra la imagen para aumentar la resolución.
            new_size = (tile_size * 2, tile_size * 2)  # Aumenta el tamaño de 256x256 a 512x512.
            tile_img_resampled = tile_img.resize(new_size, Image.BILINEAR)

            # Nombre del archivo para guardar el tile.
            tile_filename = f"{output_dir_map}/map_{x}_{y}.png"
            # Guarda la imagen reamuestrada como archivo PNG.
            tile_img_resampled.save(tile_filename)
            print(f"Guardado tile de mapa: {tile_filename}")
        else:
            # Imprime un mensaje de error si no se pudo descargar el tile.
            print(f"Error al descargar tile: {x}, {y}")

        # Pausa breve para evitar sobrecargar el servidor.
        time.sleep(0.1)

print("Generación de dataset de mapas completada.")
