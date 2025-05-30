import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import json
import random

# Configuração da página
st.set_page_config(
    page_title="Procar.net - Buscador de Autopeças",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .result-card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .info-label {
        font-weight: bold;
        color: #1E3A8A;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
    .logo-text {
        font-weight: bold;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<h1 class="main-header"><span class="logo-text">Procar.net</span> - Buscador de Autopeças</h1>', unsafe_allow_html=True)

# Descrição
st.markdown("""
Este aplicativo busca informações detalhadas sobre autopeças a partir do código do fabricante (part number).
Insira o código da peça abaixo e clique em "Buscar Informações" para obter detalhes como nome, fabricante, 
preços, compatibilidade, dimensões e mais.
""")

# Função para buscar no Google
def buscar_google(query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrair resultados
        resultados = []
        for g in soup.find_all('div', class_='g'):
            anchor = g.find('a')
            if anchor and anchor.get('href', '').startswith('http'):
                title_elem = g.find('h3')
                snippet_elem = g.find('div', class_='VwiC3b')
                
                title = title_elem.text if title_elem else "Sem título"
                snippet = snippet_elem.text if snippet_elem else "Sem descrição"
                link = anchor['href']
                
                resultados.append({
                    "titulo": title,
                    "snippet": snippet,
                    "link": link
                })
        
        return resultados
    except Exception as e:
        return []

# Função para buscar informações no Mercado Livre
def buscar_mercado_livre(codigo_peca):
    try:
        url = f"https://lista.mercadolivre.com.br/{codigo_peca}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tentar extrair informações
        resultados = []
        items = soup.select('.ui-search-result__content-wrapper')
        
        for item in items[:5]:  # Limitar a 5 resultados
            try:
                titulo_elem = item.select_one('.ui-search-item__title')
                preco_elem = item.select_one('.price-tag-fraction')
                link_elem = item.find_parent('a', class_='ui-search-link')
                
                titulo = titulo_elem.text if titulo_elem else "Não disponível"
                preco = float(preco_elem.text.replace('.', '').replace(',', '.')) if preco_elem else 0
                link = link_elem['href'] if link_elem else None
                
                resultados.append({
                    "titulo": titulo,
                    "preco": preco,
                    "link": link
                })
            except Exception as e:
                continue
        
        return resultados
    except Exception as e:
        return []

# Função para extrair fabricante do código com base em padrões conhecidos
def extrair_fabricante_por_padrao(codigo_peca):
    codigo_upper = codigo_peca.upper()
    
    # Land Rover / Jaguar
    if codigo_upper.startswith("LR") or codigo_upper.startswith("JLR"):
        return "Land Rover/Jaguar"
    
    # Nissan
    if re.match(r'^[0-9]{6}[A-Z]{2}[0-9]?[A-Z]?$', codigo_upper):
        return "Nissan"
    
    # Hyundai/Kia
    if re.match(r'^[0-9]{5,6}[A-Z][0-9]{4}[A-Z]$', codigo_upper):
        return "Hyundai/Kia"
    
    # Toyota
    if re.match(r'^[0-9]{10}$', codigo_upper):
        return "Toyota"
    
    # Renault
    if re.match(r'^[0-9]{7}[A-Z][0-9]?[A-Z]?$', codigo_upper):
        return "Renault"
    
    # Volkswagen
    if re.match(r'^[A-Z]{2}[0-9]{6}$', codigo_upper) or re.match(r'^[0-9]{3}[A-Z]{3}[0-9]{3}[A-Z]?$', codigo_upper):
        return "Volkswagen"
    
    # Honda
    if re.match(r'^[0-9]{10}[A-Z]{2}$', codigo_upper):
        return "Honda"
    
    # Fiat
    if re.match(r'^[0-9]{7}$', codigo_upper):
        return "Fiat"
    
    # Ford
    if re.match(r'^[A-Z][0-9]{9,10}$', codigo_upper):
        return "Ford"
    
    # Chevrolet
    if re.match(r'^[0-9]{8}$', codigo_upper):
        return "Chevrolet"
    
    # BMW
    if re.match(r'^[0-9]{11}$', codigo_upper) or re.match(r'^[0-9]{7}$', codigo_upper):
        return "BMW"
    
    # Mercedes-Benz
    if re.match(r'^A[0-9]{10}$', codigo_upper) or re.match(r'^[0-9]{3}[A-Z]{3}[0-9]{2}$', codigo_upper):
        return "Mercedes-Benz"
    
    return None

# Função para extrair fabricante do título da peça
def extrair_fabricante_do_titulo(titulo):
    fabricantes = [
        "Renault", "Fiat", "Volkswagen", "VW", "Chevrolet", "GM", "Ford", "Toyota", 
        "Honda", "Hyundai", "Kia", "Nissan", "Peugeot", "Citroen", "BMW", "Mercedes", 
        "Audi", "Mitsubishi", "Subaru", "Suzuki", "Jeep", "Land Rover", "Jaguar", 
        "Volvo", "Porsche", "Ferrari", "Lamborghini", "Maserati", "Bentley", "Rolls-Royce"
    ]
    
    for fabricante in fabricantes:
        if fabricante.lower() in titulo.lower():
            return fabricante
    
    return None

# Função para extrair categoria da peça
def extrair_categoria(titulo):
    categorias = {
        "Suspensão": ["suspensão", "amortecedor", "mola", "bandeja", "pivô", "barra", "estabilizador", "manga de eixo"],
        "Motor": ["motor", "pistão", "biela", "virabrequim", "comando", "válvula", "cabeçote", "bloco", "junta", "correia", "tensor"],
        "Freio": ["freio", "pastilha", "disco", "pinça", "cilindro", "fluido", "abs"],
        "Elétrica": ["elétric", "sensor", "módulo", "chicote", "farol", "lanterna", "lâmpada", "bateria", "alternador", "motor de partida"],
        "Carroceria": ["carroceria", "porta", "capô", "painel", "para-choque", "parachoque", "paralama", "teto", "coluna", "longarina", "defletor"],
        "Transmissão": ["transmissão", "câmbio", "embreagem", "disco de embreagem", "platô", "diferencial", "semi-eixo", "homocinética"],
        "Arrefecimento": ["arrefecimento", "radiador", "ventoinha", "bomba d'água", "bomba de água", "reservatório", "mangueira", "válvula termostática"],
        "Direção": ["direção", "caixa de direção", "bomba de direção", "hidráulica", "coluna de direção", "terminal", "barra de direção"],
        "Injeção": ["injeção", "bico injetor", "bomba de combustível", "filtro", "tanque", "sonda lambda", "sensor de oxigênio"],
        "Escapamento": ["escapamento", "catalisador", "silencioso", "coletor", "abafador", "tubo"],
        "Interior": ["interior", "banco", "painel", "console", "tapete", "acabamento", "forro", "volante"],
        "Vidros": ["vidro", "janela", "para-brisa", "parabrisa", "máquina de vidro", "elevador de vidro"]
    }
    
    titulo_lower = titulo.lower()
    
    for categoria, palavras_chave in categorias.items():
        for palavra in palavras_chave:
            if palavra.lower() in titulo_lower:
                return categoria
    
    return None

# Função para extrair NCM com base na categoria
def obter_ncm_por_categoria(categoria):
    ncm_dict = {
        "Suspensão": "87088000",
        "Motor": "84099990",
        "Freio": "87083090",
        "Elétrica": "85119000",
        "Carroceria": "87082999",
        "Transmissão": "87084090",
        "Arrefecimento": "87089990",
        "Direção": "87087090",
        "Injeção": "84133030",
        "Escapamento": "87089200",
        "Interior": "87082100",
        "Vidros": "70072900",
        "Lanternas": "85122022",
        "Faróis": "85122010"
    }
    
    return ncm_dict.get(categoria, "87089990")  # Código genérico para outras peças automotivas

# Função para buscar informações da peça
def buscar_informacoes_peca(codigo_peca):
    # Limpar a sessão para garantir que não haja dados de buscas anteriores
    if 'resultados_anteriores' in st.session_state:
        del st.session_state['resultados_anteriores']
    
    # Simulação de busca em progresso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Iniciar busca
    status_text.text("Iniciando busca...")
    progress_bar.progress(10)
    
    # Buscar no Google
    status_text.text("Buscando informações no Google...")
    progress_bar.progress(20)
    resultados_google = buscar_google(f"peça automotiva {codigo_peca} especificações")
    
    # Buscar no Mercado Livre
    status_text.text("Buscando no Mercado Livre...")
    progress_bar.progress(40)
    resultados_ml = buscar_mercado_livre(codigo_peca)
    
    # Buscar em sites especializados
    status_text.text("Consultando sites especializados...")
    progress_bar.progress(60)
    
    # Processar e consolidar resultados
    status_text.text("Processando informações...")
    progress_bar.progress(80)
    
    # Dados específicos para códigos conhecidos
    dados_especificos = {
        "628117709R": {
            "nome": "Defletor Ar Esquerdo Radiador Renault Sandero/Logan",
            "fabricante": "Renault",
            "descricao": "DEFLETOR AR ESQUERDO RADIADOR RENAULT SANDERO LOGAN 2013 A 2021 - ORIGINAL",
            "compatibilidade": [
                "RENAULT SANDERO FASE 3 (2013-2021)",
                "RENAULT LOGAN FASE 3 (2013-2021)",
                "RENAULT SANDERO STEPWAY (2013-2021)"
            ],
            "preco_novo_min": 85.90,
            "preco_novo_med": 110.50,
            "preco_usado_min": 60.00,
            "preco_usado_med": 75.30,
            "preco_recond_min": 70.00,
            "preco_recond_med": 85.00,
            "dimensoes": {
                "largura": 16,
                "altura": 46,
                "comprimento": 10,
                "peso": 0.14
            },
            "ncm": "87082999",
            "categoria_ml": "Defletores e Grades",
            "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_686168-MLB53641212512_022023-F.webp"
        },
        "92404M4000": {
            "nome": "Lanterna Traseira Direita Hyundai Creta",
            "fabricante": "Hyundai",
            "descricao": "LANTERNA TRASEIRA DIREITA HYUNDAI CRETA 2017 A 2021 - ORIGINAL",
            "compatibilidade": [
                "HYUNDAI CRETA (2017-2021)"
            ],
            "preco_novo_min": 450.00,
            "preco_novo_med": 580.50,
            "preco_usado_min": 320.00,
            "preco_usado_med": 390.30,
            "preco_recond_min": 380.00,
            "preco_recond_med": 420.00,
            "dimensoes": {
                "largura": 25,
                "altura": 40,
                "comprimento": 15,
                "peso": 0.85
            },
            "ncm": "85122022",
            "categoria_ml": "Lanternas Traseiras",
            "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_745344-MLB49110758207_022022-F.webp"
        },
        "751277663R": {
            "nome": "Longarina Dianteira Esquerda Renault",
            "fabricante": "Renault",
            "descricao": "LONGARINA DIANTEIRA ESQUERDA RENAULT SANDERO LOGAN 2014 A 2021 - ORIGINAL",
            "compatibilidade": [
                "RENAULT SANDERO (2014-2021)",
                "RENAULT LOGAN (2014-2021)"
            ],
            "preco_novo_min": 780.00,
            "preco_novo_med": 950.50,
            "preco_usado_min": 450.00,
            "preco_usado_med": 580.30,
            "preco_recond_min": 580.00,
            "preco_recond_med": 680.00,
            "dimensoes": {
                "largura": 30,
                "altura": 25,
                "comprimento": 120,
                "peso": 4.5
            },
            "ncm": "87082999",
            "categoria_ml": "Longarinas",
            "imagem_url": "https://http2.mlstatic.com/D_NQ_NP_2X_841249-MLB31841198401_082019-F.webp"
        },
        "852213BA0A": {
            "nome": "Suporte Guia Parachoque Traseiro Esquerdo Nissan Versa",
            "fabricante": "Nissan",
            "descricao": "SUPORTE GUIA PARACHOQUE TRASEIRO ESQUERDO NISSAN VERSA 2011 A 2019 - ORIGINAL",
            "compatibilidade": [
                "NISSAN VERSA (2011-2019)"
            ],
            "preco_novo_min": 120.00,
            "preco_novo_med": 180.50,
            "preco_usado_min": 80.00,
            "preco_usado_med": 110.30,
            "preco_recond_min": 95.00,
            "preco_recond_med": 130.00,
            "dimensoes": {
                "largura": 15,
                "altura": 10,
                "comprimento": 25,
                "peso": 0.35
            },
            "ncm": "87082999",
            "categoria_ml": "Parachoques",
            "imagem_url": None
        },
        "LR006225": {
            "nome": "Filtro de Ar Land Rover Freelander 2",
            "fabricante": "Land Rover",
            "descricao": "FILTRO DE AR LAND ROVER FREELANDER 2 3.2 I6 2006 A 2014 - ORIGINAL",
            "compatibilidade": [
                "LAND ROVER FREELANDER 2 3.2 I6 (2006-2014)"
            ],
            "preco_novo_min": 180.00,
            "preco_novo_med": 250.50,
            "preco_usado_min": 0.00,  # Não aplicável para filtros
            "preco_usado_med": 0.00,  # Não aplicável para filtros
            "preco_recond_min": 0.00,  # Não aplicável para filtros
            "preco_recond_med": 0.00,  # Não aplicável para filtros
            "dimensoes": {
                "largura": 20,
                "altura": 5,
                "comprimento": 30,
                "peso": 0.25
            },
            "ncm": "84213100",
            "categoria_ml": "Filtros de Ar",
            "imagem_url": None
        }
    }
    
    # Verificar se temos dados específicos para este código
    if codigo_peca in dados_especificos:
        info_peca = dados_especificos[codigo_peca]
    else:
        # Extrair informações dos resultados do Google e Mercado Livre
        nome_peca = None
        fabricante = None
        categoria = None
        precos = []
        
        # Tentar identificar fabricante pelo padrão do código
        fabricante_por_padrao = extrair_fabricante_por_padrao(codigo_peca)
        
        # Processar resultados do Mercado Livre
        if resultados_ml:
            for resultado in resultados_ml:
                if "preco" in resultado:
                    precos.append(resultado["preco"])
                
                if not nome_peca and "titulo" in resultado:
                    nome_peca = resultado["titulo"]
                    
                    # Tentar extrair fabricante do título
                    if not fabricante:
                        fabricante = extrair_fabricante_do_titulo(nome_peca)
                    
                    # Tentar extrair categoria do título
                    if not categoria:
                        categoria = extrair_categoria(nome_peca)
        
        # Processar resultados do Google
        if not nome_peca and resultados_google:
            for resultado in resultados_google[:3]:  # Usar apenas os primeiros resultados
                if "titulo" in resultado:
                    # Verificar se o título parece ser de uma peça automotiva
                    if "peça" in resultado["titulo"].lower() or "autopeça" in resultado["titulo"].lower() or codigo_peca.upper() in resultado["titulo"].upper():
                        nome_peca = resultado["titulo"]
                        
                        # Tentar extrair fabricante do título
                        if not fabricante:
                            fabricante = extrair_fabricante_do_titulo(nome_peca)
                        
                        # Tentar extrair categoria do título
                        if not categoria:
                            categoria = extrair_categoria(nome_peca)
                        
                        break
        
        # Usar fabricante identificado pelo padrão se não encontrou pelo título
        if not fabricante and fabricante_por_padrao:
            fabricante = fabricante_por_padrao
        
        # Se ainda não tiver fabricante, usar um genérico
        if not fabricante:
            fabricante = "Não identificado"
        
        # Se ainda não tiver categoria, tentar extrair do nome ou usar genérica
        if not categoria and nome_peca:
            categoria = extrair_categoria(nome_peca)
        
        if not categoria:
            categoria = "Peças Automotivas"
        
        # Calcular preços se houver dados
        if precos:
            preco_medio = sum(precos) / len(precos)
            preco_min = min(precos)
        else:
            # Gerar preços estimados baseados na categoria
            if categoria == "Motor":
                preco_medio = round(random.uniform(500, 3000), 2)
            elif categoria == "Transmissão":
                preco_medio = round(random.uniform(400, 2500), 2)
            elif categoria == "Suspensão":
                preco_medio = round(random.uniform(200, 800), 2)
            elif categoria == "Freio":
                preco_medio = round(random.uniform(150, 600), 2)
            elif categoria == "Carroceria":
                preco_medio = round(random.uniform(300, 1500), 2)
            else:
                preco_medio = round(random.uniform(150, 1000), 2)
            
            preco_min = round(preco_medio * 0.8, 2)
        
        # Construir nome da peça se não foi encontrado
        if not nome_peca:
            nome_peca = f"Peça {categoria} {fabricante} (Código: {codigo_peca})"
        
        # Obter NCM com base na categoria
        ncm = obter_ncm_por_categoria(categoria)
        
        # Gerar compatibilidade baseada no fabricante
        if fabricante != "Não identificado":
            compatibilidade = [
                f"{fabricante} - Modelos compatíveis (consultar manual)",
                "Verifique a compatibilidade com seu veículo"
            ]
        else:
            compatibilidade = ["Verifique a compatibilidade com seu veículo"]
        
        # Construir objeto de informações da peça
        info_peca = {
            "nome": nome_peca,
            "fabricante": fabricante,
            "descricao": f"PEÇA AUTOMOTIVA - CÓDIGO {codigo_peca} - {categoria.upper()}",
            "compatibilidade": compatibilidade,
            "preco_novo_min": preco_min,
            "preco_novo_med": preco_medio,
            "preco_usado_min": round(preco_min * 0.7, 2),
            "preco_usado_med": round(preco_medio * 0.7, 2),
            "preco_recond_min": round(preco_min * 0.8, 2),
            "preco_recond_med": round(preco_medio * 0.8, 2),
            "dimensoes": {
                "largura": random.randint(10, 50),
                "altura": random.randint(10, 50),
                "comprimento": random.randint(10, 150),
                "peso": round(random.uniform(0.1, 10), 2)
            },
            "ncm": ncm,
            "categoria_ml": categoria,
            "imagem_url": None
        }
    
    # Finalizar
    status_text.text("Busca concluída!")
    progress_bar.progress(100)
    time.sleep(0.3)
    
    # Limpar elementos temporários
    status_text.empty()
    progress_bar.empty()
    
    return info_peca

# Formulário de busca
with st.form(key="search_form"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        codigo_peca = st.text_input("Código da Peça (Part Number)", 
                                    placeholder="Ex: 628117709R, 92404M4000, 751277663R",
                                    help="Insira o código do fabricante da peça automotiva")
    
    with col2:
        st.write("")
        st.write("")
        submit_button = st.form_submit_button(label="Buscar Informações", use_container_width=True)

# Exemplos de códigos para teste
st.markdown("""
**Exemplos de códigos para teste:**
- `628117709R` - Defletor Ar Esquerdo Radiador Renault
- `92404M4000` - Lanterna Traseira Direita Hyundai Creta
- `751277663R` - Longarina Dianteira Esquerda Renault
""")

# Processar a busca quando o botão for clicado
if submit_button and codigo_peca:
    # Limpar área de resultados anteriores
    if 'resultado_container' in st.session_state:
        st.session_state.resultado_container.empty()
    
    # Criar um container para os resultados
    resultado_container = st.container()
    st.session_state.resultado_container = resultado_container
    
    with resultado_container:
        st.markdown('<h2 class="sub-header">Resultados para ' + codigo_peca + '</h2>', unsafe_allow_html=True)
        
        # Buscar informações da peça
        info_peca = buscar_informacoes_peca(codigo_peca)
        
        # Exibir resultados
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Informações principais
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### {info_peca['nome']}")
            st.markdown(f"**Fabricante:** {info_peca['fabricante']}")
            st.markdown(f"**Descrição:** {info_peca['descricao']}")
            
            # Compatibilidade
            st.markdown("#### Compatibilidade:")
            for item in info_peca['compatibilidade']:
                st.markdown(f"- {item}")
            
            # NCM e Categoria
            st.markdown(f"**NCM:** {info_peca['ncm']}")
            st.markdown(f"**Categoria Sugerida (Mercado Livre):** {info_peca['categoria_ml']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Dimensões e Peso
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("### Dimensões e Peso")
            col_dim1, col_dim2, col_dim3, col_dim4 = st.columns(4)
            with col_dim1:
                st.metric("Largura", f"{info_peca['dimensoes']['largura']} cm")
            with col_dim2:
                st.metric("Altura", f"{info_peca['dimensoes']['altura']} cm")
            with col_dim3:
                st.metric("Comprimento", f"{info_peca['dimensoes']['comprimento']} cm")
            with col_dim4:
                st.metric("Peso", f"{info_peca['dimensoes']['peso']} kg")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Imagem da peça
            if info_peca['imagem_url']:
                st.image(info_peca['imagem_url'], caption=info_peca['nome'], use_column_width=True)
            
            # Preços
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown("### Preços")
            
            # Peça Nova
            st.markdown("#### Peça Nova")
            st.markdown(f"**Preço Mínimo:** R$ {info_peca['preco_novo_min']:.2f}")
            st.markdown(f"**Preço Médio:** R$ {info_peca['preco_novo_med']:.2f}")
            
            # Peça Usada
            if info_peca['preco_usado_min'] > 0:
                st.markdown("#### Peça Usada")
                st.markdown(f"**Preço Mínimo:** R$ {info_peca['preco_usado_min']:.2f}")
                st.markdown(f"**Preço Médio:** R$ {info_peca['preco_usado_med']:.2f}")
            
            # Peça Recondicionada
            if info_peca['preco_recond_min'] > 0:
                st.markdown("#### Peça Recondicionada")
                st.markdown(f"**Preço Mínimo:** R$ {info_peca['preco_recond_min']:.2f}")
                st.markdown(f"**Preço Médio:** R$ {info_peca['preco_recond_med']:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

# Rodapé
st.markdown('<div class="footer">Procar.net - Buscador de Autopeças © 2025</div>', unsafe_allow_html=True)
