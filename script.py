
import requests
import json
from github import Github

# Cargar configuraciones desde config.json
with open("config.json", "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

GITHUB_TOKEN = config["github_token"]
GITHUB_REPO = config["github_repo"]
ARCHIVO = config["output_file"]
CATEGORIAS = config["categories"]

WIKIPEDIA_API_URL = "https://es.wikipedia.org/w/api.php"

def obtener_paginas_categoria(categoria, paginas=None):
    """
    Obtiene una lista de páginas de una categoría y sus subcategorías de Wikipedia.
    """
    if paginas is None:
        paginas = {}

    # Obtener páginas en la categoría
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": categoria,
        "cmlimit": "max",
        "format": "json"
    }
    response = requests.get(WIKIPEDIA_API_URL, params=params).json()
    miembros = response.get("query", {}).get("categorymembers", [])

    for miembro in miembros:
        titulo = miembro["title"]
        if titulo.startswith("Categoría:"):
            # Es una subcategoría; explorar recursivamente
            obtener_paginas_categoria(titulo, paginas)
        else:
            # Es una página normal; agregarla al diccionario
            paginas[miembro["pageid"]] = {
                "title": titulo,
                "url": f"https://es.wikipedia.org/wiki/{titulo.replace(' ', '_')}"
            }

    return paginas

def actualizar_archivo_github(token, repo, archivo, contenido):
    """
    Sube o actualiza un archivo en un repositorio de GitHub.
    """
    g = Github(token)
    repository = g.get_repo(repo)
    try:
        # Verifica si el archivo ya existe
        archivo_existente = repository.get_contents(archivo)
        # Actualiza el archivo existente
        repository.update_file(archivo_existente.path, f"Actualizar {archivo}", contenido, archivo_existente.sha)
    except Exception:
        # Si no existe, lo crea
        repository.create_file(archivo, f"Crear {archivo}", contenido)

# Script principal
resultado = {}
for categoria in CATEGORIAS:
    # Obtener páginas para cada categoría
    paginas = obtener_paginas_categoria(categoria)
    # Agregar al resultado bajo el nombre de la categoría
    resultado[categoria] = paginas

# Convertir el diccionario a formato JSON
contenido_json = json.dumps(resultado, indent=4, ensure_ascii=False)

# Actualizar el archivo en GitHub
actualizar_archivo_github(GITHUB_TOKEN, GITHUB_REPO, ARCHIVO, contenido_json)
print("Archivo actualizado en GitHub.")
