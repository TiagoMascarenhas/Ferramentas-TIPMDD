"""
Módulo: Conversor de Imagens para PDF
Categoria: 🖼️ Imagens
"""

import io
import tempfile
import streamlit as st
from PIL import Image

MODULE_NAME     = "Imagens → PDF"
MODULE_ICON     = "🖼️"
MODULE_CATEGORY = "🖼️ Imagens"
MODULE_DESC     = "Converte imagens JPG/PNG em um único arquivo PDF."

MAX_FILE_SIZE_MB = 10
MAX_FILES        = 20


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload de uma ou mais imagens (JPG ou PNG).
        2. Ordene-as arrastando se necessário (a ordem de upload é mantida).
        3. Clique em **Gerar PDF** para baixar o resultado.
        - Limite: **20 imagens**, **10 MB por imagem**.
        """)

    uploaded = st.file_uploader(
        "Selecione as imagens",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="img2pdf_upload",
    )

    if not uploaded:
        st.info("Aguardando upload de imagens…")
        return

    # Validar tamanho
    valid_files = []
    for f in uploaded[:MAX_FILES]:
        if f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.warning(f"⚠️ `{f.name}` excede {MAX_FILE_SIZE_MB} MB e foi ignorado.")
        else:
            valid_files.append(f)

    st.success(f"✅ {len(valid_files)} imagem(ns) carregada(s).")

    # Preview
    cols = st.columns(min(len(valid_files), 5))
    for i, f in enumerate(valid_files[:5]):
        cols[i % 5].image(f, caption=f.name, use_container_width=True)
    if len(valid_files) > 5:
        st.caption(f"… e mais {len(valid_files) - 5} imagem(ns).")

    if st.button("🔄 Gerar PDF", key="img2pdf_btn"):
        try:
            images = []
            for f in valid_files:
                img = Image.open(f).convert("RGB")
                images.append(img)

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                if len(images) == 1:
                    images[0].save(tmp.name, "PDF")
                else:
                    images[0].save(tmp.name, "PDF", save_all=True, append_images=images[1:])

            with open(tmp.name, "rb") as out:
                pdf_bytes = out.read()

            st.download_button(
                label="⬇️ Baixar PDF gerado",
                data=pdf_bytes,
                file_name="imagens_convertidas.pdf",
                mime="application/pdf",
                key="img2pdf_download",
            )
            st.success("PDF gerado com sucesso!")
        except Exception as e:
            st.error(f"❌ Falha ao gerar PDF: {e}")
