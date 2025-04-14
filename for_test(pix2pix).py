import os
import shutil
import random

"""

Script para dataset con paired, train y test

"""



# Definir las rutas
dataset_path = "./dataset"
paired_path = os.path.join(dataset_path, "paired")
train_path = os.path.join(dataset_path, "train")
test_path = os.path.join(dataset_path, "test")

# Crear las carpetas de destino si no existen
os.makedirs(train_path, exist_ok=True)
os.makedirs(test_path, exist_ok=True)

# Obtener la lista de archivos en la carpeta paired
paired_files = os.listdir(paired_path)

# Barajar las imágenes para seleccionar aleatoriamente
random.shuffle(paired_files)

# Seleccionar 1000 imágenes para entrenamiento y 1000 para test
train_files = paired_files[:1000]
test_files = paired_files[1000:2000]

# Copiar las imágenes seleccionadas a las carpetas de destino
for file_name in train_files:
    src = os.path.join(paired_path, file_name)
    dst = os.path.join(train_path, file_name)
    shutil.copy(src, dst)

for file_name in test_files:
    src = os.path.join(paired_path, file_name)
    dst = os.path.join(test_path, file_name)
    shutil.copy(src, dst)

print(f"Se han copiado {len(train_files)} imágenes a la carpeta de entrenamiento (train).")
print(f"Se han copiado {len(test_files)} imágenes a la carpeta de test.")
