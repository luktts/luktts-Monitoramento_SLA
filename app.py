import tkinter as tk
from tkinter import ttk
import webbrowser

from logic.csv_reader import selecionar_csv, ler_csv
from logic.classify import separar_por_equipe
from logic.email_builder import gerar_email, abrir_email, gerar_mensagem_teams

from config.contact import contact_teams


# ==============================
# NOTIFICAÇÃO DISCRETA (POP-UP)
# ==============================
def notificar(texto):
    note = tk.Toplevel()
    note.overrideredirect(True)
    note.attributes("-topmost", True)

    tk.Label(
        note,
        text=texto,
        bg="#333",
        fg="white",
        font=("Segoe UI", 10),
        padx=12,
        pady=6
    ).pack()

    note.update_idletasks()
    x = root.winfo_x() + root.winfo_width() - note.winfo_width() - 20
    y = root.winfo_y() + 20
    note.geometry(f"+{x}+{y}")

    note.after(1400, note.destroy)


# ==============================
# ABRIR LINK EXTERNO (manager_link)
# ==============================
def abrir_link(equipe):
    link = contact_teams.get(equipe, {}).get("INC_link", "")

    if not link:
        notificar("Nenhum link disponível para esta equipe.")
        return

    webbrowser.open(link)
    notificar("Abrindo link...")


# ==============================
# POP-UP DE MENSAGEM TEAMS
# ==============================
def mostrar_teams(equipe, incidentes):
    texto = gerar_mensagem_teams(equipe, incidentes)

    win = tk.Toplevel()
    win.title(f"Mensagem Teams — {equipe}")
    win.geometry("700x500")

    txt = tk.Text(win, wrap="word")
    txt.pack(fill="both", expand=True, padx=10, pady=10)
    txt.insert("1.0", texto)

    def copiar():
        win.clipboard_clear()
        win.clipboard_append(texto)
        notificar("Mensagem copiada!")

    ttk.Button(win, text="Copiar para área de transferência", command=copiar)\
        .pack(pady=10)


# ==============================
# POP-UP DE PREVIEW DE EMAIL (texto simples)
# ==============================
def mostrar_email(equipe, incidentes):
    texto_email = gerar_email(equipe, incidentes)

    janela = tk.Toplevel()
    janela.title(f"Preview — {equipe}")
    janela.geometry("700x500")

    txt = tk.Text(janela, wrap="word")
    txt.pack(fill="both", expand=True)

    scroll = tk.Scrollbar(txt)
    scroll.pack(side="right", fill="y")
    txt.config(yscrollcommand=scroll.set)
    scroll.config(command=txt.yview)

    txt.insert("1.0", texto_email)


# ==============================
# CARREGAR CSV E MONTAR TABELA
# ==============================
def carregar_arquivo():
    caminho = selecionar_csv()
    if not caminho:
        notificar("Nenhum arquivo selecionado.")
        return

    incidentes = ler_csv(caminho)
    if not incidentes:
        notificar("Erro ao ler CSV ou arquivo vazio.")
        return

    resumo = separar_por_equipe(incidentes)

    # Limpar tabela anterior
    for widget in frame_equipes.winfo_children():
        widget.destroy()

    # Cabeçalhos
    ttk.Label(frame_equipes, text="Equipe", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=10, pady=5)
    ttk.Label(frame_equipes, text="Quantidade", font=("Arial", 11, "bold")).grid(row=0, column=1, padx=10, pady=5)
    ttk.Label(frame_equipes, text="Ações", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=10, pady=5)

    # Preencher linhas
    for linha, (equipe, lista) in enumerate(resumo.items(), start=1):

        ttk.Label(frame_equipes, text=equipe).grid(row=linha, column=0, padx=10, pady=5)
        ttk.Label(frame_equipes, text=str(len(lista))).grid(row=linha, column=1, padx=10, pady=5)

        ttk.Button(frame_equipes, text="Teams",
                   command=lambda eq=equipe, inc=lista: mostrar_teams(eq, inc))\
            .grid(row=linha, column=2, padx=5)

        ttk.Button(frame_equipes, text="Abrir Link",
                   command=lambda eq=equipe: abrir_link(eq))\
            .grid(row=linha, column=3, padx=5)

        ttk.Button(frame_equipes, text="Gerar Email",
                   command=lambda eq=equipe, inc=lista: abrir_email(eq, inc))\
            .grid(row=linha, column=4, padx=5)


# ==============================
# GUI PRINCIPAL
# ==============================
root = tk.Tk()
root.title("Monitoramento SLA — App Genérico")
root.geometry("900x550")

frame_top = ttk.Frame(root)
frame_top.pack(pady=10)

ttk.Button(frame_top, text="Selecionar arquivo CSV", command=carregar_arquivo)\
    .grid(row=0, column=0, padx=10)

ttk.Label(root, text="Selecione um arquivo CSV para começar.", font=("Arial", 10))\
    .pack(pady=5)

frame_equipes = ttk.Frame(root)
frame_equipes.pack(fill="both", expand=True, padx=20, pady=10)

root.mainloop()