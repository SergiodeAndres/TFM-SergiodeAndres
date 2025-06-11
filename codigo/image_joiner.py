from PIL import Image
from tkinter import filedialog, Tk
import os
import re

def seleccionar_imagenes():
    root = Tk()
    root.withdraw()  # Ocultar ventana principal
    rutas = filedialog.askopenfilenames(
        title="Selecciona 2 o 3 imágenes", 
        filetypes=[("Imagenes", "*.png *.jpg *.jpeg *.bmp")]
    )
    return list(rutas)

def combinar_dos_vertical(im1, im2):
    # Ajustar anchos al mismo valor si son distintos
    ancho = max(im1.width, im2.width)
    im1 = im1.resize((ancho, int(im1.height * ancho / im1.width)))
    im2 = im2.resize((ancho, int(im2.height * ancho / im2.width)))

    altura_total = im1.height + im2.height
    combinada = Image.new('RGB', (ancho, altura_total), (255, 255, 255))

    combinada.paste(im1, (0, 0))
    combinada.paste(im2, (0, im1.height))

    return combinada

def unir_horizontal(imagenes):
    imgs = [Image.open(img).convert("RGBA") for img in imagenes]
    anchos = [img.width for img in imgs]
    max_ancho = max(anchos)
    total_alto = sum(img.height for img in imgs)

    nueva = Image.new("RGBA", (max_ancho, total_alto), (255, 255, 255, 0))

    y = 0
    for img in imgs:
        x = (max_ancho - img.width) // 2
        nueva.paste(img, (x, y), mask=img if img.mode == 'RGBA' else None)
        y += img.height

    return nueva

def unir_horizontal(imagenes):
    imgs = [Image.open(img).convert("RGBA") for img in imagenes]
    alturas = [img.height for img in imgs]
    max_alto = max(alturas)
    total_ancho = sum(img.width for img in imgs)

    nueva = Image.new("RGBA", (total_ancho, max_alto), (255, 255, 255, 0))

    x = 0
    for img in imgs:
        y = (max_alto - img.height) // 2
        nueva.paste(img, (x, y))
        x += img.width

    return nueva

def unir_piramide(imagenes):
    img1, img2, img3 = [Image.open(img).convert("RGBA") for img in imagenes]

    ancho_superior = img1.width + img2.width
    ancho_total = max(ancho_superior, img3.width)
    alto_total = img1.height + img3.height + 10  # 10px de margen

    nueva = Image.new("RGBA", (ancho_total, alto_total), (255, 255, 255, 0))

    nueva.paste(img1, (0, 0))
    nueva.paste(img2, (img1.width, 0))

    x3 = (ancho_total - img3.width) // 2
    nueva.paste(img3, (x3, img1.height + 10))

    return nueva

def unir_cuadrado(imagenes):
    imgs = [Image.open(img).convert("RGBA") for img in imagenes]

    # Suponemos tamaños similares (podrías redimensionar si quieres)
    ancho = max(img.width for img in imgs)
    alto = max(img.height for img in imgs)

    total_ancho = 2 * ancho
    total_alto = 2 * alto + 10  # 10 px de margen entre filas

    nueva = Image.new("RGBA", (total_ancho, total_alto), (255, 255, 255, 0))

    # Coordenadas manuales
    coords = [
        (0, 0),               # img1
        (ancho, 0),           # img2
        (0, alto + 10),       # img3
        (ancho, alto + 10)    # img4
    ]

    for img, (x, y) in zip(imgs, coords):
        nueva.paste(img, (x, y))

    return nueva

def extraer_nombre(imagenes):
    if len(imagenes) == 2:
        temas = []
        semestres = []

        for path in imagenes:
            basename = os.path.basename(path)

            # Extraer tema: palabra justo antes de "_semestre"
            tema_match = re.search(r"_([^_]+)_semestre", basename)
            if tema_match:
                temas.append(tema_match.group(1))

            # Extraer semestre: después de semestre_
            semestre_match = re.search(r"semestre_(20\d{2}-S[12])", basename)
            if semestre_match:
                semestres.append(semestre_match.group(1))

        tema_final = temas[0] if len(set(temas)) == 1 else "VARIOS"
        return f"{tema_final}_" + "_".join(semestres) + "_NUEVO" if semestres else "salida_horizontal"

    elif len(imagenes) in [3, 4]:
        partes = []
        for path in imagenes:
            match = re.search(r"posts_([^_]+)", os.path.basename(path))
            if match:
                partes.append(match.group(1))
        return "_".join(partes) if partes else f"salida_{len(imagenes)}imgs"
    else:
        return "combinacion"

def combinar_y_guardar(imagenes):
    if len(imagenes) == 2:
        resultado = unir_horizontal(imagenes)
        nombre = extraer_nombre(imagenes)
        guardar_imagen(resultado, nombre, imagenes[0])

    elif len(imagenes) == 3:
        resultado = unir_piramide(imagenes)
        nombre = extraer_nombre(imagenes)
        guardar_imagen(resultado, nombre, imagenes[0])

    elif len(imagenes) == 4:
        resultado = unir_cuadrado(imagenes)
        nombre = extraer_nombre(imagenes)
        guardar_imagen(resultado, nombre, imagenes[0])

    elif len(imagenes) > 4:
        print(f"\n🔁 Procesando {len(imagenes)} imágenes de dos en dos...")
        for i in range(0, len(imagenes) - 1, 2):
            pareja = imagenes[i:i+2]
            if len(pareja) == 2:
                resultado = unir_horizontal(pareja)
                nombre = extraer_nombre(pareja)
                guardar_imagen(resultado, nombre, pareja[0])
            else:
                print(f"⚠️ Imagen sin pareja: {os.path.basename(pareja[0])}")
    else:
        print("❌ Debes seleccionar entre 2 y 4 imágenes, o más para agrupar por pares.")

def guardar_imagen(imagen, nombre, base_path):
    output_path = os.path.join(os.path.dirname(base_path), f"combinada_{nombre}.png")
    imagen.save(output_path)
    print(f"✅ Imagen guardada como: {output_path}")
    #imagen.show()

def main():
    while True:
        print("Selecciona 2 o 3 imágenes (o pulsa Cancelar para salir).")
        rutas = seleccionar_imagenes()
        if not rutas:
            print("Salida del programa.")
            break
        try:
            combinar_y_guardar(rutas)
        except Exception as e:
            print("❌ Error al procesar las imágenes:", e)

if __name__ == "__main__":
    main()