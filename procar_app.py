import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from bs4 import BeautifulSoup
import re # Import regular expressions for price cleaning

def buscar_mercado_livre(codigo_peca):
    """Busca informações da peça no Mercado Livre."""
    search_url = f"https://lista.mercadolivre.com.br/{codigo_peca}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    resultados = {
        "nome": "Não encontrado",
        "preco_medio_novo": "N/A",
        "preco_medio_usado": "N/A",
        "categoria_sugerida": "Não encontrada"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status() # Verifica se houve erro HTTP
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- Encontrar Nome (primeiro item) ---
        # Tenta encontrar o título do primeiro item nos resultados
        # A classe pode mudar, é preciso inspecionar o HTML do ML
        primeiro_item_tag = soup.find('h2', class_='ui-search-item__title')
        if primeiro_item_tag:
            resultados["nome"] = primeiro_item_tag.text.strip()
        else:
             # Tenta outra classe comum
             primeiro_item_tag = soup.find('a', class_='ui-search-item__group__element')
             if primeiro_item_tag and primeiro_item_tag.find('h2'):
                 resultados["nome"] = primeiro_item_tag.find('h2').text.strip()

        # --- Encontrar Preço Médio (simplificado - média dos primeiros) ---
        # A classe do preço também pode mudar
        precos_tags = soup.find_all('span', class_='andes-money-amount__fraction')
        precos_numericos = []
        for tag in precos_tags:
            # Limpa o preço (remove pontos, substitui vírgula por ponto)
            preco_texto = tag.text.strip().replace('.', '').replace(',', '.')
            try:
                precos_numericos.append(float(preco_texto))
            except ValueError:
                continue # Ignora se não for um número válido
        
        if precos_numericos:
            # Simplificação: Calcula a média dos preços encontrados na primeira página
            # Idealmente, separaríamos novo/usado, mas isso é mais complexo via scraping
            preco_medio = sum(precos_numericos) / len(precos_numericos)
            resultados["preco_medio_novo"] = f"R$ {preco_medio:.2f}" # Assume novo por simplicidade
            resultados["preco_medio_usado"] = "Verificar manualmente" # Indicar que precisa de análise

        # --- Encontrar Categoria Sugerida (simplificado - do primeiro item) ---
        # Tenta encontrar a categoria no breadcrumb
        breadcrumb_tags = soup.find_all('li', class_='andes-breadcrumb__item')
        if len(breadcrumb_tags) > 1:
            # Pega a penúltima categoria como sugestão
            resultados["categoria_sugerida"] = breadcrumb_tags[-2].text.strip()
        elif breadcrumb_tags:
             resultados["categoria_sugerida"] = breadcrumb_tags[0].text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar Mercado Livre: {e}")
        messagebox.showerror("Erro de Rede", f"Não foi possível conectar ao Mercado Livre: {e}")
        return None # Retorna None em caso de erro de rede
    except Exception as e:
        print(f"Erro ao processar dados do Mercado Livre: {e}")
        # Não mostra messagebox aqui para não interromper se for só erro de parsing

    return resultados

def buscar_informacoes():
    codigo_peca = entry_codigo.get()
    
    if not codigo_peca:
        messagebox.showwarning("Entrada Inválida", "Por favor, insira o código da peça.")
        return

    # Limpa a área de resultados
    text_resultados.config(state=tk.NORMAL)
    text_resultados.delete(1.0, tk.END)
    text_resultados.insert(tk.END, f"Buscando informações para o código: {codigo_peca}...\n")
    text_resultados.config(state=tk.DISABLED)
    root.update_idletasks() # Atualiza a interface para mostrar a mensagem

    # --- Busca no Mercado Livre ---
    resultados_ml = buscar_mercado_livre(codigo_peca)
    
    # Atualiza a área de resultados
    text_resultados.config(state=tk.NORMAL)
    text_resultados.delete(1.0, tk.END) # Limpa a mensagem "Buscando..."
    
    if resultados_ml:
        texto_final = f"--- Resultados para {codigo_peca} (Fonte: Mercado Livre) ---\n"
        texto_final += f"Nome Sugerido: {resultados_ml.get('nome', 'Não encontrado')}\n"
        texto_final += f"Preço Médio (Novo - Estimado): {resultados_ml.get('preco_medio_novo', 'N/A')}\n"
        texto_final += f"Preço Médio (Usado - Estimado): {resultados_ml.get('preco_medio_usado', 'N/A')}\n"
        texto_final += f"Categoria Sugerida: {resultados_ml.get('categoria_sugerida', 'Não encontrada')}\n\n"
        texto_final += "--- Próximos Passos ---\n"
        texto_final += "- Implementar busca em outras fontes (Google, sites especializados)\n"
        texto_final += "- Buscar Fabricante, Descrição, Compatibilidade, Dimensões, NCM\n"
        texto_final += "- Refinar cálculo de preços (separar novo/usado/recondicionado)\n"
        text_resultados.insert(tk.END, texto_final)
    else:
        text_resultados.insert(tk.END, f"Não foi possível obter resultados para {codigo_peca} do Mercado Livre.")
        
    text_resultados.config(state=tk.DISABLED)

# --- Configuração da Interface Gráfica --- 
root = tk.Tk()
root.title("Procar.net - Buscador de Peças")

# Frame principal
frame_principal = ttk.Frame(root, padding="10")
frame_principal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Entrada Código da Peça
ttk.Label(frame_principal, text="Código da Peça (Fabricante/Part Number):").grid(row=0, column=0, sticky=tk.W, pady=2)
entry_codigo = ttk.Entry(frame_principal, width=40)
entry_codigo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

# Botão Buscar
btn_buscar = ttk.Button(frame_principal, text="Buscar Informações", command=buscar_informacoes)
btn_buscar.grid(row=2, column=0, columnspan=3, pady=10)

# Área de Resultados
ttk.Label(frame_principal, text="Resultados:").grid(row=3, column=0, sticky=tk.W, pady=2)
text_resultados = tk.Text(frame_principal, width=80, height=20, wrap=tk.WORD, state=tk.DISABLED)
text_resultados.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))

# Scrollbar para a área de resultados
scrollbar = ttk.Scrollbar(frame_principal, orient=tk.VERTICAL, command=text_resultados.yview)
scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S))
text_resultados['yscrollcommand'] = scrollbar.set

# Configuração de redimensionamento
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame_principal.columnconfigure(1, weight=1)

# Inicia a interface
root.mainloop()

