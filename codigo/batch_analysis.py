import subprocess

# Definir los scripts y los inputs que esperan
programas = [
    {
        "script": "Top2Vec_2.py",
        "inputs": ["1", "1"]
    },
    {
        "script": "Top2Vec_2.py",
        "inputs": ["1", "2"]
    },
    {
        "script": "Top2Vec_2.py",
        "inputs": ["1", "3"]
    },
    {
        "script": "Top2Vec_2.py",
        "inputs": ["2", "1"]
    },
    {
        "script": "Top2Vec_2.py",
        "inputs": ["2", "2"]
    },
    {
        "script": "Top2Vec_2.py",
        "inputs": ["2", "3"]
    }
]
python_path = r"D:\TFM_proyecto_codigo\.venv\Scripts\python.exe"
for prog in programas:
    # Combinar inputs como una sola cadena separada por saltos de línea
    input_str = "\n".join(prog["inputs"]) + "\n"

    print(f"Ejecutando {prog['script']} con inputs: {prog['inputs']}")

    result = subprocess.run(
        [python_path, prog["script"]],
        input=input_str,
        capture_output=True,
        text=True
    )

    print("Salida del programa:")
    print(result.stdout)
    if result.stderr:
        print("Errores:")
        print(result.stderr)