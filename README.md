# Procar.net - Buscador de Autopeças

## Visão Geral

O Procar.net é um aplicativo web desenvolvido com Streamlit que permite buscar informações detalhadas sobre autopeças a partir do código do fabricante (part number). O aplicativo consulta múltiplas fontes e apresenta dados organizados sobre a peça, incluindo nome, fabricante, preços, compatibilidade, dimensões e mais.

## Funcionalidades

- **Busca por código de peça**: Insira o código do fabricante e obtenha informações detalhadas
- **Detecção automática de fabricante**: Identifica o fabricante com base no padrão do código
- **Consulta em múltiplas fontes**: Mercado Livre e outras fontes especializadas
- **Informações completas**: Nome, fabricante, descrição, compatibilidade, preços, dimensões, peso, NCM e categoria
- **Interface amigável**: Design moderno e responsivo para fácil visualização dos resultados

## Como Usar

1. Acesse o aplicativo através do link: [Procar.net Streamlit App](https://procar-net.streamlit.app/)
2. Digite o código da peça no campo de busca
3. Clique no botão "Buscar Informações"
4. Visualize os resultados organizados por seções

### Exemplos de Códigos para Teste

- `628117709R` - Defletor Ar Esquerdo Radiador Renault
- `92404M4000` - Lanterna Traseira Direita Hyundai Creta
- `751277663R` - Longarina Dianteira Esquerda Renault

## Executando Localmente

Se desejar executar o aplicativo em seu próprio computador:

1. Certifique-se de ter Python 3.7+ instalado
2. Clone este repositório ou baixe o arquivo `app.py`
3. Instale as dependências:
   ```
   pip install streamlit requests beautifulsoup4
   ```
4. Execute o aplicativo:
   ```
   streamlit run app.py
   ```
5. O aplicativo será aberto automaticamente em seu navegador

## Publicando no Streamlit Cloud

Para publicar sua própria versão do aplicativo no Streamlit Cloud:

1. Crie uma conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Crie um repositório no GitHub com o código do aplicativo
3. No Streamlit Cloud, clique em "New app" e selecione seu repositório
4. Configure as opções de implantação e clique em "Deploy"
5. Seu aplicativo estará disponível em um link público

## Estrutura do Código

O aplicativo é composto por um único arquivo `app.py` com as seguintes seções:

- **Configuração e estilo**: Define a aparência e layout do aplicativo
- **Funções de busca**: Implementa a lógica para buscar informações em diferentes fontes
- **Interface do usuário**: Define os elementos de entrada e saída
- **Processamento de resultados**: Organiza e exibe os dados encontrados

## Limitações Atuais

- A busca em tempo real no Mercado Livre pode ser lenta em alguns casos
- Alguns códigos de peça podem não retornar resultados precisos
- As dimensões e peso são estimados para códigos não cadastrados
- A detecção de fabricante funciona apenas para padrões conhecidos de códigos

## Próximas Melhorias

- Adicionar mais fontes de busca (sites de fabricantes, catálogos especializados)
- Melhorar a precisão da detecção de fabricante
- Implementar cache para resultados frequentes
- Adicionar suporte para busca por nome da peça
- Permitir upload de imagens para identificação visual

## Suporte

Para dúvidas ou sugestões, entre em contato através do email: claudir2001@gmail.com
