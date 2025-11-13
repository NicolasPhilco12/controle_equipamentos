import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =====================
# Configurações iniciais
# =====================
st.set_page_config(page_title="Controle de Equipamentos", layout="centered")

# --- SENHA DO ADMIN ---
# !!! IMPORTANTE: Mude esta senha para algo seguro !!!
ADMIN_PASSWORD = "admin123"

# Caminhos dos arquivos de dados
ESTOQUE_FILE = "estoque.csv"
SOLICITACOES_FILE = "solicitacoes.csv"

# Função auxiliar: carrega ou cria arquivos CSV
def load_data(file, columns):
    """Carrega um CSV ou cria um novo se não existir."""
    if os.path.exists(file):
        try:
            return pd.read_csv(file)
        except pd.errors.EmptyDataError:
            # Se o arquivo estiver vazio, retorna um DataFrame vazio com colunas
            return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df

# =================================
# Início do Aplicativo (Sempre aberto)
# =================================

# Carrega os dados
estoque_df = load_data(ESTOQUE_FILE, ["Item", "Quantidade"])
solicitacoes_df = load_data(
    SOLICITACOES_FILE,
    [
        "Data", "Tipo", "Item", "Quantidade", "Colaborador", "Matrícula",
        "Marca", "Patrimônio", "Backup", "Solicitante", "Status", "Prioridade"
    ]
)

# =====================
# Lógica de exibição
# =====================

# Inicializa o session state para autenticação de admin
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

st.sidebar.title("Navegação")
# Define as opções de navegação - Painel de Admin sempre visível
nav_options = ["Formulários", "Painel de Admin"]
aba = st.sidebar.radio("Menu", nav_options)


if aba == "Formulários":
    st.title("📦 Solicitação e Recolhimento de Equipamentos")

    # Removido: col1, col2 = st.columns(2)
    # Trocamos o layout de colunas por Abas para uma UI mais limpa
    
    tab_solicitar, tab_chamado, tab_recolher = st.tabs([
        "📦 Solicitar Equipamento", 
        "🎫 Abrir Chamado", 
        "♻️ Recolher Item"
    ])

    # -------------------------
    # Aba 1: Solicitação
    # -------------------------
    with tab_solicitar:
        # Removido: st.header("Solicitação de Equipamento / Chamado")
        # Removido: tipo = st.selectbox(...)
        # Removido: if tipo == "Solicitar Equipamento":
        
        st.subheader("Formulário de Solicitação")
        
        nome_solicitante = st.text_input("Seu nome completo*", key="sol_nome")
        st.divider()
        
        equipamentos = ["Notebook", "Monitor", "Teclado", "Mouse", "Fone", "Outro"]
        selecionados = st.multiselect("Selecione os equipamentos", equipamentos)

        outros_textos = ""
        if "Outro" in selecionados:
            outros_textos = st.text_input("Descreva o equipamento adicional:")

        quantidade = st.number_input("Quantidade total", min_value=1, step=1)

        if st.button("Enviar Solicitação"):
        # --- VALIDAÇÃO ---
            if not nome_solicitante:
                st.error("❌ O campo 'Seu nome completo' é obrigatório.")
            elif not selecionados:
                st.error("❌ Você deve selecionar pelo menos um equipamento.")
            else:
                nova = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Tipo": "Solicitação",
                    "Item": ", ".join(selecionados) + (f" ({outros_textos})" if outros_textos else ""),
                    "Quantidade": quantidade,
                    "Colaborador": "",
                    "Matrícula": "",
                    "Marca": "",
                    "Patrimônio": "",
                    "Backup": "",
                    "Solicitante": nome_solicitante, # Salva o nome
                    "Status": "Em análise",
                    "Prioridade": "Média"
                }
                # Correção: Usando pd.concat em vez do obsoleto _append
                nova_df = pd.DataFrame([nova])
                solicitacoes_df = pd.concat([solicitacoes_df, nova_df], ignore_index=True)
                
                solicitacoes_df.to_csv(SOLICITACOES_FILE, index=False)
                st.success("✅ Solicitação enviada com sucesso!")
                st.rerun() # Atualiza a UI

    # -------------------------
    # Aba 2: Abrir Chamado
    # -------------------------
    with tab_chamado:
        # Removido: elif tipo == "Abrir Chamado":
        st.subheader("📋 Dados do Chamado")
        
        nome_solicitante_ch = st.text_input("Seu nome (solicitante)*", key="ch_nome")
        st.divider()

        patrimonio = st.text_input("Patrimônio do Notebook*")
        marca = st.selectbox("Marca do Notebook", ["Philco", "HP", "Dell", "Lenovo"])
        nome_colab = st.text_input("Nome do colaborador que usa o notebook*")
        matricula = st.text_input("Matrícula do colaborador")
        backup = st.radio("Precisa de backup?", ["Sim", "Não"], horizontal=True)

        if st.button("Enviar Chamado"):
        # --- VALIDAÇÃO ---
            if not patrimonio or not nome_colab or not nome_solicitante_ch:
                st.error("❌ Os campos 'Seu nome', 'Patrimônio do Notebook' e 'Nome do colaborador' são obrigatórios.")
            else:
                novo = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Tipo": "Chamado",
                    "Item": "Notebook",
                    "Quantidade": 1,
                    "Colaborador": nome_colab,
                    "Matrícula": matricula,
                    "Marca": marca,
                    "Patrimônio": patrimonio,
                    "Backup": backup,
                    "Solicitante": nome_solicitante_ch, # Salva o nome
                    "Status": "Em análise",
                    "Prioridade": "Média"
                }
                # Correção: Usando pd.concat
                novo_df = pd.DataFrame([novo])
                solicitacoes_df = pd.concat([solicitacoes_df, novo_df], ignore_index=True)
                
                solicitacoes_df.to_csv(SOLICITACOES_FILE, index=False)
                st.success("📨 Chamado registrado com sucesso!")
                st.rerun()

    # -------------------------
    # Lado 2: Recolhimento (Agora Aba 3)
    # -------------------------
    with tab_recolher:
        # Removido: st.header("♻️ Solicitação de Recolhimento")
        st.subheader("Formulário de Recolhimento")

        nome_solicitante_rec = st.text_input("Seu nome (quem solicita o recolhimento)*", key="rec_nome")
        patrimonio_rec = st.text_input("Patrimônio do(s) item(ns) a recolher*", key="rec_pat", help="Se for mais de um, separe por vírgula.")
        st.divider()

        recolhimentos = ["Fone", "Teclado", "Mouse", "Computador", "Monitor", "Outro"]
        selecionados_rec = st.multiselect("Selecione o que será recolhido", recolhimentos)

        outros_rec = ""
        if "Outro" in selecionados_rec:
            outros_rec = st.text_input("Descreva o item adicional:")

        if st.button("Enviar Recolhimento"):
            # --- VALIDAÇÃO ---
            if not nome_solicitante_rec or not patrimonio_rec:
                st.error("❌ Os campos 'Seu nome' e 'Patrimônio' são obrigatórios.")
            elif not selecionados_rec:
                st.error("❌ Você deve selecionar pelo menos um item para recolher.")
            else:
                nova = {
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Tipo": "Recolhimento",
                    "Item": ", ".join(selecionados_rec) + (f" ({outros_rec})" if outros_rec else ""),
                    "Quantidade": len(selecionados_rec),
                    "Colaborador": "", # Pode ser preenchido pelo admin depois
                    "Matrícula": "",
                    "Marca": "",
                    "Patrimônio": patrimonio_rec, # Salva o patrimônio
                    "Backup": "",
                    "Solicitante": nome_solicitante_rec, # Salva o nome
                    "Status": "Em análise",
                    "Prioridade": "Baixa"
                }
                # Correção: Usando pd.concat
                nova_df = pd.DataFrame([nova])
                solicitacoes_df = pd.concat([solicitacoes_df, nova_df], ignore_index=True)
                
                solicitacoes_df.to_csv(SOLICITACOES_FILE, index=False)
                st.success("♻️ Solicitação de recolhimento enviada com sucesso!")
                st.rerun()

# =====================
# Painel do Administrador
# =====================
elif aba == "Painel de Admin":

    # Se já estiver autenticado, mostra o painel
    if st.session_state.admin_authenticated:
        st.title("🧰 Painel de Controle do Administrador")

        if st.sidebar.button("Logout Admin"):
            st.session_state.admin_authenticated = False
            st.rerun()

        aba_admin = st.tabs(["📋 Solicitações", "📦 Estoque"])
        
        with aba_admin[0]:
            st.subheader("Gerenciar Solicitações")
            
            # Filtros
            st.markdown("### Filtros")
            
            # Define opções de filtro mesmo se o dataframe estiver vazio
            status_options = solicitacoes_df["Status"].unique() if not solicitacoes_df.empty else ["Em análise"]
            tipo_options = solicitacoes_df["Tipo"].unique() if not solicitacoes_df.empty else ["Solicitação"]

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                status_filtro = st.multiselect(
                    "Filtrar por Status",
                    options=status_options,
                    default=status_options
                )
            with col_f2:
                tipo_filtro = st.multiselect(
                    "Filtrar por Tipo",
                    options=tipo_options,
                    default=tipo_options
                )

            df_filtrado = pd.DataFrame(columns=solicitacoes_df.columns) # Default
            if not solicitacoes_df.empty:
                # Aplica filtros
                df_filtrado = solicitacoes_df[
                    solicitacoes_df["Status"].isin(status_filtro) &
                    solicitacoes_df["Tipo"].isin(tipo_filtro)
                ]
            
            # Ordena por data, mais recente primeiro
            try:
                if not df_filtrado.empty:
                    df_filtrado["Data_dt"] = pd.to_datetime(df_filtrado["Data"], format="%d/%m/%Y %H:%M")
                    df_filtrado = df_filtrado.sort_values(by="Data_dt", ascending=False).drop(columns=["Data_dt"])
            except Exception:
                # Ignora falha na ordenação se o formato da data estiver incorreto
                pass

            st.dataframe(df_filtrado, use_container_width=True)

            st.markdown("### Atualizar Solicitação")
            if not df_filtrado.empty:
                # Seleciona pelo índice real do DataFrame, não pela posição na tela
                indices_disponiveis = df_filtrado.index.tolist()
                idx_selecionado = st.selectbox(
                    "Selecione a solicitação para atualizar (pelo índice)",
                    options=indices_disponiveis,
                    format_func=lambda x: f"Índice {x} - {solicitacoes_df.loc[x, 'Tipo']} por {solicitacoes_df.loc[x, 'Solicitante']}"
                )
                
                if idx_selecionado is not None:
                    st.write("---")
                    item_atual = solicitacoes_df.loc[idx_selecionado]
                    
                    # Garante que o índice exista mesmo se as opções não estiverem no item_atual
                    status_opts = ["Em análise", "Aprovado", "Rejeitado", "Concluído"]
                    prio_opts = ["Alta", "Média", "Baixa"]
                    
                    status_idx = status_opts.index(item_atual["Status"]) if item_atual["Status"] in status_opts else 0
                    prio_idx = prio_opts.index(item_atual["Prioridade"]) if item_atual["Prioridade"] in prio_opts else 1


                    col_up1, col_up2 = st.columns(2)
                    with col_up1:
                        status = st.selectbox(
                            "Novo status",
                            status_opts,
                            index=status_idx
                        )
                    with col_up2:
                        prioridade = st.selectbox(
                            "Prioridade",
                            prio_opts,
                            index=prio_idx
                        )

                    if st.button("Atualizar Solicitação"):
                        solicitacoes_df.loc[idx_selecionado, "Status"] = status
                        solicitacoes_df.loc[idx_selecionado, "Prioridade"] = prioridade
                        solicitacoes_df.to_csv(SOLICITACOES_FILE, index=False)
                        st.success("📊 Solicitação atualizada com sucesso!")
                        st.rerun()
                else:
                    st.info("Nenhuma solicitação corresponde aos filtros para ser atualizada.")
            else:
                st.info("Nenhuma solicitação para exibir com os filtros atuais.")


        with aba_admin[1]:
            st.subheader("Controle de Estoque")
            
            # Usar st.data_editor para edição direta
            st.info("💡 Você pode editar as quantidades diretamente na tabela abaixo e salvar.")
            edited_estoque = st.data_editor(estoque_df, num_rows="dynamic", use_container_width=True)

            if st.button("Salvar Alterações no Estoque"):
                # Salva o dataframe editado
                edited_estoque.to_csv(ESTOQUE_FILE, index=False)
                st.success("✅ Estoque atualizado com sucesso!")
                st.rerun()

    # Se não estiver autenticado, mostra a tela de senha
    else:
        st.title("🔒 Acesso ao Painel de Admin")
        
        password = st.text_input("Digite a senha de administrador", type="password")

        if st.button("Entrar"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("Login bem-sucedido!")
                st.rerun() # Recarrega a página para mostrar o painel
            else:
                st.error("❌ Senha incorreta.")
