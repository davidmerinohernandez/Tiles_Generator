from PIL import Image
import os

input_dir = "C:/Users/david/PycharmProjects/tiles/trainA/trainA"
output_dir = "C:/Users/david/PycharmProjects/tiles/train_stylegan_10K"


"""

Script para redimensionar las imágenes a 512 píxeles. Necesario para StyleGAN3.

"""



# Crea el directorio de salida si no existe
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    # Procesa solo archivos con extensiones válidas
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        try:
            # Ruta completa del archivo
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # Abre la imagen
            with Image.open(input_path) as img:
                # Redimensiona la imagen
                img_resized = img.resize((512, 512), Image.BILINEAR)

                # Guarda la imagen en el directorio de salida
                img_resized.save(output_path)

            print(f"Procesada: {filename}")

        except Exception as e:
            print(f"Error al procesar {filename}: {e}")

