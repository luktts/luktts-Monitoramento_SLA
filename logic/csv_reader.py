import csv
from tkinter import filedialog


def selecionar_csv():
    caminho = filedialog.askopenfilename(
        title="Selecione um arquivo CSV",
        filetypes=[("CSV Files", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    return caminho


def ler_csv(caminho):
    incidentes = []

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            leitor = csv.DictReader(f)

            for row in leitor:
                incidentes.append({
                    "number": row.get("number", "").strip(),
                    "short_description": row.get("short_description", "").strip(),
                    "assignment_group": row.get("assignment_group", "").strip()
                })

        return incidentes

    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return []