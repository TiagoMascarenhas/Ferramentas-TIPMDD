"""
Módulo: Consolidador de Planilhas
Categoria: 📊 Planilhas / Dados
"""

import io
import streamlit as st
import pandas as pd

MODULE_NAME     = "Consolidador de Planilhas"
MODULE_ICON     = "🗂️"
MODULE_CATEGORY = "📊 Planilhas / Dados"
MODULE_DESC     = "Combina múltiplos arquivos Excel/CSV em uma única planilha."

MAX_FILE_SIZE_MB = 20
MAX_FILES        = 20


def _read_file(f) -> pd.DataFrame:
    name = f.name.lower()
    f.seek(0)
    if name.endswith(".csv"):
        try:
            return pd.read_csv(f, encoding="utf-8")
        except UnicodeDecodeError:
            f.seek(0)
            return pd.read_csv(f, encoding="latin-1")
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(f.read()))
    else:
        raise ValueError(f"Formato não suportado: {f.name}")


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload de arquivos Excel (`.xlsx`, `.xls`) ou CSV.
        2. Os dados serão empilhados verticalmente (todos os arquivos precisam ter colunas compatíveis).
        3. Escolha o formato de saída e clique em **Consolidar**.
        - Limite: **20 arquivos**, **20 MB por arquivo**.
        """)

    uploaded = st.file_uploader(
        "Selecione os arquivos",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key="consolidar_upload",
    )

    if not uploaded:
        st.info("Aguardando upload…")
        return

    valid = [f for f in uploaded[:MAX_FILES] if f.size <= MAX_FILE_SIZE_MB * 1024 * 1024]
    ignored = len(uploaded) - len(valid)
    if ignored:
        st.warning(f"⚠️ {ignored} arquivo(s) excederam {MAX_FILE_SIZE_MB} MB e foram ignorados.")

    if len(valid) < 2:
        st.warning("Envie pelo menos **2 arquivos** para consolidar.")
        return

    add_source = st.checkbox("Adicionar coluna com nome do arquivo de origem", value=True)
    output_fmt = st.radio("Formato de saída", ["Excel (.xlsx)", "CSV (.csv)"], horizontal=True, key="consolidar_fmt")

    if st.button("🔄 Consolidar", key="consolidar_btn"):
        try:
            frames = []
            errors = []
            for f in valid:
                try:
                    df = _read_file(f)
                    if add_source:
                        df.insert(0, "_origem", f.name)
                    frames.append(df)
                except Exception as e:
                    errors.append(f"`{f.name}`: {e}")

            if errors:
                for err in errors:
                    st.warning(f"⚠️ {err}")

            if not frames:
                st.error("❌ Nenhum arquivo pôde ser lido.")
                return

            merged = pd.concat(frames, ignore_index=True)

            buf = io.BytesIO()
            if output_fmt.startswith("Excel"):
                merged.to_excel(buf, index=False, engine="openpyxl")
                fname = "consolidado.xlsx"
                mime  = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                buf.write(merged.to_csv(index=False).encode("utf-8"))
                fname = "consolidado.csv"
                mime  = "text/csv"

            buf.seek(0)
            st.dataframe(merged.head(50), use_container_width=True)
            st.caption(f"Prévia das primeiras 50 linhas. Total: **{len(merged):,} linhas** × **{len(merged.columns)} colunas**.")

            st.download_button(
                label=f"⬇️ Baixar {fname}",
                data=buf.getvalue(),
                file_name=fname,
                mime=mime,
                key="consolidar_download",
            )
            st.success(f"✅ {len(frames)} arquivo(s) consolidados em {len(merged):,} linhas!")
        except Exception as e:
            st.error(f"❌ Falha ao consolidar: {e}")
