import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import PyPDF2
import re


def sanitize_filename(filename):
    sanitized = re.sub(r'[^\w\s.-]', '', filename)
    sanitized = sanitized.replace(' ', '_')
    sanitized = sanitized.replace('\n', '')
    sanitized = sanitized.lstrip('0')  # Remove os zeros à esquerda
    return sanitized


def find_and_rename_strings(folder_path, search_string, progress_bar, status_label):
    pdf_files = [filename for filename in os.listdir(folder_path) if filename.endswith('.pdf')]
    total_files = len(pdf_files)
    processed_files = 0

    for idx, filename in enumerate(pdf_files, start=1):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                index = text.find(search_string)
                if index != -1:
                    em_index = text.find('em', index + len(search_string))
                    if em_index != -1:
                        # Encontra a substring entre "protocolado" (sem espaço) e "em"
                        substring = text[index + len(search_string):em_index]
                        # Remove caracteres que não são números
                        new_filename = ''.join(filter(str.isdigit, substring))
                        if not new_filename:
                            new_filename = 'NoDigitsFound'
                        new_filename = f"{new_filename}.pdf"
                    else:
                        new_filename = f"{text[index + len(search_string):]}.pdf"

                    new_filename = sanitize_filename(new_filename)
                    new_file_path = os.path.join(folder_path, new_filename)

                    if os.path.exists(new_file_path):
                        status_label.config(text=f"Arquivo {new_filename} já existe. Pulando renomeação.")
                        break

                    pdf_file.close()
                    os.rename(file_path, new_file_path)
                    processed_files += 1
                    break

        progress_bar["value"] = (idx / total_files) * 100
        status_label.config(text=f"Renomeando arquivo {idx}/{total_files}")
        progress_bar.update()

    message = f"Processo concluído. Arquivos renomeados: {processed_files}/{total_files}."
    messagebox.showinfo("Concluído", message)

    # Abrir a pasta dos arquivos processados após a conclusão
    os.startfile(folder_path)


def select_directory():
    # Destrói o frame anterior se já existir
    if "frame" in root.children:
        root.children["frame"].destroy()

    folder_path = filedialog.askdirectory()
    search_string = "protocolado"

    frame = tk.Frame(root)  # Cria um novo frame para a barra de progresso e o rótulo de status
    frame.pack(pady=10)

    progress_bar = ttk.Progressbar(frame, length=500, mode="determinate")
    progress_bar.pack(pady=5)

    status_label = tk.Label(frame, text="", font=("Helvetica", 12))
    status_label.pack(pady=5)

    find_and_rename_strings(folder_path, search_string, progress_bar, status_label)


root = tk.Tk()
root.title("Utilitário para renomear PDF's em lote")
root.geometry("400x300")
root.resizable(False, False)

label = tk.Label(root, text="Selecione o diretório:", font=("Helvetica", 14))
label.pack(pady=10)

select_button = tk.Button(root, text="Selecionar diretório e renomear", command=select_directory,
                          font=("Helvetica", 12))
select_button.pack(pady=10)

root.mainloop()
