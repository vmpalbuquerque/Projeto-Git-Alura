import re
import os
import unicodedata
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import xlsxwriter

# ---------------- CONFIGURAÇÃO E REGEX ----------------

RE_VALOR = re.compile(r'(-?\s*\d{1,3}(?:\.\d{3})*,\d{2})')
RE_DATE = re.compile(r'(\d{2}/\d{2})')
RE_PARCELA = re.compile(r'(\d{1,2}\s*/\s*\d{1,2})')

RE_FULL_TRANSACTION = re.compile(
    r'(\d{2}/\d{2})'
    r'(.*?)'
    r'(-?\s*\d{1,3}(?:\.\d{3})*,\d{2})',
    re.DOTALL
)

# ---------------- FUNÇÕES AUXILIARES ----------------

def normalizar(texto):
    if texto is None:
        return ""
    t = unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("utf-8").lower()
    return re.sub(r'\s+', ' ', t).strip()

def limpar_estabelecimento(estab_raw):
    if pd.isna(estab_raw):
        return ""
    limpo = str(estab_raw).replace("\n", " ").strip()
    limpo = re.sub(r'\s+', ' ', limpo).strip()
    limpo = RE_PARCELA.sub("", limpo).strip()
    limpo = re.sub(r'\s*\d{2}/\d{2}$', '', limpo).strip()
    limpo = limpo.strip("-").strip()
    return limpo

def calcular_parcelas_restantes(parcela_raw):
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

# ---------------- EXTRATOR ----------------

def extrair_lancamentos_fatura(raw_text):
    matches = RE_FULL_TRANSACTION.findall(raw_text)
    final_regs = []

    for data_raw, estab_temp, valor_text in matches:

        if re.search(r'-\s*\d', valor_text):
            continue

        try:
            valor_clean = valor_text.replace(" ", "").replace(".", "").replace(",", ".")
            valor_float = float(valor_clean)
        except:
            continue

        if valor_float < 0:
            continue

        parcela = ""
        m_parc = RE_PARCELA.search(estab_temp)
        if m_parc:
            parcela_raw = m_parc.group(1)
            parcela = parcela_raw.replace(" ", "")
            estab_temp = estab_temp.replace(parcela_raw, "", 1).strip()

        estabelecimento = limpar_estabelecimento(estab_temp)

        if len(estabelecimento) < 2:
            continue
        if any(key in normalizar(estabelecimento) for key in [
            'lancamentos', 'total', 'pagamento', 'vencimento', 'saque', 'compra', 'parcial'
        ]):
            continue

        final_regs.append({
            "Data": data_raw,
            "Estabelecimento": estabelecimento,
            "Valor_texto": valor_text.strip(),
            "Valor": valor_float,
            "Parcela": parcela
        })

    df = pd.DataFrame(final_regs)
    if df.empty:
        return []

    df["is_parc"] = df["Parcela"].apply(lambda x: 1 if x else 0)
    df = df.sort_values(by=["is_parc", "Data"], ascending=[False, True])
    df = df.drop(columns=["is_parc"]).reset_index(drop=True)

    df["Parcelas Restantes"] = df["Parcela"].apply(calcular_parcelas_restantes)
    return df.to_dict("records")

# ---------------- SALVAR EXCEL ----------------

def save_records_to_excel(records, path_out):
    df = pd.DataFrame(records)
    df = df.rename(columns={"Valor": "Valor (R$)"})
    cols = ["Data", "Estabelecimento", "Valor (R$)", "Parcela", "Parcelas Restantes"]
    df = df[cols]

    total_sum = df["Valor (R$)"].sum() if not df.empty else 0.0

    workbook = xlsxwriter.Workbook(path_out)
    ws = workbook.add_worksheet("Lançamentos")

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

class App:
    def __init__(self, root):
        self.root = root
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

        self.records = []

    def extract_and_preview(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text:
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
            return

        name = self.out_entry.get().strip()
        if not name.endswith(".xlsx"):
            name += ".xlsx"

        path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=name)
        if not path:
            return

        save_records_to_excel(self.records, path)
        messagebox.showinfo("Sucesso", f"Planilha salva em:\n{path}")

    def copy_text(self):
        txt = self.text_input.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        messagebox.showinfo("Copiado", "Texto copiado.")

# ---------------- INICIAR ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
