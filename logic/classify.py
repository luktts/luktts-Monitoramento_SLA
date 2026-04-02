from config.grupos import groups

def separar_por_equipe(incidentes):
    resultado = {}

    for inc in incidentes:
        grupo_csv = inc.get("assignment_group", "")

        equipe_final = "Outros"

        for equipe, lista_grupos in groups.items():
            if grupo_csv in lista_grupos:
                equipe_final = equipe
                break

        if equipe_final not in resultado:
            resultado[equipe_final] = []

        resultado[equipe_final].append(inc)

    return resultado
