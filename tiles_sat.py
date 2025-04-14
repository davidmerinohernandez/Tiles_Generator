import rasterio  # Biblioteca para leer y procesar datos geoespaciales (imágenes satelitales).
from rasterio.windows import Window  # Para definir subregiones (ventanas) de la imagen.
from PIL import Image  # Biblioteca para manipulación de imágenes.
import os  # Para manejo de archivos y directorios.
import numpy as np  # Biblioteca para operaciones numéricas.


"""
Script utilizado para recortar la ortofoto en teselas más pequeñas y poder posteriormente emparejarlas con las
teselas que se recortan de OSM y que representan las mismas zonas.

El tamaño de la imagen es de 256x256, pues es lo necesario para entrenar los modelos.

"""




# Ruta de la imagen satelital en formato TIFF.
satellite_image_path = "PNOA_MA_OF_ETRS89_HU30_h25_0533_2.tif"
# Directorio de salida donde se guardarán los tiles generados.
output_dir_satellite = "TEST10K/testA"
# Tamaño de cada tile en píxeles.
tile_size = 256

# Crea el directorio de salida si no existe.
os.makedirs(output_dir_satellite, exist_ok=True)


def normalize_tile(tile):
    """
    Normaliza los valores de los píxeles en la tesela (tile) para que estén en el rango [0, 255].
    Esto se hace para mejorar la visualización de las imágenes al guardarlas en formato PNG.

    Parámetros:
    - tile: Array NumPy con los datos de la tesela.

    Retorna:
    - Tesela normalizada como un array de enteros de 8 bits.
    """
    min_val = tile.min()  # Valor mínimo en la tesela.
    max_val = tile.max()  # Valor máximo en la tesela.

    # Normaliza los valores de la tesela si hay una diferencia entre mínimo y máximo.
    if max_val > min_val:
        tile = (tile - min_val) / (max_val - min_val) * 255

    # Asegura que los valores estén en el rango [0, 255].
    tile = np.clip(tile, 0, 255)
    return tile.astype(np.uint8)


def generate_satellite_dataset(image_path):
    """
    Genera un dataset de tiles a partir de una imagen satelital.
    Divide la imagen en subregiones de tamaño fijo y guarda cada tile como una imagen PNG.

    Parámetros:
    - image_path: Ruta de la imagen satelital (formato TIFF).
    """
    # Abre el archivo TIFF utilizando rasterio.
    with rasterio.open(image_path) as src_ds:
        width = src_ds.width  # Ancho de la imagen.
        height = src_ds.height  # Alto de la imagen.

        # Recorre la imagen por secciones de tamaño `tile_size`.
        for i in range(0, width, tile_size):
            for j in range(0, height, tile_size):
                # Define una ventana (subregión) de la imagen con las coordenadas actuales.
                window = Window(i, j, tile_size, tile_size)

                # Lee los datos de la imagen dentro de la ventana.
                tile = src_ds.read(window=window)

                # Verifica que la tesela tenga el tamaño adecuado.
                if tile.shape[1] < tile_size or tile.shape[2] < tile_size:
                    continue  # Omite teselas incompletas en los bordes de la imagen.

                # Normaliza los datos de la tesela para convertirlos al rango [0, 255].
                tile = normalize_tile(tile)

                # Crea una imagen PIL a partir del array Numpy transpuesto.
                # Se usa RGB asumiendo que la imagen tiene 3 bandas (rojo, verde, azul).
                tile_img = Image.fromarray(tile.transpose(1, 2, 0), 'RGB')

                # Define el nombre del archivo para la tesela.
                tile_filename = f"{output_dir_satellite}/sat_{i}_{j}.png"

                # Guarda la tesela como una imagen PNG.
                tile_img.save(tile_filename)
                print(f"Guardado tile de satélite: {tile_filename}")


generate_satellite_dataset(satellite_image_path)
print("Generación de dataset satelital completada.")
