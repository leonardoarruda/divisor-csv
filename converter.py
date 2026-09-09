import csv
import os
import zipfile
import shutil
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, ttk

# Variável global para armazenar o caminho do arquivo selecionado
caminho_arquivo_global = ""

def selecionar_arquivo(entrada_texto):
    global caminho_arquivo_global
    # Abre a janela nativa do Windows para escolher o arquivo
    arquivo_selecionado = filedialog.askopenfilename(
        title="Selecione o arquivo CSV",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    if arquivo_selecionado:
        caminho_arquivo_global = arquivo_selecionado
        # Limpa o campo de texto e escreve o nome do arquivo selecionado
        entrada_texto.delete(0, "end")
        entrada_texto.insert(0, os.path.basename(arquivo_selecionado))

def executar_conversao():
    global caminho_arquivo_global
    
    if not caminho_arquivo_global:
        messagebox.showwarning("Aviso", "Por favor, selecione um arquivo CSV primeiro!")
        return
        
    try:
        linhas_limite = 1000  
        nome_base = os.path.splitext(os.path.basename(caminho_arquivo_global))[0]
        
        # Define a pasta onde o .exe está rodando atualmente
        pasta_do_exe = os.getcwd()
        
        # Cria uma pasta temporária para as partes
        pasta_temp = os.path.join(pasta_do_exe, f"temp_{nome_base}")
        os.makedirs(pasta_temp, exist_ok=True)
        
        # Gera o timestamp no formato AAAAMMDD_HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_zip = f"arquivos_convertidos_{timestamp}.zip"
        caminho_zip = os.path.join(pasta_do_exe, nome_zip)
        
        with open(caminho_arquivo_global, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f)
            
            # Captura o cabeçalho duplo específico do arquivo
            cabecalho_1 = next(leitor)
            cabecalho_2 = next(leitor)
            
            parte = 1
            linhas_atuais = []
            arquivos_criados = []
            
            for linha in leitor:
                linhas_atuais.append(linha)
                
                if len(linhas_atuais) == linhas_limite:
                    nome_saida = os.path.join(pasta_temp, f'{nome_base}_parte_{parte}.csv')
                    salvar_parte(nome_saida, cabecalho_1, cabecalho_2, linhas_atuais)
                    arquivos_criados.append(nome_saida)
                    parte += 1
                    linhas_atuais = []
            
            # Salva o restante (última parte)
            if linhas_atuais:
                nome_saida = os.path.join(pasta_temp, f'{nome_base}_parte_{parte}.csv')
                salvar_parte(nome_saida, cabecalho_1, cabecalho_2, linhas_atuais)
                arquivos_criados.append(nome_saida)

        if not arquivos_criados:
            shutil.rmtree(pasta_temp)
            messagebox.showwarning("Aviso", "O arquivo não possui dados além do cabeçalho.")
            return

        # Compacta tudo no arquivo ZIP final
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for arq in arquivos_criados:
                zipf.write(arq, os.path.basename(arq))
        
        # Limpa os arquivos temporários da pasta
        shutil.rmtree(pasta_temp)
        
        messagebox.showinfo("Sucesso!", f"Arquivo criado com sucesso!\n\nNome: {nome_zip}\nSalvo na pasta do programa.")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao processar:\n{str(e)}")

def salvar_parte(caminho_completo, cab_1, cab_2, dados):
    with open(caminho_completo, 'w', encoding='utf-8', newline='') as f_saida:
        escritor = csv.writer(f_saida, quoting=csv.QUOTE_MINIMAL)
        escritor.writerow(cab_1)
        escritor.writerow(cab_2)
        escritor.writerows(dados)

# --- Interface Gráfica (GUI) ---
def criar_gui():
    janela = Tk()
    janela.title("Divisor de CSV (1000 Linhas)")
    janela.geometry("450x180")
    janela.resizable(False, False)
    
    # Label explicativo
    lbl_instrucao = Label(janela, text="Selecione o arquivo CSV para dividir em partes de 1000 linhas:", font=("Arial", 10))
    lbl_instrucao.pack(pady=(20, 5))
    
    # Container para o Input e o Botão de Procurar ficarem lado a lado
    frame_procurar = ttk.Frame(janela)
    frame_procurar.pack(padx=20, fill="x")
    
    txt_arquivo = Entry(frame_procurar, font=("Arial", 10))
    txt_arquivo.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=4)
    
    btn_procurar = Button(
        frame_procurar, 
        text="Procurar...", 
        font=("Arial", 9),
        command=lambda: selecionar_arquivo(txt_arquivo)
    )
    btn_procurar.pack(side="right", ipady=2)
    
    # Botão de conversão grande embaixo
    btn_converter = Button(
        janela, 
        text="CONVERTER E GERAR ZIP", 
        font=("Arial", 11, "bold"), 
        bg="#2ecc71", 
        fg="white", 
        relief="raised",
        command=executar_conversao
    )
    btn_converter.pack(pady=25, padx=20, fill="x")
    
    janela.mainloop()

if __name__ == "__main__":
    criar_gui()
