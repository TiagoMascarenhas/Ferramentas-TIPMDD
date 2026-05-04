"""
Módulo: Concatenador de Arquivos TXT
Categoria: 📝 Texto
"""

import io
import streamlit as st

MODULE_NAME     = "Concatenador de TXT"
MODULE_ICON     = "📋"
MODULE_CATEGORY = "📝 Texto"
MODULE_DESC     = "Une múltiplos arquivos de texto (.txt) em um único arquivo."

MAX_FILE_SIZE_MB = 5
MAX_FILES        = 50


def _decode(data: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload de dois ou mais arquivos `.txt`.
        2. Escolha o separador entre os arquivos.
        3. Clique em **Concatenar** e baixe o resultado.
        - Limite: **50 arquivos**, **5 MB por arquivo**.
        """)

    uploaded = st.file_uploader(
        "Selecione os arquivos TXT",
        type=["txt"],
        accept_multiple_files=True,
        key="concat_upload",
    )

    if not uploaded:
        st.info("Aguardando upload dos arquivos…")
        return

    valid = [f for f in uploaded[:MAX_FILES] if f.size <= MAX_FILE_SIZE_MB * 1024 * 1024]
    if len(valid) < 2:
        st.warning("Envie pelo menos **2 arquivos** para concatenar.")
        return

    sep_option = st.selectbox(
        "Separador entre arquivos",
        [
            "Nenhum (texto contínuo)",
            "Linha em branco",
            "Linha separadora (--- nome do arquivo ---)",
            "Página (múltiplas linhas em branco)",
        ],
        key="concat_sep",
    )

    if st.button("🔄 Concatenar", key="concat_btn"):
        try:
            parts = []
            for f in valid:
                text = _decode(f.read())
                if sep_option == "Nenhum (texto contínuo)":
                    parts.append(text)
                elif sep_option == "Linha em branco":
                    parts.append(text + "\n")
                elif sep_option == "Linha separadora (--- nome do arquivo ---)":
                    header = f"\n{'─'*50}\n{f.name}\n{'─'*50}\n"
                    parts.append(header + text)
                else:  # Página
                    parts.append(text + "\n\n\n")

            result = "".join(parts)

            st.text_area("Prévia (primeiros 2000 caracteres)", value=result[:2000], height=250, key="concat_preview")
            st.caption(f"Total: **{len(result):,} caracteres** · **{result.count(chr(10)):,} linhas**")

            st.download_button(
                label="⬇️ Baixar arquivo concatenado (.txt)",
                data=result.encode("utf-8"),
                file_name="concatenado.txt",
                mime="text/plain",
                key="concat_download",
            )
            st.success(f"✅ {len(valid)} arquivos concatenados com sucesso!")
        except Exception as e:
            st.error(f"❌ Falha ao concatenar arquivos: {e}")
