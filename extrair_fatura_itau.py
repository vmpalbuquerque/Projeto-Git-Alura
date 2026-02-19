import re
import os
import unicodedata
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import xlsxwriter

# ---------------- CONFIGURAÇÃO E REGEX ----------------

<<<<<<< HEAD
RE_VALOR = re.compile(r'(-?\s*\d{1,3}(?:\.\d{3})*,\d{2})')
RE_DATE = re.compile(r'(\d{2}/\d{2})')
RE_PARCELA = re.compile(r'(\d{1,2}\s*/\s*\d{1,2})')

RE_FULL_TRANSACTION = re.compile(
    r'(\d{2}/\d{2})'
    r'(.*?)'
    r'(-?\s*\d{1,3}(?:\.\d{3})*,\d{2})',
=======
RE_VALOR = re.compile(r'(-?\s*\d{1,3}(?:\.\d{3})*,\d{2})')  # agora captura sinal opcional antes do número
RE_DATE = re.compile(r'(\d{2}/\d{2})')

# Regex que detecta parcela mesmo colada ao nome (ex: MERCADOLIVRE*MERCA01/03 ou PESCOMERC02/02)
RE_PARCELA = re.compile(r'(\d{1,2}\s*/\s*\d{1,2})')

# Detecta Data + Nome + Valor (mantendo comportamento do seu robô original)
# Valor agora aceita um hífen opcional e espaços entre hífen e número: "- 0,01", "-0,01", etc.
RE_FULL_TRANSACTION = re.compile(
    r'(\d{2}/\d{2})'                  # data
    r'(.*?)'                          # nome (qualquer coisa, não guloso)
    r'(-?\s*\d{1,3}(?:\.\d{3})*,\d{2})',   # valor (com possibilidade de '-' separado por espaços)
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
    re.DOTALL
)

# ---------------- FUNÇÕES AUXILIARES ----------------

def normalizar(texto):
    if texto is None:
        return ""
    t = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8").lower()
    return re.sub(r'\s+', ' ', t).strip()

def limpar_estabelecimento(estab_raw):
<<<<<<< HEAD
    if pd.isna(estab_raw):
        return ""
    limpo = str(estab_raw).replace("\n", " ").strip()
    limpo = re.sub(r'\s+', ' ', limpo).strip()
    limpo = RE_PARCELA.sub("", limpo).strip()
    limpo = re.sub(r'\s*\d{2}/\d{2}$', '', limpo).strip()
    limpo = limpo.strip("-").strip()
    return limpo

def calcular_parcelas_restantes(parcela_raw):
=======
    """Mantém o nome completo do estabelecimento; remove possíveis parcelas residuais e ruídos simples."""
    if pd.isna(estab_raw):
        return ""

    limpo = str(estab_raw).replace("\n", " ").strip()
    limpo = re.sub(r'\s+', ' ', limpo).strip()

    # Remove parcela caso ainda exista (por segurança)
    limpo = RE_PARCELA.sub("", limpo).strip()

    # Remove datas finais grudentas (por segurança)
    limpo = re.sub(r'\s*\d{2}/\d{2}$', '', limpo).strip()
    limpo = limpo.strip("-").strip()

    return limpo

def calcular_parcelas_restantes(parcela_raw):
    """Retorna número de parcelas restantes como int ou string vazia se não houver."""
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
    if not parcela_raw:
        return ""
    m = re.search(r'(\d{1,2})\s*/\s*(\d{1,2})', parcela_raw)
    if not m:
        return ""
    atual = int(m.group(1))
    total = int(m.group(2))
    restantes = total - atual
    if restantes < 0:
        restantes = 0
    return str(restantes)

<<<<<<< HEAD
# ---------------- EXTRATOR ----------------
=======
# ---------------- EXTRATOR PRINCIPAL (v13.23) ----------------
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81

def extrair_lancamentos_fatura(raw_text):
    matches = RE_FULL_TRANSACTION.findall(raw_text)
    final_regs = []

    for data_raw, estab_temp, valor_text in matches:

<<<<<<< HEAD
        if re.search(r'-\s*\d', valor_text):
            continue

        try:
            valor_clean = valor_text.replace(" ", "").replace(".", "").replace(",", ".")
            valor_float = float(valor_clean)
        except:
            continue

        if valor_float < 0:
            continue

=======
        # valor_text pode trazer o hífen e espaços, normalizamos para checar sinal
        valor_text_raw = str(valor_text)

        # --- DETECÇÃO DE NEGATIVOS ---
        # Se houver um '-' imediatamente antes do número (mesmo com espaços) o lançamento é negativo -> ignorar
        if re.search(r'-\s*\d', valor_text_raw):
            # descartamos totalmente, não inclui no resultado
            continue

        # conversão segura do valor (remover possíveis espaços no valor)
        try:
            # retirar espaços e possíveis sinais residuais
            valor_clean = valor_text_raw.replace(" ", "").replace(".", "").replace(",", ".")
            valor_float = float(valor_clean)
        except Exception:
            # se não conseguir converter, pular
            continue

        # ignorar valores negativos (caso venha com sinal consolidado)
        if valor_float < 0:
            continue

        # detectar parcela mesmo colada ao nome
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
        parcela = ""
        m_parc = RE_PARCELA.search(estab_temp)
        if m_parc:
            parcela_raw = m_parc.group(1)
            parcela = parcela_raw.replace(" ", "")
<<<<<<< HEAD
            estab_temp = estab_temp.replace(parcela_raw, "", 1).strip()

        estabelecimento = limpar_estabelecimento(estab_temp)

=======
            # remover apenas a primeira ocorrência da parcela no texto do estabelecimento
            estab_temp = estab_temp.replace(parcela_raw, "", 1).strip()

        # limpar estabelecimento (mantendo o nome o máximo possível)
        estabelecimento = limpar_estabelecimento(estab_temp)

        # filtros originais
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
        if len(estabelecimento) < 2:
            continue
        if any(key in normalizar(estabelecimento) for key in [
            'lancamentos', 'total', 'pagamento', 'vencimento', 'saque', 'compra', 'parcial'
        ]):
            continue

        final_regs.append({
            "Data": data_raw,
            "Estabelecimento": estabelecimento,
<<<<<<< HEAD
            "Valor_texto": valor_text.strip(),
=======
            "Valor_texto": valor_text_raw.strip(),
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
            "Valor": valor_float,
            "Parcela": parcela
        })

    df = pd.DataFrame(final_regs)
    if df.empty:
        return []

<<<<<<< HEAD
=======
    # ordenação: parcelado primeiro (como você já fazia)
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
    df["is_parc"] = df["Parcela"].apply(lambda x: 1 if x else 0)
    df = df.sort_values(by=["is_parc", "Data"], ascending=[False, True])
    df = df.drop(columns=["is_parc"]).reset_index(drop=True)

<<<<<<< HEAD
    df["Parcelas Restantes"] = df["Parcela"].apply(calcular_parcelas_restantes)
    return df.to_dict("records")

# ---------------- SALVAR EXCEL ----------------

def save_records_to_excel(records, path_out):
    df = pd.DataFrame(records)
    df = df.rename(columns={"Valor": "Valor (R$)"})
=======
    # nova coluna: Parcelas Restantes
    df["Parcelas Restantes"] = df["Parcela"].apply(calcular_parcelas_restantes)
    df["_origem"] = "texto_colado"

    return df.to_dict("records")

# ---------------- SALVAR EM EXCEL (com alinhamentos solicitados) ----------------

def save_records_to_excel(records, path_out):
    df = pd.DataFrame(records)
    # renomear conforme sua expectativa
    df = df.rename(columns={"Valor": "Valor (R$)"})

    # garantir colunas na ordem solicitada
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
    cols = ["Data", "Estabelecimento", "Valor (R$)", "Parcela", "Parcelas Restantes"]
    df = df[cols]

    total_sum = df["Valor (R$)"].sum() if not df.empty else 0.0

    workbook = xlsxwriter.Workbook(path_out)
    ws = workbook.add_worksheet("Lançamentos")

<<<<<<< HEAD
    header_fmt = workbook.add_format({
        "bold": True, "bg_color": "#1c1c1c", "font_color": "white",
        "border": 1, "align": "center"
    })

    center_fmt = workbook.add_format({"align": "center"})
    left_fmt = workbook.add_format({"align": "left"})
    currency_fmt = workbook.add_format({
        "num_format": "R$ #,##0.00", "align": "right"
    })

    for col, name in enumerate(cols):
        ws.write(0, col, name, header_fmt)

    row = 1
    for _, r in df.iterrows():
        ws.write_string(row, 0, str(r["Data"]), center_fmt)
        ws.write_string(row, 1, str(r["Estabelecimento"]), left_fmt)
        ws.write_number(row, 2, float(r["Valor (R$)"]), currency_fmt)
        ws.write_string(row, 3, str(r["Parcela"]), center_fmt)
        ws.write_string(row, 4, str(r["Parcelas Restantes"]), center_fmt)
        row += 1

    total_row = row + 1
    ws.write_string(total_row, 1, "VALOR TOTAL DOS LANÇAMENTOS", header_fmt)
    ws.write_number(total_row, 2, total_sum, currency_fmt)

    ws.set_column("A:A", 10)
    ws.set_column("B:B", 60)
    ws.set_column("C:C", 14)
    ws.set_column("D:D", 12)
    ws.set_column("E:E", 20)

    workbook.close()

# ---------------- GUI DARK FUTURISTA ----------------
=======
    # ---------- formatos ----------
    # Cabeçalho: centralizado
    header_fmt = workbook.add_format({
        "bold": True, "font_name": "Calibri", "font_color": "black",
        "bg_color": "#FFF2CC", "border": 1, "align": "center", "valign": "vcenter"
    })

    # Texto centralizado (para tudo que NÃO for lançamento específico)
    center_fmt = workbook.add_format({
        "font_name": "Calibri", "align": "center", "valign": "vcenter"
    })

    # Estabelecimento: alinhado à esquerda (lançamentos)
    left_fmt = workbook.add_format({
        "font_name": "Calibri", "align": "left", "valign": "vcenter"
    })

    # Valores: alinhado à direita em formato moeda
    currency_fmt = workbook.add_format({
        "num_format": "R$ #,##0.00", "font_name": "Calibri", "align": "right", "valign": "vcenter"
    })

    # Parcela: centralizado
    parc_fmt = workbook.add_format({
        "font_name": "Calibri", "align": "center", "valign": "vcenter"
    })

    # Parcelas Restantes: centralizado (número ou vazio)
    rest_fmt = workbook.add_format({
        "font_name": "Calibri", "align": "center", "valign": "vcenter"
    })

    # Total final: centralizado e destacado
    total_label_fmt = workbook.add_format({
        "bold": True, "bg_color": "#FFF2CC", "font_name": "Calibri", "border": 1, "align": "center", "valign": "vcenter"
    })
    total_value_fmt = workbook.add_format({
        "num_format": "R$ #,##0.00", "bold": True, "font_name": "Calibri", "align": "right", "valign": "vcenter"
    })

    # ---------- escrever cabeçalho ----------
    for col, name in enumerate(cols):
        ws.write(0, col, name, header_fmt)

    # ---------- escrever linhas de lançamentos ----------
    row = 1
    for _, r in df.iterrows():
        # Data -> centralizado
        ws.write_string(row, 0, str(r.get("Data", "")), center_fmt)

        # Estabelecimento -> alinhado à esquerda (lançamento)
        ws.write_string(row, 1, str(r.get("Estabelecimento", "")), left_fmt)

        # Valor -> alinhado à direita (moeda)
        try:
            ws.write_number(row, 2, float(r.get("Valor (R$)", 0.0)), currency_fmt)
        except:
            ws.write_string(row, 2, str(r.get("Valor (R$)", "")), center_fmt)

        # Parcela -> centralizado
        ws.write_string(row, 3, str(r.get("Parcela", "") or ""), parc_fmt)

        # Parcelas Restantes -> centralizado (se número, escrever como número para facilitar filtros)
        pr = r.get("Parcelas Restantes", "")
        if pr is None or pr == "":
            ws.write_string(row, 4, "", rest_fmt)
        else:
            # tentar converter para int
            try:
                ws.write_number(row, 4, int(pr), rest_fmt)
            except:
                ws.write_string(row, 4, str(pr), rest_fmt)

        row += 1

    # ---------- total final (linha abaixo) ----------
    total_row = row + 1
    ws.write_string(total_row, 1, "VALOR TOTAL DOS LANÇAMENTOS", total_label_fmt)
    ws.write_number(total_row, 2, total_sum, total_value_fmt)

    # ---------- ajustar colunas ----------
    ws.set_column("A:A", 10)   # Data
    ws.set_column("B:B", 60)   # Estabelecimento
    ws.set_column("C:C", 14)   # Valor
    ws.set_column("D:D", 12)   # Parcela
    ws.set_column("E:E", 20)   # Parcelas Restantes

    workbook.close()

# ---------------- GUI (mantendo fluxo do seu robô) ----------------
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81

class App:
    def __init__(self, root):
        self.root = root
<<<<<<< HEAD
        root.title("Robô Extrator de Fatura Itaú")

        root.geometry("1100x720")
        root.configure(bg="#0f0f0f")
        root.resizable(False, False)

        self.green = "#00a651"
        self.yellow = "#ffc107"
        self.red = "#c1121f"
        self.white = "#f1f1f1"
        self.frame_bg = "#1c1c1c"

        tk.Label(root, text="🔥 ROBÔ EXTRATOR DE FATURA 🔥",
                 font=("Segoe UI", 16, "bold"),
                 fg=self.green, bg="#0f0f0f").pack(pady=10)

        input_frame = tk.Frame(root, bg=self.frame_bg)
        input_frame.pack(padx=15, pady=5, fill="both")

        tk.Label(input_frame, text="Cole o conteúdo da fatura:",
                 fg=self.white, bg=self.frame_bg,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=5)

        self.text_input = tk.Text(input_frame, height=10, width=110,
                                  bg="#121212", fg=self.white,
                                  insertbackground="white",
                                  font=("Consolas", 10), relief="flat")
        self.text_input.pack(padx=10, pady=5)

        btn_frame = tk.Frame(root, bg="#0f0f0f")
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="Extrair Lançamentos",
                  bg=self.green, fg="black",
                  font=("Segoe UI", 11, "bold"),
                  width=20, relief="flat",
                  command=self.extract_and_preview).grid(row=0, column=0, padx=6)

        tk.Button(btn_frame, text="Copiar Texto",
                  bg=self.yellow, fg="black",
                  font=("Segoe UI", 11, "bold"),
                  width=15, relief="flat",
                  command=self.copy_text).grid(row=0, column=1, padx=6)

        tk.Button(btn_frame, text="Fechar",
                  bg=self.red, fg="white",
                  font=("Segoe UI", 11, "bold"),
                  width=12, relief="flat",
                  command=root.destroy).grid(row=0, column=2, padx=6)

        preview_frame = tk.Frame(root, bg=self.frame_bg)
        preview_frame.pack(padx=15, pady=5, fill="both")

        tk.Label(preview_frame, text="Preview:",
                 fg=self.white, bg=self.frame_bg,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=5)

        self.text_preview = tk.Text(preview_frame, height=10, width=110,
                                    bg="#121212", fg=self.white,
                                    insertbackground="white",
                                    font=("Consolas", 10), relief="flat")
        self.text_preview.pack(padx=10, pady=5)

        save_frame = tk.Frame(root, bg="#0f0f0f")
        save_frame.pack(pady=10)

        tk.Label(save_frame, text="Nome do arquivo:",
                 fg=self.white, bg="#0f0f0f").grid(row=0, column=0, padx=6)

        self.out_entry = tk.Entry(save_frame, width=45,
                                  bg="#1c1c1c", fg=self.white,
                                  insertbackground="white",
                                  relief="flat")
        self.out_entry.grid(row=0, column=1, padx=6)
        self.out_entry.insert(0, f"Compras_Fatura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

        tk.Button(save_frame, text="Salvar Excel",
                  bg=self.green, fg="black",
                  font=("Segoe UI", 11, "bold"),
                  width=15, relief="flat",
                  command=self.save_excel).grid(row=0, column=2, padx=6)
=======
        root.title("Robô Extrator de Fatura Itaú — v13.23")

        # Texto para colagem da fatura
        tk.Label(root, text="Cole o conteúdo da fatura (copie do PDF e cole aqui):", font=("Calibri", 11, "bold")).pack(anchor="w", padx=10, pady=(6,0))
        self.text_input = tk.Text(root, height=16, width=120, wrap=tk.WORD, font=("Consolas", 10))
        self.text_input.pack(padx=10, pady=6)

        # Botões
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=4)
        tk.Button(btn_frame, text="Extrair Lançamentos", bg="blue", fg="white", font=("Calibri", 11, "bold"), command=self.extract_and_preview).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Copiar Texto", bg="orange", fg="white", font=("Calibri", 11, "bold"), command=self.copy_text).grid(row=0, column=1, padx=6)

        # Preview
        tk.Label(root, text="Preview - registros extraídos:", font=("Calibri", 11, "bold")).pack(anchor="w", padx=10, pady=(6,0))
        self.text_preview = tk.Text(root, height=16, width=120)
        self.text_preview.pack(padx=10, pady=6)

        # Salvar Excel
        frame = tk.Frame(root)
        frame.pack(pady=6, fill="x")
        tk.Label(frame, text="Nome do arquivo (.xlsx):", font=("Calibri", 10)).grid(row=0, column=0, padx=6, sticky="w")
        self.out_entry = tk.Entry(frame, width=60)
        self.out_entry.grid(row=0, column=1, padx=6)
        self.out_entry.insert(0, f"Compras_Fatura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        tk.Button(frame, text="Salvar Excel", bg="green", fg="white", font=("Calibri", 11, "bold"), command=self.save_excel).grid(row=0, column=2, padx=6)
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81

        self.records = []

    def extract_and_preview(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text:
<<<<<<< HEAD
            messagebox.showerror("Erro", "Nenhum texto colado.")
            return

        self.records = extrair_lancamentos_fatura(raw_text)
        self.text_preview.delete("1.0", tk.END)

        if not self.records:
            self.text_preview.insert(tk.END, "Nenhum lançamento encontrado.")
            return

        df = pd.DataFrame(self.records)
        total = df["Valor"].sum()

        for r in self.records:
            self.text_preview.insert(
                tk.END,
                f"{r['Data']} | {r['Estabelecimento']} | R$ {r['Valor_texto']} | {r['Parcela']} | {r['Parcelas Restantes']}\n"
            )

        self.text_preview.insert(tk.END, "\n")
        self.text_preview.insert(
            tk.END,
            f"TOTAL: R$ {total:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        )

    def save_excel(self):
        if not self.records:
            messagebox.showerror("Erro", "Nenhum registro para salvar.")
=======
            messagebox.showerror("Erro", "Nenhum texto colado. Cole o conteúdo da fatura para extrair.")
            return

        try:
            self.records = extrair_lancamentos_fatura(raw_text)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao extrair: {e}")
            return

        self.text_preview.delete("1.0", tk.END)
        if not self.records:
            self.text_preview.insert(tk.END, "Nenhum lançamento encontrado.\n")
            return

        # mostrar preview
        df = pd.DataFrame(self.records)
        total = df["Valor"].sum() if not df.empty else 0.0

        header = f"{'DATA':8} | {'ESTABELECIMENTO':60} | {'VALOR':12} | {'PARCELA':8} | {'RESTANTES':10}\n"
        self.text_preview.insert(tk.END, header)
        self.text_preview.insert(tk.END, "-" * 115 + "\n")
        for r in self.records:
            dt = r.get("Data", "")
            est = r.get("Estabelecimento", "")[:60]
            val = r.get("Valor_texto", "")
            parc = r.get("Parcela", "")
            rest = r.get("Parcelas Restantes", "")
            self.text_preview.insert(tk.END, f"{dt:8} | {est:60} | R$ {val:10} | {parc:8} | {rest:10}\n")
        self.text_preview.insert(tk.END, "\n")
        self.text_preview.insert(tk.END, f"TOTAL: R$ {total:,.2f}".replace(",", "_TEMP_").replace(".", ",").replace("_TEMP_", "."))

    def save_excel(self):
        if not self.records:
            messagebox.showerror("Erro", "Nenhum registro para salvar. Faça a extração antes.")
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
            return

        name = self.out_entry.get().strip()
        if not name.endswith(".xlsx"):
            name += ".xlsx"

        path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=name)
        if not path:
            return

<<<<<<< HEAD
        save_records_to_excel(self.records, path)
        messagebox.showinfo("Sucesso", f"Planilha salva em:\n{path}")
=======
        try:
            save_records_to_excel(self.records, path)
            messagebox.showinfo("Sucesso", f"Planilha salva em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro ao salvar", f"Falha ao salvar o arquivo: {e}")
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81

    def copy_text(self):
        txt = self.text_input.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
<<<<<<< HEAD
        messagebox.showinfo("Copiado", "Texto copiado.")

# ---------------- INICIAR ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
=======
        messagebox.showinfo("Copiado", "Texto copiado para a área de transferência.")

# Inicia a GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
>>>>>>> b0bc81a7a348b9e03ad71ad1f6fab33548cc4d81
