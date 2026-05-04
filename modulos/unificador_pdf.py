"""
Módulo: Unificador de PDFs
Categoria: 📄 PDFs
"""

import io
import tempfile
import streamlit as st
from pypdf import PdfWriter, PdfReader

MODULE_NAME     = "Unificador de PDFs"
MODULE_ICON     = "📎"
MODULE_CATEGORY = "📄 PDFs"
MODULE_DESC     = "Combina múltiplos arquivos PDF em um único documento."

MAX_FILE_SIZE_MB = 30
MAX_FILES        = 30


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload de 2 ou mais PDFs.
        2. A ordem de mesclagem segue a ordem do upload.
        3. Clique em **Unificar PDFs** para gerar o arquivo final.
        - Limite: **30 arquivos**, **30 MB por arquivo**.
        """)

    uploaded = st.file_uploader(
        "Selecione os PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_upload",
    )

    if not uploaded:
        st.info("Aguardando upload de PDFs…")
        return

    valid = []
    for f in uploaded[:MAX_FILES]:
        if f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.warning(f"⚠️ `{f.name}` excede {MAX_FILE_SIZE_MB} MB e foi ignorado.")
        else:
            valid.append(f)

    if len(valid) < 2:
        st.warning("Envie pelo menos **2 PDFs** para unificar.")
        return

    st.markdown("**Ordem de mesclagem:**")
    for i, f in enumerate(valid, 1):
        try:
            reader = PdfReader(io.BytesIO(f.read()))
            n_pages = len(reader.pages)
            f.seek(0)
            st.markdown(f"`{i}.` {f.name} — **{n_pages} página(s)**")
        except Exception:
            st.markdown(f"`{i}.` {f.name}")
            f.seek(0)

    if st.button("🔄 Unificar PDFs", key="merge_btn"):
        try:
            writer = PdfWriter()
            for f in valid:
                f.seek(0)
                reader = PdfReader(io.BytesIO(f.read()))
                for page in reader.pages:
                    writer.add_page(page)

            buf = io.BytesIO()
            writer.write(buf)
            buf.seek(0)

            st.download_button(
                label="⬇️ Baixar PDF unificado",
                data=buf.getvalue(),
                file_name="unificado.pdf",
                mime="application/pdf",
                key="merge_download",
            )
            total = sum(1 for _ in writer.pages)
            st.success(f"✅ PDF gerado com {total} página(s) no total!")
        except Exception as e:
            st.error(f"❌ Falha ao unificar PDFs: {e}")
