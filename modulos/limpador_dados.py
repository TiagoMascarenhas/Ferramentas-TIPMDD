"""
Módulo: Limpador de Dados
Categoria: 📊 Planilhas / Dados
"""

import io
import streamlit as st
import pandas as pd

MODULE_NAME     = "Limpador de Dados"
MODULE_ICON     = "🧹"
MODULE_CATEGORY = "📊 Planilhas / Dados"
MODULE_DESC     = "Remove linhas vazias, duplicatas e faz limpeza básica em planilhas."

MAX_FILE_SIZE_MB = 20


def _read_file(f) -> pd.DataFrame:
    name = f.name.lower()
    f.seek(0)
    if name.endswith(".csv"):
        try:
            return pd.read_csv(f, encoding="utf-8")
        except UnicodeDecodeError:
            f.seek(0)
            return pd.read_csv(f, encoding="latin-1")
    else:
        return pd.read_excel(io.BytesIO(f.read()))


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload de um arquivo Excel ou CSV.
        2. Selecione as operações de limpeza desejadas.
        3. Clique em **Limpar Dados** e baixe o resultado.
        - Limite: **20 MB por arquivo**.
        """)

    uploaded = st.file_uploader(
        "Selecione o arquivo",
        type=["xlsx", "xls", "csv"],
        key="clean_upload",
    )

    if not uploaded:
        st.info("Aguardando upload…")
        return

    if uploaded.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"❌ Arquivo excede {MAX_FILE_SIZE_MB} MB.")
        return

    try:
        df_orig = _read_file(uploaded)
    except Exception as e:
        st.error(f"❌ Não foi possível ler o arquivo: {e}")
        return

    st.info(f"📊 Arquivo carregado: **{len(df_orig):,} linhas** × **{len(df_orig.columns)} colunas**")
    st.dataframe(df_orig.head(10), use_container_width=True)

    st.markdown("### ⚙️ Operações de limpeza")
    op_empty_rows  = st.checkbox("Remover linhas completamente vazias", value=True)
    op_empty_cols  = st.checkbox("Remover colunas completamente vazias", value=True)
    op_duplicates  = st.checkbox("Remover linhas duplicadas", value=True)
    op_strip       = st.checkbox("Remover espaços em branco nas células de texto", value=True)
    op_strip_cols  = st.checkbox("Remover espaços nos nomes das colunas", value=True)
    op_lower_cols  = st.checkbox("Converter nomes de colunas para minúsculas", value=False)

    output_fmt = st.radio("Formato de saída", ["Excel (.xlsx)", "CSV (.csv)"], horizontal=True, key="clean_fmt")

    if st.button("🧹 Limpar Dados", key="clean_btn"):
        try:
            df = df_orig.copy()
            log = []

            if op_strip_cols:
                df.columns = [str(c).strip() for c in df.columns]
                log.append("✅ Espaços nos nomes das colunas removidos.")

            if op_lower_cols:
                df.columns = [str(c).lower() for c in df.columns]
                log.append("✅ Nomes de colunas convertidos para minúsculas.")

            if op_empty_cols:
                before = len(df.columns)
                df.dropna(axis=1, how="all", inplace=True)
                removed = before - len(df.columns)
                log.append(f"✅ {removed} coluna(s) vazia(s) removida(s).")

            if op_empty_rows:
                before = len(df)
                df.dropna(how="all", inplace=True)
                log.append(f"✅ {before - len(df)} linha(s) completamente vazia(s) removida(s).")

            if op_duplicates:
                before = len(df)
                df.drop_duplicates(inplace=True)
                log.append(f"✅ {before - len(df)} linha(s) duplicada(s) removida(s).")

            if op_strip:
                for col in df.select_dtypes(include="object").columns:
                    df[col] = df[col].str.strip()
                log.append("✅ Espaços nas células de texto removidos.")

            for msg in log:
                st.markdown(msg)

            st.info(f"📊 Resultado: **{len(df):,} linhas** × **{len(df.columns)} colunas**")
            st.dataframe(df.head(20), use_container_width=True)

            buf = io.BytesIO()
            if output_fmt.startswith("Excel"):
                df.to_excel(buf, index=False, engine="openpyxl")
                fname = "dados_limpos.xlsx"
                mime  = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                buf.write(df.to_csv(index=False).encode("utf-8"))
                fname = "dados_limpos.csv"
                mime  = "text/csv"

            buf.seek(0)
            st.download_button(
                label=f"⬇️ Baixar {fname}",
                data=buf.getvalue(),
                file_name=fname,
                mime=mime,
                key="clean_download",
            )
        except Exception as e:
            st.error(f"❌ Falha ao limpar dados: {e}")
