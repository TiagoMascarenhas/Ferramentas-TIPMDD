"""
Módulo: Gerador de Relatório de Diretório
Categoria: 🛠️ Utilitários
"""

import os
import io
import datetime
import zipfile
import streamlit as st
import pandas as pd

MODULE_NAME     = "Relatório de Diretório"
MODULE_ICON     = "📁"
MODULE_CATEGORY = "🛠️ Utilitários"
MODULE_DESC     = "Lista e analisa os arquivos de um conjunto de uploads, gerando relatório detalhado."

MAX_FILE_SIZE_MB = 100
MAX_FILES        = 200


def _human_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload de **qualquer conjunto de arquivos** de uma pasta.
        2. O módulo gera um relatório com nome, extensão, tamanho e data de upload.
        3. Baixe o relatório em Excel ou CSV.
        - Limite: **200 arquivos**, **100 MB por arquivo**.

        > 💡 **Dica:** No Windows, você pode selecionar múltiplos arquivos com `Ctrl+A` no diálogo de upload.
        """)

    uploaded = st.file_uploader(
        "Selecione os arquivos para inventariar",
        accept_multiple_files=True,
        key="dirreport_upload",
    )

    if not uploaded:
        st.info("Faça upload dos arquivos para gerar o relatório.")
        return

    valid = [f for f in uploaded[:MAX_FILES] if f.size <= MAX_FILE_SIZE_MB * 1024 * 1024]
    ignored = len(uploaded) - len(valid)
    if ignored:
        st.warning(f"⚠️ {ignored} arquivo(s) excederam {MAX_FILE_SIZE_MB} MB e foram ignorados.")

    st.success(f"✅ {len(valid)} arquivo(s) carregado(s).")

    output_fmt = st.radio("Formato do relatório", ["Excel (.xlsx)", "CSV (.csv)"], horizontal=True, key="dirreport_fmt")

    if st.button("📊 Gerar Relatório", key="dirreport_btn"):
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows = []
            ext_counter: dict[str, int] = {}

            for f in valid:
                ext = os.path.splitext(f.name)[1].lower() or "(sem extensão)"
                ext_counter[ext] = ext_counter.get(ext, 0) + 1
                rows.append({
                    "Nome do Arquivo":   f.name,
                    "Extensão":          ext,
                    "Tamanho (bytes)":   f.size,
                    "Tamanho Legível":   _human_size(f.size),
                    "Data do Relatório": now,
                })

            df = pd.DataFrame(rows).sort_values("Nome do Arquivo").reset_index(drop=True)
            df.index += 1  # 1-based

            # Métricas
            total_size = sum(r["Tamanho (bytes)"] for r in rows)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total de arquivos",  len(valid))
            c2.metric("Tamanho total",       _human_size(total_size))
            c3.metric("Tipos diferentes",    len(ext_counter))

            # Tabela resumo por extensão
            st.markdown("#### Resumo por tipo de arquivo")
            ext_df = (
                pd.DataFrame(list(ext_counter.items()), columns=["Extensão", "Qtd"])
                .sort_values("Qtd", ascending=False)
                .reset_index(drop=True)
            )
            st.dataframe(ext_df, use_container_width=False, hide_index=True)

            # Listagem completa
            st.markdown("#### Listagem completa")
            st.dataframe(df[["Nome do Arquivo", "Extensão", "Tamanho Legível"]], use_container_width=True)

            # Download
            buf = io.BytesIO()
            if output_fmt.startswith("Excel"):
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name="Inventário", index=True)
                    ext_df.to_excel(writer, sheet_name="Resumo por Tipo", index=False)
                fname = "relatorio_diretorio.xlsx"
                mime  = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            else:
                buf.write(df.to_csv(index=True).encode("utf-8"))
                fname = "relatorio_diretorio.csv"
                mime  = "text/csv"

            buf.seek(0)
            st.download_button(
                label=f"⬇️ Baixar {fname}",
                data=buf.getvalue(),
                file_name=fname,
                mime=mime,
                key="dirreport_download",
            )
            st.success(f"✅ Relatório gerado para {len(valid)} arquivo(s)!")
        except Exception as e:
            st.error(f"❌ Falha ao gerar relatório: {e}")
