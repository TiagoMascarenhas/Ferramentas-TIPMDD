"""
Módulo: Comparador de Arquivos
Categoria: 📊 Planilhas / Dados
"""

import io
import difflib
import streamlit as st
import pandas as pd

MODULE_NAME     = "Comparador de Arquivos"
MODULE_ICON     = "🔍"
MODULE_CATEGORY = "📊 Planilhas / Dados"
MODULE_DESC     = "Compara dois arquivos e exibe as diferenças entre eles."

MAX_FILE_SIZE_MB = 10


def _read_as_lines(f) -> list[str]:
    name = f.name.lower()
    f.seek(0)
    if name.endswith(".csv"):
        try:
            content = f.read().decode("utf-8")
        except UnicodeDecodeError:
            f.seek(0)
            content = f.read().decode("latin-1")
        return content.splitlines(keepends=True)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(f.read()))
        return df.to_csv(index=False).splitlines(keepends=True)
    elif name.endswith(".txt"):
        try:
            return f.read().decode("utf-8").splitlines(keepends=True)
        except UnicodeDecodeError:
            f.seek(0)
            return f.read().decode("latin-1").splitlines(keepends=True)
    else:
        raise ValueError(f"Formato não suportado: {f.name}")


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload do **Arquivo A** (original) e do **Arquivo B** (modificado).
        2. Clique em **Comparar** para visualizar as diferenças.
        - Suporta: CSV, Excel (`.xlsx`/`.xls`), TXT.
        - Linhas em **verde** foram adicionadas; em **vermelho**, removidas.
        - Limite: **10 MB por arquivo**.
        """)

    col1, col2 = st.columns(2)
    file_a = col1.file_uploader("📂 Arquivo A (original)", type=["csv", "xlsx", "xls", "txt"], key="diff_a")
    file_b = col2.file_uploader("📂 Arquivo B (modificado)", type=["csv", "xlsx", "xls", "txt"], key="diff_b")

    if not file_a or not file_b:
        st.info("Faça upload dos dois arquivos para comparar.")
        return

    for f in [file_a, file_b]:
        if f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.error(f"❌ `{f.name}` excede {MAX_FILE_SIZE_MB} MB.")
            return

    if st.button("🔍 Comparar", key="diff_btn"):
        try:
            lines_a = _read_as_lines(file_a)
            lines_b = _read_as_lines(file_b)

            diff = list(difflib.unified_diff(
                lines_a, lines_b,
                fromfile=file_a.name,
                tofile=file_b.name,
                lineterm="",
            ))

            if not diff:
                st.success("✅ Os arquivos são **idênticos**! Nenhuma diferença encontrada.")
                return

            # Contagens
            added   = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
            removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Linhas adicionadas", f"+{added}", delta=added, delta_color="normal")
            col_m2.metric("Linhas removidas",   f"-{removed}", delta=-removed, delta_color="inverse")
            col_m3.metric("Total de diferenças", added + removed)

            # Renderização colorida
            html_lines = ["<pre style='font-size:0.8rem;line-height:1.5;overflow-x:auto'>"]
            for line in diff:
                line_esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if line.startswith("+") and not line.startswith("+++"):
                    html_lines.append(f"<span style='background:#d4edda;color:#155724;display:block'>{line_esc}</span>")
                elif line.startswith("-") and not line.startswith("---"):
                    html_lines.append(f"<span style='background:#f8d7da;color:#721c24;display:block'>{line_esc}</span>")
                elif line.startswith("@@"):
                    html_lines.append(f"<span style='background:#cce5ff;color:#004085;display:block'>{line_esc}</span>")
                else:
                    html_lines.append(f"<span style='display:block'>{line_esc}</span>")
            html_lines.append("</pre>")
            st.markdown("".join(html_lines), unsafe_allow_html=True)

            diff_text = "".join(diff)
            st.download_button(
                label="⬇️ Baixar diff (.txt)",
                data=diff_text.encode("utf-8"),
                file_name="comparacao.txt",
                mime="text/plain",
                key="diff_download",
            )
        except Exception as e:
            st.error(f"❌ Falha ao comparar arquivos: {e}")
