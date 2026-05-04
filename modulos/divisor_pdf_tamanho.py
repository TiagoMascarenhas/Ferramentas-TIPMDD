MODULE_NAME     = "Divisor por Tamanho"
MODULE_ICON     = "⚖️"
MODULE_CATEGORY = "📄 PDFs"
MODULE_DESC     = "Divide um PDF em partes de até 4,6 MB — ideal para envio em portais do governo."


def render():
    import io
    import zipfile
    import streamlit as st
    from pypdf import PdfReader, PdfWriter

    # ── Constantes ────────────────────────────────────────────────────────────
    LIMITE_PADRAO_MB = 4.6
    LIMITE_PADRAO_BYTES = int(LIMITE_PADRAO_MB * 1024 * 1024)

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:#1e3a5f;padding:1.2rem 1.5rem;border-radius:10px;margin-bottom:1.2rem">
            <h3 style="color:#fff;margin:0">⚖️ Divisor de PDF por Tamanho</h3>
            <p style="color:#a8c4e0;margin:0.3rem 0 0">
                Divide automaticamente um PDF em partes de até <b>4,6 MB</b>,
                respeitando os limites de portais governamentais.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Upload ─────────────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        "Selecione o arquivo PDF",
        type=["pdf"],
        help="O arquivo será dividido em lotes de páginas que caibam dentro do limite.",
    )

    # ── Configurações ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        limite_mb = st.number_input(
            "Limite por parte (MB)",
            min_value=0.5,
            max_value=49.0,
            value=LIMITE_PADRAO_MB,
            step=0.1,
            format="%.1f",
            help="Padrão: 4,6 MB (margem de segurança para sites com limite de 5 MB).",
        )
    with col2:
        nome_base = st.text_input(
            "Nome base dos arquivos gerados",
            value="parte",
            help='Ex.: "parte" → parte_01.pdf, parte_02.pdf …',
        )

    limite_bytes = int(limite_mb * 1024 * 1024)

    # ── Processamento ──────────────────────────────────────────────────────────
    if uploaded and st.button("✂️ Dividir PDF", type="primary", use_container_width=True):

        dados_originais = uploaded.read()
        tamanho_original_mb = len(dados_originais) / (1024 * 1024)

        if len(dados_originais) <= limite_bytes:
            st.info(
                f"✅ O arquivo já tem {tamanho_original_mb:.2f} MB — menor ou igual ao limite "
                f"de {limite_mb:.1f} MB. Nenhuma divisão necessária."
            )
            st.download_button(
                "⬇️ Baixar arquivo original",
                data=dados_originais,
                file_name=uploaded.name,
                mime="application/pdf",
            )
            return

        reader = PdfReader(io.BytesIO(dados_originais))
        total_paginas = len(reader.pages)

        st.info(
            f"📄 **{total_paginas} páginas** · {tamanho_original_mb:.2f} MB  →  "
            f"dividindo em partes de até {limite_mb:.1f} MB…"
        )

        partes: list[bytes] = []          # bytes de cada parte gerada
        writer = PdfWriter()
        buf_atual = io.BytesIO()

        def _fechar_parte() -> bytes:
            """Serializa o writer atual e retorna os bytes."""
            b = io.BytesIO()
            writer.write(b)
            return b.getvalue()

        progresso = st.progress(0, text="Processando páginas…")

        for idx, page in enumerate(reader.pages):
            writer.add_page(page)

            # Mede o tamanho estimado da parte atual
            tamanho_atual = len(_fechar_parte())

            if tamanho_atual > limite_bytes:
                # A página que acabou de ser adicionada estourou o limite.
                # Salva a parte SEM essa página e começa nova parte com ela.
                writer_sem_ultima = PdfWriter()
                for p in list(writer.pages)[:-1]:          # todas exceto a última
                    writer_sem_ultima.add_page(p)

                buf = io.BytesIO()
                writer_sem_ultima.write(buf)
                partes.append(buf.getvalue())

                # Nova parte começa com a página que estourou
                writer = PdfWriter()
                writer.add_page(page)

            progresso.progress((idx + 1) / total_paginas, text=f"Página {idx + 1}/{total_paginas}")

        # Fecha a última parte (pode ter sobrado páginas)
        if len(writer.pages) > 0:
            buf = io.BytesIO()
            writer.write(buf)
            partes.append(buf.getvalue())

        progresso.empty()

        # ── Resultado ─────────────────────────────────────────────────────────
        total_partes = len(partes)
        st.success(f"✅ PDF dividido em **{total_partes} parte(s)**.")

        # Tabela-resumo
        resumo_cols = st.columns([3, 2, 2])
        resumo_cols[0].markdown("**Arquivo**")
        resumo_cols[1].markdown("**Tamanho**")
        resumo_cols[2].markdown("**Páginas**")

        pagina_acumulada = 0
        for i, parte_bytes in enumerate(partes, start=1):
            # Conta páginas dessa parte
            r_tmp = PdfReader(io.BytesIO(parte_bytes))
            npag = len(r_tmp.pages)
            pg_ini = pagina_acumulada + 1
            pg_fim = pagina_acumulada + npag
            pagina_acumulada += npag

            nome_arquivo = f"{nome_base}_{i:02d}.pdf"
            tamanho_parte_mb = len(parte_bytes) / (1024 * 1024)
            alerta = " ⚠️" if len(parte_bytes) > limite_bytes else ""

            c0, c1, c2 = st.columns([3, 2, 2])
            c0.write(f"📄 {nome_arquivo}{alerta}")
            c1.write(f"{tamanho_parte_mb:.2f} MB")
            c2.write(f"p. {pg_ini}–{pg_fim} ({npag} págs.)")

        st.divider()

        # ── Download individual ou ZIP ─────────────────────────────────────────
        if total_partes == 1:
            st.download_button(
                label="⬇️ Baixar parte única",
                data=partes[0],
                file_name=f"{nome_base}_01.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            # Gera ZIP com todas as partes
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, parte_bytes in enumerate(partes, start=1):
                    zf.writestr(f"{nome_base}_{i:02d}.pdf", parte_bytes)
            zip_buf.seek(0)

            st.download_button(
                label=f"⬇️ Baixar todas as {total_partes} partes (.zip)",
                data=zip_buf.getvalue(),
                file_name=f"{nome_base}_partes.zip",
                mime="application/zip",
                use_container_width=True,
            )

            st.caption(
                "💡 Dica: o arquivo ZIP contém todos os PDFs prontos para envio individual."
            )

        # Aviso sobre páginas muito grandes
        paginas_grandes = [
            i + 1
            for i, parte_bytes in enumerate(partes)
            if len(parte_bytes) > limite_bytes
        ]
        if paginas_grandes:
            st.warning(
                f"⚠️ As partes {paginas_grandes} ainda excedem o limite porque contêm páginas "
                "individuais maiores que o limite configurado (ex.: imagens em alta resolução). "
                "Considere otimizar/comprimir o PDF original antes de dividir."
            )
