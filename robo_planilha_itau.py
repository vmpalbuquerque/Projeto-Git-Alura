import tkinter as tk
from tkinter import messagebox
import re
from openpyxl import Workbook
from datetime import datetime


def limpar_valor(valor_str):
    valor_str = valor_str.replace(" ", "")
    return float(valor_str.replace(".", "").replace(",", "."))


def processar_lancamentos(texto):

    linhas = texto.strip().split("\n")

    parcelados = []
    normais = []

    total = 0

    for linha in linhas:

        linha = linha.strip()

        # captura valores
        valor_match = re.search(r"(\d+,\s?\d{2})$", linha)
        if not valor_match:
            continue

        valor_str = valor_match.group(1)
        valor = limpar_valor(valor_str)
        total += valor

        # captura todas datas/parcela
        datas = re.findall(r"\d{2}/\d{2}", linha)

        data_compra = datas[0] if datas else ""
        parcela = datas[1] if len(datas) > 1 else "-"

        # remove data, parcela e valor para pegar nome
        nome = linha
        nome = nome.replace(data_compra, "", 1)
        nome = nome.replace(valor_str, "")
        if parcela != "-":
            nome = nome.replace(parcela, "", 1)

        nome = nome.strip()

        registro = [data_compra, nome, parcela, valor]

        if parcela != "-":
            parcelados.append(registro)
        else:
            normais.append(registro)

    return parcelados, normais, total


def gerar_planilha(parcelados, normais, total):

    wb = Workbook()
    ws = wb.active
    ws.title = "Fatura"

    ws.append(["Data", "Estabelecimento", "Parcela", "Valor"])

    # 🔹 Primeiro parcelados
    for linha in parcelados:
        ws.append(linha)

    # 🔹 Depois normais
    for linha in normais:
        ws.append(linha)

    ws.append([])
    ws.append(["", "", "TOTAL GERAL", total])

    nome_arquivo = f"planilha_fatura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(nome_arquivo)

    return nome_arquivo


def executar():

    texto = caixa_texto.get("1.0", tk.END)

    if not texto.strip():
        messagebox.showwarning("Aviso", "Cole os lançamentos primeiro.")
        return

    parcelados, normais, total = processar_lancamentos(texto)

    if not parcelados and not normais:
        messagebox.showerror("Erro", "Nenhum lançamento identificado.")
        return

    arquivo = gerar_planilha(parcelados, normais, total)

    resultado_label.config(
        text=f"Parcelados: {len(parcelados)}  |  Normais: {len(normais)}  |  Total: R$ {total:.2f}"
    )

    messagebox.showinfo("Sucesso", f"Planilha gerada:\n{arquivo}")


# ==========================
# INTERFACE
# ==========================

janela = tk.Tk()
janela.title("Robô Fatura Inteligente")
janela.geometry("750x520")

titulo = tk.Label(
    janela,
    text="Cole os lançamentos da fatura abaixo:",
    font=("Arial", 12)
)
titulo.pack(pady=10)

caixa_texto = tk.Text(janela, height=22)
caixa_texto.pack(fill="both", expand=True, padx=10)

botao = tk.Button(
    janela,
    text="Gerar Planilha",
    command=executar,
    bg="#1f7a1f",
    fg="white",
    font=("Arial", 11, "bold")
)
botao.pack(pady=10)

resultado_label = tk.Label(janela, text="", font=("Arial", 11))
resultado_label.pack()

janela.mainloop()
