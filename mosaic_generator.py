from PIL import Image
import os
import numpy as np
import colorsys
from sklearn.cluster import KMeans

def calculate_average_color(image_path):
    """Calcule la couleur moyenne d'une image."""
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        pixels = np.array(img)
        avg_color = np.mean(pixels, axis=(0, 1))
        return tuple(avg_color.astype(int))

def calculate_luminance(color):
    """Calcule la luminance d'une couleur RGB."""
    r, g, b = color
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def calculate_saturation(color):
    """Calcule la saturation d'une couleur RGB."""
    r, g, b = color
    _, s, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return s

def calculate_dominant_color(image_path, n_colors=1):
    """Calcule la couleur dominante d'une image en utilisant K-means."""
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        pixels = np.array(img).reshape(-1, 3)
        kmeans = KMeans(n_clusters=n_colors, random_state=0).fit(pixels)
        dominant_color = kmeans.cluster_centers_[0]
        return tuple(dominant_color.astype(int))

def sort_images_by_luminance(image_paths):
    """Trie les images par luminance moyenne."""
    images = []
    for image_path in image_paths:
        avg_color = calculate_average_color(image_path)
        luminance = calculate_luminance(avg_color)
        with Image.open(image_path) as img:
            images.append((luminance, img.copy()))
    images.sort(key=lambda x: x[0])
    return images

def sort_images_by_saturation(image_paths):
    """Trie les images par saturation moyenne."""
    images = []
    for image_path in image_paths:
        avg_color = calculate_average_color(image_path)
        saturation = calculate_saturation(avg_color)
        with Image.open(image_path) as img:
            images.append((saturation, img.copy()))
    images.sort(key=lambda x: x[0])
    return images

def sort_images_by_dominant_color(image_paths):
    """Trie les images par couleur dominante."""
    images = []
    for image_path in image_paths:
        dominant_color = calculate_dominant_color(image_path)
        color_value = sum(dominant_color)  # Utiliser la somme des composantes RGB pour le tri
        with Image.open(image_path) as img:
            images.append((color_value, img.copy()))
    images.sort(key=lambda x: x[0])
    return images

def create_mosaic(image_paths, image_size=(100, 100), output_file='mosaic.png', spacing=5, sort_func=None):
    """Crée une mosaïque d'images triées selon une fonction de tri spécifiée."""
    if sort_func is None:
        raise ValueError("A sorting function must be provided.")

    sorted_images = sort_func(image_paths)

    num_images = len(sorted_images)
    grid_width = int(num_images ** 0.5)
    grid_height = (num_images + grid_width - 1) // grid_width

    mosaic_width = grid_width * (image_size[0] + spacing) - spacing
    mosaic_height = grid_height * (image_size[1] + spacing) - spacing

    mosaic = Image.new('RGB', (mosaic_width, mosaic_height), color='grey')

    x_offset = 0
    y_offset = 0
    for _, img in sorted_images:
        img = img.resize(image_size)
        mosaic.paste(img, (x_offset, y_offset))
        x_offset += image_size[0] + spacing
        if x_offset >= mosaic_width:
            x_offset = 0
            y_offset += image_size[1] + spacing

    mosaic.save(output_file)
    print(f"Mosaic saved as {output_file}")
    return mosaic

def main():
    folder_name = 'covers'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, folder_name)
    image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Créer la mosaïque triée par luminance
    create_mosaic(image_files, image_size=(100, 100), output_file='mosaic_luminance.png', spacing=10, sort_func=sort_images_by_luminance)
    
    # Créer la mosaïque triée par saturation
    create_mosaic(image_files, image_size=(100, 100), output_file='mosaic_saturation.png', spacing=10, sort_func=sort_images_by_saturation)
    
    # Créer la mosaïque triée par couleur dominante
    create_mosaic(image_files, image_size=(100, 100), output_file='mosaic_dominant_color.png', spacing=10, sort_func=sort_images_by_dominant_color)

if __name__ == "__main__":
    main()
