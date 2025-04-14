Repositorio utilizado para generar el dataset utlizado para el entrenamiento y test de los modelos CycleGAN, Pix2Pix y StyleGAN3.
Partiendo de una ortofoto de alta resolución (GeoTIFF), se extraen los límites en coordenadas de la foto.
Posteriormente, se recorta la foto teniendo en cuenta un tamaño y zoom de las subimágenes para poder generar el dataset de imágenes satelitales.
Para poder obtener las correspondientes imágenes en el dominio de mapa, utilizando las coordenadas, se recortan imágenes de la misma región y zoom
realizando peticiones a la web de OpenStreetMap.
Por último, para poder emparejarlas para Pix2Pix, en base a las coordenadas EPSG:4326, se unen en un dataset llamado "paired" las imágenes en formato
satelital y en formato mapa de la misma región.
