import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
from docx.enum.section import WD_ORIENT, WD_SECTION

# --- CONFIGURAÇÕES GLOBAIS E PORTABILIDADE ---

# Tenta definir o diretório base para garantir a portabilidade do caminho da logo
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd() # Fallback

# Caminho para a logo (AGORA RELATIVO, deve estar na mesma pasta do script)
LOGO_PATH = os.path.join(BASE_DIR, "logo_porto_2.png")

# Cor azul do cabeçalho (sem #)
HEADER_BLUE = "009CDE"
# Cor branca para o texto do cabeçalho
HEADER_TEXT_COLOR = RGBColor(255, 255, 255) 
# Cor preta para o corpo do documento
BODY_TEXT_COLOR = RGBColor(0, 0, 0) 

# ---------------- utilidades OXML ----------------
def set_cell_background(cell, fill):
    """
    Define o preenchimento de cor de fundo de uma célula (hex sem '#') usando OXML.
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tcPr.append(shd)

# ---------------- formatação global ----------------
def aplicar_formato_run(run, tamanho_pt=None, cor=BODY_TEXT_COLOR):
    """Aplica Calibri, negrito, cor e tamanho opcional a um run."""
    run.font.name = "Calibri"
    run.bold = True
    run.font.color.rgb = cor # Usa a cor passada (padrão é preta)
    if tamanho_pt:
        run.font.size = Pt(tamanho_pt)

def aplicar_formato_paragrafo(p, tamanho_pt=None, cor=BODY_TEXT_COLOR):
    """Aplica o formato padrão a todos os runs de um parágrafo recém-criado."""
    # Se parágrafo não tiver runs (correção), cria um run vazio
    if not p.runs:
        r = p.add_run()
        aplicar_formato_run(r, tamanho_pt, cor)
    else:
        for run in p.runs:
            aplicar_formato_run(run, tamanho_pt, cor)

def padronizar_documento(documento):
    """Garante que toda run no documento esteja em Calibri, negrito e preta (inclui tabelas)."""
    for par in documento.paragraphs:
        for run in par.runs:
            if run.font.color.rgb != HEADER_TEXT_COLOR:
                 aplicar_formato_run(run)
    for tbl in documento.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for par in cell.paragraphs:
                    for run in par.runs:
                        if run.font.color.rgb != HEADER_TEXT_COLOR:
                             aplicar_formato_run(run)

# ---------------- helpers de imagem ----------------
def file_timestamp(path):
    # Função mantida, mas não utilizada no documento final, apenas se precisar de debug
    try:
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ""

def inserir_imagem_com_titulo(documento, caminho_imagem, largura_inch=6.0):
    """
    Insere imagem SEM legenda no documento.
    Ajusta largura para Inches(largura_inch).
    """
    nome = os.path.basename(caminho_imagem)
    
    # ❌ CÓDIGO DE LEGENDA REMOVIDO AQUI:
    # par_legend = documento.add_paragraph() 
    # run = par_legend.add_run(f"Print: {nome}  (capturado em {file_timestamp(caminho_imagem)})")
    # aplicar_formato_run(run, tamanho_pt=9)
    # par_legend.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    
    # Inserir imagem redimensionada para a largura em polegadas
    try:
        documento.add_picture(caminho_imagem, width=Inches(largura_inch))
    except Exception as e:
        p_err = documento.add_paragraph(f"[ERRO AO INSERIR IMAGEM: {nome}] - {e}")
        aplicar_formato_paragrafo(p_err, tamanho_pt=9, cor=RGBColor(255, 0, 0)) # Erro em vermelho

# ---------------- função principal de criação ----------------
def criar_documento_porto(caminhos_imagens, cenario_texto, titulo_documento="Relatorio_Evidencias_Porto"):
    """
    Cria o documento com layout Porto Seguro e salva .docx
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_documento = f"{titulo_documento}_{timestamp}.docx"
    doc = Document()
    # Define as margens do documento
    section = doc.sections[0]
    
    # Margem Esquerda: 0.5 polegadas (para empurrar o conteúdo para a esquerda)
    section.left_margin = Inches(0.5) 
    
    # Você pode ajustar as outras se necessário:
    section.right_margin = Inches(0.75) 
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)

    # --- Cabeçalho estilizado com tabela 1x2 (texto à esquerda, logo à direita) ---
    tabela = doc.add_table(rows=1, cols=2)
    tabela.autofit = True
    a_cel_titulo = tabela.columns[0]
    a_cel_logo = tabela.columns[1]
    a_cel_titulo.width = Inches(5)
    a_cel_logo.width = Inches(2)

    cel_titulo = tabela.rows[0].cells[0]
    cel_logo = tabela.rows[0].cells[1]

    # Pinta fundo das células com azul (ambas para parecer faixa)
    set_cell_background(cel_titulo, HEADER_BLUE)
    set_cell_background(cel_logo, HEADER_BLUE)

    # Título grande à esquerda
    p_t = cel_titulo.paragraphs[0]
    p_t.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    run_t = p_t.add_run("EVIDÊNCIAS DE TESTES")
    
    # Define a cor do texto do cabeçalho como BRANCA para contraste!
    aplicar_formato_run(run_t, tamanho_pt=20, cor=HEADER_TEXT_COLOR) 
    
    p_t.space_after = Pt(6)

    # Logo à direita
    if os.path.exists(LOGO_PATH):
        p_logo = cel_logo.paragraphs[0]
        p_logo.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        try:
            p_logo.add_run().add_picture(LOGO_PATH, width=Inches(1.5))
        except Exception as e:
            p_logo.add_run("LOGO").bold = True
    else:
        # Se não existir logo, escreve aviso
        p_logo = cel_logo.paragraphs[0]
        p_logo.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        run_missing = p_logo.add_run("LOGO NÃO ENCONTRADA")
        aplicar_formato_run(run_missing, tamanho_pt=10, cor=HEADER_TEXT_COLOR) # Cor branca para contraste

    # Espaço após cabeçalho
    doc.add_paragraph("")


    # --- Seção: Cenário de Teste / Descrição ---
    h1 = doc.add_paragraph()
    run_h1 = h1.add_run("Cenário de Teste / Descrição:")
    aplicar_formato_run(run_h1, tamanho_pt=14)
    h1.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    doc.add_paragraph("")  # pequena quebra

    p_cenario = doc.add_paragraph()
    run_cenario = p_cenario.add_run(cenario_texto)
    aplicar_formato_run(run_cenario, tamanho_pt=11)
    p_cenario.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

    doc.add_paragraph("")

    # --- Seção: Evidências ---
    h2 = doc.add_paragraph()
    run_h2 = h2.add_run("Evidências:")
    aplicar_formato_run(run_h2, tamanho_pt=14)

    doc.add_paragraph("")

    if not caminhos_imagens:
        p_empty = doc.add_paragraph()
        run_empty = p_empty.add_run("Nenhuma imagem anexada.")
        aplicar_formato_run(run_empty, tamanho_pt=11)
    else:
        for i, caminho in enumerate(caminhos_imagens):
            # Subtítulo para cada evidência
            p_ev = doc.add_paragraph()
            # ❌ ALTERAÇÃO AQUI: Removido o os.path.basename(caminho) para não mostrar o nome do arquivo.
            run_ev = p_ev.add_run(f"Evidência {i+1}")
            aplicar_formato_run(run_ev, tamanho_pt=12)

            doc.add_paragraph("")  # pular linha

            inserir_imagem_com_titulo(doc, caminho, largura_inch=6.0)

            doc.add_paragraph("")

    # Salva documento
    doc.save(nome_documento)
    return os.path.abspath(nome_documento)

# ---------------- GUI simples ----------------
class AppGUI:
    def __init__(self, master):
        self.master = master
        master.title("Robô Evidências - Modelo Porto Seguro")
        master.minsize(460, 380)

        tk.Label(master, text="Cenário de Teste (cole o texto abaixo):", font=("Calibri", 11, "bold")).pack(pady=(8,0))
        self.texto = tk.Text(master, height=6, width=70, font=("Calibri", 11))
        self.texto.pack(padx=10, pady=6)

        tk.Label(master, text="Imagens selecionadas:", font=("Calibri", 11, "bold")).pack(pady=(6,0))
        self.var_display = tk.StringVar(value="Nenhuma imagem selecionada")
        self.label_display = tk.Label(master, textvariable=self.var_display, bg="lightgray", width=60, anchor="w", wraplength=420, font=("Calibri", 10))
        self.label_display.pack(padx=10, pady=6)

        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=6)

        tk.Button(btn_frame, text="Selecionar Imagens", command=self.selecionar_imagens, font=("Calibri", 11, "bold")).grid(row=0, column=0, padx=6)
        tk.Button(btn_frame, text="Gerar Documento (DOCX)", command=self.gerar, bg="green", fg="white", font=("Calibri", 11, "bold")).grid(row=0, column=1, padx=6)

        self.status = tk.Label(master, text="", font=("Calibri", 10, "bold"))
        self.status.pack(pady=(8,6))

        self.caminhos = []

    def selecionar_imagens(self):
        initial_dir = BASE_DIR if os.path.exists(BASE_DIR) else os.getcwd()
        
        arquivos = filedialog.askopenfilenames(title="Selecione imagens de evidência",
                                               filetypes=[("Imagens", "*.png *.jpg *.jpeg"), ("Todos os arquivos", "*.*")],
                                               initialdir=initial_dir)
        if arquivos:
            self.caminhos = list(arquivos)
            self.var_display.set(f"{len(self.caminhos)} imagem(ns) selecionada(s).")
            self.status.config(text="Imagens carregadas.", fg="black")
        else:
            self.caminhos = []
            self.var_display.set("Nenhuma imagem selecionada")
            self.status.config(text="Nenhuma imagem selecionada.", fg="red")

    def gerar(self):
        texto = self.texto.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showerror("Erro", "O campo do cenário não pode ficar vazio.")
            return
        if not self.caminhos:
            messagebox.showerror("Erro", "Selecione ao menos uma imagem.")
            return

        self.status.config(text="Gerando documento...", fg="orange")
        self.master.update()

        try:
            caminho_doc = criar_documento_porto(self.caminhos, texto)
            self.status.config(text=f"Documento criado: {caminho_doc}", fg="green")
            messagebox.showinfo("Sucesso", f"Documento criado:\n{caminho_doc}")
        except Exception as e:
            self.status.config(text=f"Erro: {e}", fg="red")
            messagebox.showerror("Erro", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()