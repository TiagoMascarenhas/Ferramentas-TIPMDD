"""
Módulo: Conversor PDF → Texto
Categoria: 📄 PDFs
"""

import io
import streamlit as st
from pypdf import PdfReader

MODULE_NAME     = "PDF → Texto"
MODULE_ICON     = "📝"
MODULE_CATEGORY = "📄 PDFs"
MODULE_DESC     = "Extrai o texto de arquivos PDF para edição ou análise."

MAX_FILE_SIZE_MB = 30


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload de um PDF com texto selecionável.
        2. Clique em **Extrair Texto**.
        3. Visualize o conteúdo e baixe como `.txt`.
        - ⚠️ PDFs escaneados (imagem) não possuem texto extraível.
        - Limite: **30 MB por arquivo**.
        """)

    uploaded = st.file_uploader(
        "Selecione o PDF",
        type=["pdf"],
        key="pdf2txt_upload",
    )

    if not uploaded:
        st.info("Aguardando upload do PDF…")
        return

    if uploaded.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"❌ Arquivo excede o limite de {MAX_FILE_SIZE_MB} MB.")
        return

    if st.button("🔄 Extrair Texto", key="pdf2txt_btn"):
        try:
            reader = PdfReader(io.BytesIO(uploaded.read()))
            lines  = []
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                lines.append(f"{'='*50}\nPÁGINA {i}\n{'='*50}\n{text}\n")

            full_text = "\n".join(lines).strip()

            if not full_text:
                st.warning("⚠️ Nenhum texto extraível encontrado. O PDF pode ser baseado em imagem.")
                return

            st.text_area(
                f"Texto extraído ({len(reader.pages)} páginas)",
                value=full_text,
                height=400,
                key="pdf2txt_preview",
            )

            st.download_button(
                label="⬇️ Baixar como .txt",
                data=full_text.encode("utf-8"),
                file_name="texto_extraido.txt",
                mime="text/plain",
                key="pdf2txt_download",
            )
            st.success(f"✅ Texto extraído de {len(reader.pages)} página(s).")
        except Exception as e:
            st.error(f"❌ Falha ao extrair texto: {e}")
