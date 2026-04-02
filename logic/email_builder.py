import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
from config.contact import contact_teams


def saudacao():
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    return "Boa noite"


def gerar_email(equipe, incidentes):
    info = contact_teams.get(equipe, {})

    leader = info.get("tech_leader_name", "Líder").strip()

    linhas = [
        f"Olá {leader},\n",
        f"Incidentes do grupo {equipe}:\n"
    ]

    if not incidentes:
        linhas.append("\nNenhum incidente encontrado.\n")
    else:
        for inc in incidentes:
            linhas.append(f"- {inc['number']} — {inc['short_description']}")

    linhas.append("\n\nAtenciosamente,\nEquipe de Monitoramento SLA")
    return "\n".join(linhas)


def gerar_mensagem_teams(equipe, incidentes):
    info = contact_teams.get(equipe, {})

    leader = info.get("tech_leader_name", "")
    link = info.get("INC_link", "")

    primeiro_nome = leader.split()[0] if leader else "Olá"

    lista = "\n".join(
        f"- {inc['number']} — {inc['short_description']}"
        for inc in incidentes
    )

    return (
        f"{saudacao()}, {primeiro_nome}!\n\n"
        f"Esta é uma mensagem automática.\n\n"
        f"Segue atualização dos incidentes do grupo *{equipe}*:\n\n"
        f"{lista}\n\n"
        f"Consulta completa:\n{link}"
    )


def abrir_email(equipe, incidentes):
    # === Caminhos ===
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(current_dir, "..", "emails")

    template_path = os.path.join(base_dir, "template", "template.txt")
    output_dir = os.path.join(base_dir, "emails_sends")
    assinatura_path = os.path.join(base_dir, "template", "assinatura.png")

    os.makedirs(output_dir, exist_ok=True)

    # === Carregar template ===
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    info = contact_teams.get(equipe, {})

    leader = info.get("tech_leader_name", "")
    leader_email = info.get("tech_leader_email", "")
    manager_email = info.get("manager_email", "")
    link = info.get("INC_link", "")

    primeiro = leader.split()[0] if leader else ""

    # === Lista de incidentes ===
    lista_txt = "\n".join(
        f"- {inc['number']} — {inc['short_description']}"
        for inc in incidentes
    )

    # === Preencher template ===
    corpo_texto = template.format(
        saudacao=saudacao(),
        primeiro_nome_lider=primeiro,
        equipe=equipe,
        lista_incidentes=lista_txt,
        inc_link=link
    )

    # Converter para HTML
    corpo_html = corpo_texto.replace("\n", "<br>")

    # === HTML Final com assinatura INLINE ===
    html_final = f"""
    <html>
    <body style="font-family:Segoe UI, Arial; font-size:11pt; color:#333;">
        {corpo_html}
        <br><br>
        <img src="cid:assinatura.png">
    </body>
    </html>
    """

    # === Construção do e-mail ===
    msg = MIMEMultipart("related")
    msg["To"] = leader_email
    msg["CC"] = manager_email
    msg["Subject"] = f"Atualização de Incidentes — {equipe}"
    msg["X-Unsent"] = "1"

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(corpo_texto, "plain"))
    alt.attach(MIMEText(html_final, "html"))
    msg.attach(alt)

    # === Assinatura embutida (inline), NÃO como anexo ===
    if os.path.exists(assinatura_path):
        with open(assinatura_path, "rb") as img:
            assinatura = MIMEImage(img.read())
            assinatura.add_header("Content-ID", "<assinatura.png>")
            assinatura.add_header("Content-Disposition", "inline")
            msg.attach(assinatura)

    # === Salvar arquivo EML ===
    eml_path = os.path.join(output_dir, f"email_{equipe}.eml")

    with open(eml_path, "wb") as f:
        f.write(msg.as_string().encode())

    os.startfile(eml_path)