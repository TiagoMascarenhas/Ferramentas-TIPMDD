"""
Módulo: Redimensionador de Imagens
Categoria: 🖼️ Imagens
"""

import io
import streamlit as st
from PIL import Image

MODULE_NAME     = "Redimensionador de Imagens"
MODULE_ICON     = "📐"
MODULE_CATEGORY = "🖼️ Imagens"
MODULE_DESC     = "Redimensiona imagens JPG/PNG por dimensões ou percentual."

MAX_FILE_SIZE_MB = 15


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload de uma imagem (JPG ou PNG).
        2. Escolha o modo de redimensionamento.
        3. Informe os valores desejados e clique em **Redimensionar**.
        - Limite: **15 MB por imagem**.
        """)

    uploaded = st.file_uploader(
        "Selecione a imagem",
        type=["jpg", "jpeg", "png"],
        key="resize_upload",
    )

    if not uploaded:
        st.info("Aguardando upload…")
        return

    if uploaded.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"❌ Arquivo excede o limite de {MAX_FILE_SIZE_MB} MB.")
        return

    img = Image.open(uploaded)
    w_orig, h_orig = img.size
    fmt = img.format or "PNG"
    st.image(img, caption=f"Original: {w_orig}×{h_orig}px", use_container_width=False, width=300)

    mode = st.radio("Modo de redimensionamento", ["Dimensões fixas (px)", "Percentual (%)"], horizontal=True)

    col1, col2 = st.columns(2)
    if mode == "Dimensões fixas (px)":
        new_w = col1.number_input("Largura (px)", min_value=1, max_value=10000, value=w_orig)
        new_h = col2.number_input("Altura (px)", min_value=1, max_value=10000, value=h_orig)
        manter_proporcao = st.checkbox("Manter proporção (usa a largura como base)", value=True)
        if manter_proporcao:
            ratio = new_w / w_orig
            new_h = int(h_orig * ratio)
            st.caption(f"Altura calculada automaticamente: **{new_h} px**")
    else:
        pct = col1.slider("Percentual (%)", min_value=1, max_value=500, value=100)
        new_w = int(w_orig * pct / 100)
        new_h = int(h_orig * pct / 100)
        st.caption(f"Novo tamanho: **{new_w}×{new_h} px**")

    output_fmt = st.selectbox("Formato de saída", ["PNG", "JPEG"], key="resize_fmt")
    quality    = st.slider("Qualidade JPEG (%)", 10, 100, 90) if output_fmt == "JPEG" else 95

    if st.button("🔄 Redimensionar", key="resize_btn"):
        try:
            resized = img.resize((new_w, new_h), Image.LANCZOS)
            buf = io.BytesIO()
            save_fmt = "JPEG" if output_fmt == "JPEG" else "PNG"
            if save_fmt == "JPEG":
                resized = resized.convert("RGB")
                resized.save(buf, format=save_fmt, quality=quality)
            else:
                resized.save(buf, format=save_fmt)
            buf.seek(0)

            ext = "jpg" if output_fmt == "JPEG" else "png"
            st.download_button(
                label="⬇️ Baixar imagem redimensionada",
                data=buf.getvalue(),
                file_name=f"redimensionado_{new_w}x{new_h}.{ext}",
                mime=f"image/{ext}",
                key="resize_download",
            )
            st.success(f"✅ Imagem redimensionada para {new_w}×{new_h} px!")
        except Exception as e:
            st.error(f"❌ Falha ao redimensionar: {e}")
