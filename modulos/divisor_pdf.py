"""
Módulo: Divisor de PDFs
Categoria: 📄 PDFs
"""

import io
import streamlit as st
from pypdf import PdfWriter, PdfReader

MODULE_NAME     = "Divisor de PDFs"
MODULE_ICON     = "✂️"
MODULE_CATEGORY = "📄 PDFs"
MODULE_DESC     = "Extrai páginas específicas ou intervalos de um PDF."

MAX_FILE_SIZE_MB = 50


def _parse_page_range(expr: str, total: int) -> list[int]:
    """
    Converte expressão como '1,3,5-8,10' em lista de índices 0-based.
    Lança ValueError se a expressão for inválida.
    """
    pages = set()
    for part in expr.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            a, b = int(a.strip()), int(b.strip())
            if a < 1 or b > total or a > b:
                raise ValueError(f"Intervalo inválido: {part}")
            pages.update(range(a - 1, b))
        else:
            n = int(part)
            if n < 1 or n > total:
                raise ValueError(f"Página {n} fora do intervalo (1–{total})")
            pages.add(n - 1)
    return sorted(pages)


def render():
    with st.expander("ℹ️ Como usar", expanded=False):
        st.markdown("""
        1. Faça upload do PDF que deseja dividir.
        2. Informe as páginas desejadas (ex: `1,3,5-8`).
        3. Clique em **Extrair Páginas**.
        - Limite: **50 MB por arquivo**.
        """)

    uploaded = st.file_uploader(
        "Selecione o PDF",
        type=["pdf"],
        key="split_upload",
    )

    if not uploaded:
        st.info("Aguardando upload do PDF…")
        return

    if uploaded.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"❌ Arquivo excede o limite de {MAX_FILE_SIZE_MB} MB.")
        return

    try:
        reader = PdfReader(io.BytesIO(uploaded.read()))
        total_pages = len(reader.pages)
        uploaded.seek(0)
    except Exception as e:
        st.error(f"❌ Não foi possível ler o PDF: {e}")
        return

    st.info(f"📄 O PDF contém **{total_pages} página(s)**.")

    mode = st.radio(
        "Modo de extração",
        ["Páginas específicas", "Todas as páginas em arquivos separados"],
        horizontal=True,
        key="split_mode",
    )

    if mode == "Páginas específicas":
        expr = st.text_input(
            "Páginas desejadas (ex: `1,3,5-8`)",
            placeholder="1,3,5-8",
            key="split_expr",
        )

        if st.button("✂️ Extrair Páginas", key="split_btn"):
            if not expr.strip():
                st.warning("Informe pelo menos uma página.")
                return
            try:
                indices = _parse_page_range(expr, total_pages)
                writer  = PdfWriter()
                uploaded.seek(0)
                reader2 = PdfReader(io.BytesIO(uploaded.read()))
                for idx in indices:
                    writer.add_page(reader2.pages[idx])

                buf = io.BytesIO()
                writer.write(buf)
                buf.seek(0)

                st.download_button(
                    label=f"⬇️ Baixar PDF ({len(indices)} página(s))",
                    data=buf.getvalue(),
                    file_name="paginas_extraidas.pdf",
                    mime="application/pdf",
                    key="split_download",
                )
                st.success(f"✅ {len(indices)} página(s) extraída(s) com sucesso!")
            except ValueError as ve:
                st.error(f"❌ Erro na expressão de páginas: {ve}")
            except Exception as e:
                st.error(f"❌ Falha ao extrair páginas: {e}")

    else:
        if st.button("✂️ Gerar arquivo por página", key="split_all_btn"):
            try:
                import zipfile
                uploaded.seek(0)
                reader2 = PdfReader(io.BytesIO(uploaded.read()))

                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for i, page in enumerate(reader2.pages, 1):
                        w = PdfWriter()
                        w.add_page(page)
                        p_buf = io.BytesIO()
                        w.write(p_buf)
                        zf.writestr(f"pagina_{i:03d}.pdf", p_buf.getvalue())
                zip_buf.seek(0)

                st.download_button(
                    label=f"⬇️ Baixar ZIP com {total_pages} PDFs",
                    data=zip_buf.getvalue(),
                    file_name="paginas_separadas.zip",
                    mime="application/zip",
                    key="split_zip_download",
                )
                st.success(f"✅ {total_pages} arquivos gerados!")
            except Exception as e:
                st.error(f"❌ Falha ao dividir PDF: {e}")
