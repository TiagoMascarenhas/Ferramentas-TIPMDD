"""
Hub de Produtividade da TI PMDD
app.py - Orquestrador principal.
"""

import streamlit as st
import importlib
import pkgutil
import modulos

st.set_page_config(
    page_title="Hub de Produtividade · TI PMDD",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root {
    --pmdd-navy:   #0d1b2a;
    --pmdd-blue:   #1e3a5f;
    --pmdd-accent: #2e86de;
    --pmdd-light:  #f0f4f8;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--pmdd-navy) 0%, var(--pmdd-blue) 100%);
}
[data-testid="stSidebar"] * { color: #e8edf2 !important; }

.hub-header {
    background: linear-gradient(135deg, var(--pmdd-navy), var(--pmdd-blue));
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.hub-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
.hub-header p  { margin: 0; font-size: 0.9rem; opacity: 0.75; }

.footer-bar {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: var(--pmdd-navy);
    color: #8fa8c8;
    text-align: center;
    font-size: 0.75rem;
    padding: 0.4rem;
    z-index: 9999;
    letter-spacing: 0.05em;
}

[data-testid="stExpander"] { border-left: 3px solid var(--pmdd-accent) !important; }

.stDownloadButton > button, .stButton > button {
    background: var(--pmdd-accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: background 0.2s;
}
.stDownloadButton > button:hover, .stButton > button:hover {
    background: #1a6fc4 !important;
}

.main .block-container { padding-bottom: 3.5rem !important; }
</style>
""", unsafe_allow_html=True)


def discover_modules() -> dict:
    # Varre a pasta modulos/ e importa tudo dinamicamente
    found = {}
    for _finder, name, _ispkg in pkgutil.iter_modules(modulos.__path__, modulos.__name__ + "."):
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "MODULE_NAME") and hasattr(mod, "render"):
                category = getattr(mod, "MODULE_CATEGORY", "🔧 Outros")
                icon     = getattr(mod, "MODULE_ICON", "🔧")
                label    = f"{icon} {mod.MODULE_NAME}"
                full_key = f"{category}||{label}"
                found[full_key] = mod
        except Exception as exc:
            st.sidebar.error(f"Erro ao carregar `{name}`: {exc}")
    return found


def build_sidebar(modules: dict):
    st.sidebar.markdown(
        "<div style='text-align:center;padding:0.5rem 0'>"
        "<span style='font-size:2rem'>🛡️</span><br>"
        "<strong style='font-size:1rem;letter-spacing:0.05em'>TI PMDD</strong><br>"
        "<small style='opacity:0.6'>Hub de Produtividade</small>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

    categories: dict = {}
    for key, mod in modules.items():
        cat, label = key.split("||", 1)
        categories.setdefault(cat, []).append((label, mod))

    if "_run" not in st.session_state:
        st.session_state["_run"] = 0

    if "active_module" not in st.session_state and categories:
        first_cat  = sorted(categories.keys())[0]
        first_item = sorted(categories[first_cat], key=lambda x: x[0])[0]
        st.session_state["active_module"] = first_item[0]

    selected_mod = None
    for cat in sorted(categories.keys()):
        st.sidebar.markdown(
            f"<p style='font-size:0.7rem;font-weight:700;letter-spacing:0.08em;"
            f"text-transform:uppercase;opacity:0.55;margin:0.8rem 0 0.2rem'>{cat}</p>",
            unsafe_allow_html=True,
        )
        for label, mod in sorted(categories[cat], key=lambda x: x[0]):
            if st.sidebar.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state["active_module"] = label
            if st.session_state.get("active_module") == label:
                selected_mod = mod

    if selected_mod is None and "active_module" in st.session_state:
        active_label = st.session_state["active_module"]
        for key, mod in modules.items():
            _cat, lbl = key.split("||", 1)
            if lbl == active_label:
                selected_mod = mod
                break

    st.sidebar.divider()
    st.sidebar.caption("v1.1.0 · 2026 · TI PMDD")
    return selected_mod


def render_header(mod=None):
    if mod:
        name = getattr(mod, "MODULE_NAME", "Ferramenta")
        icon = getattr(mod, "MODULE_ICON", "🛠️")
        desc = getattr(mod, "MODULE_DESC", "")
    else:
        name = "Bem-vindo ao Hub de Produtividade"
        icon = "🛡️"
        desc = "Selecione uma ferramenta na barra lateral."

    st.markdown(f"""
    <div class="hub-header">
        <div style="font-size:2.8rem;line-height:1">{icon}</div>
        <div>
            <h1>{name}</h1>
            <p>{desc}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown(
        '<div class="footer-bar">Desenvolvido pela TI PMDD — 2026</div>',
        unsafe_allow_html=True,
    )


def render_home(modules: dict):
    st.markdown("### 🗂️ Ferramentas disponíveis")
    st.markdown("Clique em qualquer item na **barra lateral** para acessar a ferramenta.")
    st.markdown("---")

    categories = {}
    for key, mod in modules.items():
        cat, label = key.split("||", 1)
        categories.setdefault(cat, []).append((label, mod))

    for cat in sorted(categories.keys()):
        st.markdown(f"#### {cat}")
        cols = st.columns(3)
        for i, (label, mod) in enumerate(sorted(categories[cat], key=lambda x: x[0])):
            with cols[i % 3]:
                desc = getattr(mod, "MODULE_DESC", "")
                st.info(f"**{label}**\n\n{desc}")
        st.markdown("")



@st.dialog("🔄 Nova operação")
def _dialog_nova_operacao():
    st.write("Deseja limpar todos os campos e começar uma nova operação?")
    col1, col2 = st.columns(2)
    if col1.button("✅ Sim, reiniciar", use_container_width=True, type="primary"):
        st.session_state["_run"] = st.session_state.get("_run", 0) + 1
        st.rerun()
    if col2.button("❌ Não, continuar", use_container_width=True):
        st.rerun()


def main():
    modules  = discover_modules()
    selected = build_sidebar(modules)

    render_header(selected)

    if selected:
        # Botão Nova Operação — abre modal centralizado
        col_btn, col_rest = st.columns([1, 5])
        with col_btn:
            if st.button("🔄 Nova operação", use_container_width=True, help="Reinicia a ferramenta atual"):
                _dialog_nova_operacao()

        try:
            selected.render()
        except Exception as exc:
            st.error(f"❌ Erro inesperado no módulo: {exc}")
            with st.expander("Detalhes técnicos do erro"):
                st.exception(exc)
    else:
        render_home(modules)

    render_footer()


if __name__ == "__main__":
    main()
