# 🛡️ Hub de Produtividade — TI PMDD

Suíte de ferramentas de produtividade para escritório, desenvolvida pela TI PMDD.

---

## 📁 Estrutura do projeto

```
hub_pmdd/
│
├── app.py                        # Orquestrador principal (NÃO editar a lógica)
├── requirements.txt              # Dependências Python
│
└── modulos/
    ├── __init__.py               # Marca o diretório como pacote Python
    │
    ├── img_para_pdf.py           # 🖼️ Imagens → PDF
    ├── redimensionador_imagem.py # 📐 Redimensionador de Imagens
    │
    ├── unificador_pdf.py         # 📎 Unificador de PDFs
    ├── divisor_pdf.py            # ✂️ Divisor de PDFs
    ├── divisor_pdf.py            # ✂️ Divisor por tamanho
    ├── pdf_para_texto.py         # 📝 PDF → Texto
    │
    ├── consolidador_planilhas.py # 🗂️ Consolidador de Planilhas
    ├── comparador_arquivos.py    # 🔍 Comparador de Arquivos
    ├── limpador_dados.py         # 🧹 Limpador de Dados
    │
    ├── concatenador_txt.py       # 📋 Concatenador de TXT
    ├── formatador_texto.py       # ✏️ Formatador de Texto
    │
    └── relatorio_diretorio.py    # 📁 Relatório de Diretório
```

---

## 🚀 Como instalar e executar

```bash
# 1. Crie e ative um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o app
streamlit run app.py
```

---

## ➕ Como adicionar um novo módulo

1. Crie um arquivo `.py` dentro de `modulos/` — ex: `modulos/meu_modulo.py`

2. O arquivo **deve** conter as seguintes variáveis e a função `render()`:

```python
# modulos/meu_modulo.py

MODULE_NAME     = "Nome da Ferramenta"       # Exibido no menu e no header
MODULE_ICON     = "🔧"                        # Emoji exibido no menu
MODULE_CATEGORY = "🛠️ Minha Categoria"        # Agrupa ferramentas no menu lateral
MODULE_DESC     = "Descrição curta da ferramenta."  # Exibida no header e na tela inicial

def render():
    import streamlit as st
    # --- Toda a lógica e UI da ferramenta vai aqui ---
    st.write("Olá! Esta é minha nova ferramenta.")
```

3. **Reinicie o Streamlit** (`Ctrl+C` e `streamlit run app.py`).

4. O módulo aparecerá automaticamente no menu lateral, agrupado pela categoria definida.

> ⚠️ **Sem `MODULE_NAME` ou sem `def render()`** → o arquivo é silenciosamente ignorado pelo orquestrador.

---

## 🛠️ Ferramentas incluídas

| Categoria | Ferramenta | Descrição |
|---|---|---|
| 🖼️ Imagens | Imagens → PDF | Converte JPG/PNG em PDF |
| 🖼️ Imagens | Redimensionador | Redimensiona por px ou % |
| 📄 PDFs | Unificador | Mescla múltiplos PDFs |
| 📄 PDFs | Divisor | Extrai páginas específicas |
| 📄 PDFs | PDF → Texto | Extrai texto de PDFs |
| 📄 PDFs | Divisor | Extrai paginas por tamanho do arquivo |
| 📊 Planilhas / Dados | Consolidador | Merge de Excel/CSV |
| 📊 Planilhas / Dados | Comparador | Diff entre dois arquivos |
| 📊 Planilhas / Dados | Limpador | Remove vazios e duplicatas |
| 📝 Texto | Concatenador TXT | Une arquivos .txt |
| 📝 Texto | Formatador | Maiúsculas, espaços, acentos |
| 🛠️ Utilitários | Relatório de Diretório | Inventaria arquivos |

---

**Desenvolvido pela TI PMDD — 2026**
