"""
Módulo: Formatador de Texto
Categoria: 📝 Texto
"""

import re
import io
import streamlit as st

MODULE_NAME     = "Formatador de Texto"
MODULE_ICON     = "✏️"
MODULE_CATEGORY = "📝 Texto"
MODULE_DESC     = "Aplica transformações de formatação a textos: maiúsculas, minúsculas, espaços e mais."

MAX_FILE_SIZE_MB = 5


def _decode(data: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def apply_transforms(text: str, opts: dict) -> str:
    if opts.get("strip_leading_trailing"):
        text = text.strip()
    if opts.get("strip_line_spaces"):
        text = "\n".join(line.strip() for line in text.splitlines())
    if opts.get("remove_blank_lines"):
        text = "\n".join(line for line in text.splitlines() if line.strip())
    if opts.get("collapse_spaces"):
        text = re.sub(r"[ \t]+", " ", text)
    if opts.get("remove_accents"):
        import unicodedata
        text = unicodedata.normalize("NFD", text)
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    case = opts.get("case")
    if case == "MAIÚSCULAS":
        text = text.upper()
    elif case == "minúsculas":
        text = text.lower()
    elif case == "Título (Primeira Letra Maiúscula)":
        text = text.title()
    elif case == "Sentença (1ª letra de cada frase)":
        text = ". ".join(s.strip().capitalize() for s in text.split("."))
    return text


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Cole o texto diretamente **ou** faça upload de um arquivo `.txt`.
        2. Selecione as transformações desejadas.
        3. Clique em **Formatar**.
        - Limite de upload: **5 MB**.
        """)

    source = st.radio("Fonte do texto", ["Digitar/Colar", "Upload de arquivo .txt"], horizontal=True, key="fmt_source")

    text_in = ""
    if source == "Digitar/Colar":
        text_in = st.text_area("Cole seu texto aqui", height=200, key="fmt_input", placeholder="Digite ou cole o texto…")
    else:
        uploaded = st.file_uploader("Arquivo .txt", type=["txt"], key="fmt_upload")
        if uploaded:
            if uploaded.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                st.error(f"❌ Arquivo excede {MAX_FILE_SIZE_MB} MB.")
                return
            text_in = _decode(uploaded.read())
            st.text_area("Conteúdo carregado (prévia)", value=text_in[:1000], height=150, disabled=True, key="fmt_loaded")

    if not text_in.strip():
        st.info("Insira ou carregue texto para continuar.")
        return

    st.markdown("### ⚙️ Transformações")
    col1, col2 = st.columns(2)
    strip_lt    = col1.checkbox("Remover espaços no início/fim do texto",    value=True)
    strip_lines = col1.checkbox("Remover espaços em cada linha",             value=False)
    rm_blank    = col1.checkbox("Remover linhas em branco",                  value=False)
    collapse    = col2.checkbox("Colapsar múltiplos espaços em um único",    value=False)
    rm_accents  = col2.checkbox("Remover acentuação (normalizar ASCII)",     value=False)

    case_opt = st.selectbox(
        "Conversão de maiúsculas/minúsculas",
        ["Sem alteração", "MAIÚSCULAS", "minúsculas", "Título (Primeira Letra Maiúscula)", "Sentença (1ª letra de cada frase)"],
        key="fmt_case",
    )

    if st.button("✏️ Formatar", key="fmt_btn"):
        try:
            opts = {
                "strip_leading_trailing": strip_lt,
                "strip_line_spaces":      strip_lines,
                "remove_blank_lines":     rm_blank,
                "collapse_spaces":        collapse,
                "remove_accents":         rm_accents,
                "case":                   case_opt if case_opt != "Sem alteração" else None,
            }
            result = apply_transforms(text_in, opts)

            st.text_area("Resultado", value=result, height=250, key="fmt_output")
            st.caption(f"**Antes:** {len(text_in):,} chars · {text_in.count(chr(10)):,} linhas  →  "
                       f"**Depois:** {len(result):,} chars · {result.count(chr(10)):,} linhas")

            st.download_button(
                label="⬇️ Baixar texto formatado (.txt)",
                data=result.encode("utf-8"),
                file_name="texto_formatado.txt",
                mime="text/plain",
                key="fmt_download",
            )
            st.success("✅ Texto formatado com sucesso!")
        except Exception as e:
            st.error(f"❌ Falha ao formatar texto: {e}")
