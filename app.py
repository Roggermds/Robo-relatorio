import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import datetime

# Configuração da página no Streamlit
st.set_page_config(page_title="Extração de Relatórios", page_icon="📊", layout="centered")

st.title("📊 Extrator de Relatórios de Condomínio")
st.markdown("Preencha os campos abaixo para realizar o login e extrair a hora/minuto do relatório.")

# --- FORMULÁRIO DE ENTRADA ---
with st.form("form_relatorio"):
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuário / E-mail")
    with col2:
        senha = st.text_input("Senha", type="password")

    condominio = st.selectbox(
        "Selecione o Condomínio",
        ["Condomínio Alpha", "Condomínio Beta", "Condomínio Gamma"]
    )

    col_data1, col_data2 = st.columns(2)
    with col_data1:
        data_inicio = st.date_input("Data de Entrada", datetime.date.today())
    with col_data2:
        data_fim = st.date_input("Data de Saída", datetime.date.today())

    submit_button = st.form_submit_button(label="🚀 Gerar e Extrair Relatório")


# --- FUNÇÃO DE AUTOMAÇÃO PLAYWRIGHT ---
async def rodar_automacao(usuario, senha, condominio, dt_inicio, dt_fim):
    async with async_playwright() as p:
        # Abre o navegador em modo invisível
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. Acesso à página de login (Substitua pela URL real)
            await page.goto("https://site-do-condominio.com/login", timeout=60000)

            # 2. Preenchimento do Login
            await page.fill("input[name='usuario']", usuario)
            await page.fill("input[name='senha']", senha)
            await page.click("button[type='submit']")
            await page.wait_for_load_state("networkidle")

            # 3. Navegação até o relatório
            await page.click("text=Relatórios")

            # 4. Seleção de Condomínio e Datas
            await page.select_option("select#condominio_id", label=condominio)
            await page.fill("input#data_entrada", dt_inicio.strftime("%Y-%m-%d"))
            await page.fill("input#data_saida", dt_fim.strftime("%Y-%m-%d"))

            # 5. Clique para filtrar e extração dos dados
            await page.click("button#btn-filtrar")
            await page.wait_for_selector(".horario-geracao", timeout=30000)

            # Captura do texto com a hora e minuto
            horario = await page.inner_text(".horario-geracao")
            
            await browser.close()
            return True, horario

        except Exception as e:
            await browser.close()
            return False, str(e)


# --- EXECUÇÃO AO CLICAR NO BOTÃO ---
if submit_button:
    if not usuario or not senha:
        st.warning("⚠️ Por favor, informe o usuário e a senha.")
    else:
        with st.spinner("Conectando ao site e extraindo dados... Aguarde."):
            # Executa o loop assíncrono do Playwright
            sucesso, resultado = asyncio.run(
                rodar_automacao(usuario, senha, condominio, data_inicio, data_fim)
            )

            if sucesso:
                st.success("✅ Relatório gerado com sucesso!")
                st.metric(label="Hora e Minuto da Extração", value=resultado)
            else:
                st.error(f"❌ Erro ao processar: {resultado}")
