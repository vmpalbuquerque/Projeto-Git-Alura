import os
from datetime import datetime
from docx import Document
from docx.shared import Inches
import tkinter as tk
from tkinter import filedialog, messagebox

# --- FUNÇÕES DE LÓGICA DO DOCUMENTO ---

def criar_documento_evidencia(caminhos_imagens, cenario_texto, titulo_documento="Relatorio_Evidencia"):
    """
    Cria um documento Word (.docx) com o cenário e UMA LISTA de imagens.
    """
    
    # Formata a data e hora para o nome do documento
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_documento = f"{titulo_documento}_{timestamp}.docx"
    
    try:
        # Inicia o Documento
        documento = Document()
        
        # Adiciona o Título Principal
        documento.add_heading('Evidências de Testes', 0)
        
        # Adiciona a Data e Hora da Geração
        documento.add_paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        documento.add_paragraph("---")
        
        # Adiciona o Cenário (Texto)
        documento.add_heading('Cenário de Teste / Descrição:', level=1)
        documento.add_paragraph(cenario_texto)
        
        # Adiciona a Imagem (Loop para múltiplas imagens)
        documento.add_heading('Evidências (Capturas de Tela):', level=1)

        if not caminhos_imagens:
            documento.add_paragraph("Nenhuma imagem anexada.")
        else:
            for i, caminho in enumerate(caminhos_imagens):
                documento.add_heading(f'Evidência {i+1}: {os.path.basename(caminho)}', level=2)
                
                # Adiciona a imagem, definindo a largura para 6 polegadas (tamanho padrão ideal)
                documento.add_picture(caminho, width=Inches(6))
                
        # Salva o Documento
        documento.save(nome_documento)
        
        return f"\n🎉 Documento de evidências criado com sucesso em: {os.path.abspath(nome_documento)}\nImagens anexadas: {len(caminhos_imagens)}"
        
    except FileNotFoundError:
        return f"❌ ERRO: Uma das imagens não foi encontrada."
    except Exception as e:
        return f"❌ Erro ao criar o documento: {e}"


# --- FUNÇÃO DA INTERFACE GRÁFICA (GUI) ---

class RoboEvidenciasApp:
    def __init__(self, master):
        self.master = master
        master.title("🤖 Robô Gerador de Evidências")
        
        # Variáveis de controle
        self.caminhos_completos = []
        self.imagens_selecionadas_display = tk.StringVar()
        self.imagens_selecionadas_display.set("Nenhuma imagem selecionada")
        
        # 1. Entrada do Cenário
        tk.Label(master, text="Descreva o Cenário de Teste:", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        self.cenario_entry = tk.Text(master, height=5, width=50)
        self.cenario_entry.pack(pady=5, padx=10)

        # 2. Seleção das Imagens
        tk.Label(master, text="Imagens Selecionadas:", font=('Arial', 10, 'bold')).pack(pady=(10, 0))
        
        # Exibe o caminho da imagem selecionada
        self.caminho_label = tk.Label(master, textvariable=self.imagens_selecionadas_display, width=50, bg='lightgray', anchor='w', wraplength=350)
        self.caminho_label.pack(pady=5, padx=10)
        
        # Botão para abrir o explorador de arquivos (Modificado para múltiplas seleções)
        self.botao_selecionar = tk.Button(master, text="📂 Selecionar Imagens (Prints)", command=self.selecionar_imagens)
        self.botao_selecionar.pack(pady=5)
        
        # 3. Botão de Execução
        self.botao_gerar = tk.Button(master, text="🚀 GERAR DOCUMENTO WORD", command=self.gerar_documento, bg='green', fg='white', font=('Arial', 12, 'bold'))
        self.botao_gerar.pack(pady=20)
        
        # 4. Status
        self.status_label = tk.Label(master, text="", fg='blue')
        self.status_label.pack(pady=(5, 10))

    def selecionar_imagens(self):
        """Abre a janela de diálogo para escolher MÚLTIPLOS arquivos de imagem."""
        
        # askopenfilenames permite a seleção de múltiplos arquivos
        caminhos = filedialog.askopenfilenames(
            initialdir=os.getcwd(), 
            title="Selecione as Imagens de Evidência (Pode selecionar várias)",
            filetypes=(("Arquivos PNG", "*.png"), ("Arquivos JPEG", "*.jpg"), ("Todos os arquivos", "*.*"))
        )
        
        if caminhos:
            self.caminhos_completos = list(caminhos)
            count = len(self.caminhos_completos)
            self.imagens_selecionadas_display.set(f"{count} imagem(ns) selecionada(s).")
            self.status_label.config(text=f"✅ {count} imagem(ns) pronta(s) para o documento.", fg='blue')
        else:
            self.caminhos_completos = []
            self.imagens_selecionadas_display.set("Nenhuma imagem selecionada")
            self.status_label.config(text="Selecione as imagens.", fg='gray')

    def gerar_documento(self):
        """Valida os dados e chama a função de criação do documento."""
        
        # '1.0' significa linha 1, caractere 0. tk.END é o fim do texto.
        cenario = self.cenario_entry.get("1.0", tk.END).strip()
        
        if not cenario:
            messagebox.showerror("Erro de Validação", "O campo 'Cenário de Teste' não pode estar vazio.")
            return

        if not self.caminhos_completos:
             messagebox.showerror("Erro de Validação", "Por favor, selecione pelo menos uma imagem de evidência.")
             return

        self.status_label.config(text="Criando documento... Aguarde.", fg='orange')
        self.master.update() # Força a atualização da interface para exibir a mensagem
        
        # Chama a função de criação do documento, passando a LISTA de caminhos
        resultado = criar_documento_evidencia(self.caminhos_completos, cenario)
        
        # Exibe o resultado na interface
        if "ERRO" in resultado:
            self.status_label.config(text=resultado, fg='red')
            messagebox.showerror("Erro", resultado)
        else:
            self.status_label.config(text=resultado, fg='green')
            messagebox.showinfo("Sucesso!", resultado)


if __name__ == "__main__":
    root = tk.Tk()
    # Define um tamanho mínimo para a janela
    root.minsize(400, 350) 
    app = RoboEvidenciasApp(root)
    root.mainloop()