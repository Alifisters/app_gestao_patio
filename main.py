import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from gestao_patio import exe_etl_siab, calculo_media


@st.cache_data(ttl=180000)
def carregar_dados_api():
    patio_interno, patio_externo, mov_ticket, his_siab, dados_sap, analise_prazo, ultm_atualizacao = exe_etl_siab()
    return patio_interno, patio_externo, mov_ticket, his_siab, dados_sap, analise_prazo, ultm_atualizacao


with st.spinner("Conectando ao Siab e carregando dados..."):
    patio_interno, patio_externo, mov_ticket, his_siab, dados_sap, analise_prazo, ultm_atualizacao = carregar_dados_api()
st.success(
    icon="✅", body=f"Dados atualizados com sucesso! \nUltima atualização {ultm_atualizacao}")

# Titulo do app
st.title("Painel de Pátios e Embarques", text_alignment="center")

st.set_page_config(layout='wide', page_icon="logo_comigo.jpg",
                   page_title='Gestão de Embarques', menu_items={"About": "Autoria: ALEFF ANDRADE COSTA"})

# Definindo lista de clientes e de armazens para uso no sidebar
lista_clientes = ["Todos"] + list(pd.concat([
    patio_interno["Transacionador"][patio_interno["TipoPesagem"]
                                    == "CARGA DE PRODUTOS"],
    his_siab["Transacionador"][his_siab["TipoPesagem"] == "CARGA DE PRODUTOS"],
    mov_ticket["Transacionador"][mov_ticket["Tipo Pesagem"]
                                 == "CARGA DE PRODUTOS"],
    dados_sap["Nome"]
]).unique())
ARMAZENS = ['0002-COMPLEXO INDUSTRIAL', '0005-ARMAZEM SANTA HELENA',	'0012-ARMAZEM JATAI',	'0013-ARMAZEM ACREUNA',	'0017-ARMAZEM MONTIVIDIU',	'0022-ARMAZEM PARAUNA',	'0024-ARMAZEM INDIARA',	'0031-ARMAZEM ESTRELA DALVA',	'0033-ARMAZEM CINQUENTAO',	'0034-ARMAZEM PONTE DE PEDRA',
            '0036-ARMAZEM PARAISO',	'0042-ARMAZEM MONTES CLAROS',	'0046-ARMAZEM CAIAPONIA',	'0048-ARMAZEM BOM JARDIM',	'0052-ARMAZEM COMIGO/PAGEL',	'0053-ARMAZEM PALMEIRAS',	'0057-ARMAZEM II SERRANOPOLIS',	'0062-ARMAZEM IPORA',	'0065-ARMAZEM MINEIROS']
TIPO_PESAGEM = ["CARGA DE PRODUTOS", "DESCARGA DE LENHA", "SIMPLES PESAGEM",
                "DESCARGA DE GRÃOS - PRODUTOR",  "DESCARGA DE TERCEIROS", "DESCARGA DE GRÃOS - FILIAIS"]

# Aparencia barra de filtros/sidebar
st.sidebar.caption("Cooperativa Comigo", text_alignment="left")
st.sidebar.image(image="logo_comigo.jpg", width=150)
st.sidebar.title("Filtros:")
st.sidebar.caption("Filtre por Armazém ou Cliente")

# Filtros para o Sidebar
cliente_selecionado = st.sidebar.selectbox("Cliente:", lista_clientes)
armazem_selecionado = st.sidebar.multiselect("Armazens:", ARMAZENS)
tipo_pesagem_sel = st.sidebar.selectbox("Tipo de Pesagem", TIPO_PESAGEM)
status_prazo = st.sidebar.multiselect(
    "Status Prazo Retirada", (list(analise_prazo["Status Atraso"].unique())))
produto_sel = st.sidebar.multiselect(label="Produto(s):",options=(list(his_siab["Produto"].unique())))

# Definição de Dataframes
patio_interno_filt = patio_interno.copy()
pesagem_dia = mov_ticket[["Placa", "Transacionador", "Produto", "Tipo Pesagem","Peso Total Liquido", "Pesagem Saída", "Centro-Armazem"]].copy().dropna(subset="Pesagem Saída")
veiculos_dia = pesagem_dia.copy().sort_values("Pesagem Saída")
dados_sap_filt = dados_sap[['Material', 'Docto.', 'Pedido',
                            'Vál.até', 'Cidade', 'Nome', 'Centro', 'UM', 'Qtd.Pendente']]
tempos_siab = his_siab
relatorio_wa = mov_ticket

# Condições utilizando filtros definidos
if cliente_selecionado != "Todos":
    patio_interno_filt = patio_interno_filt[patio_interno_filt["Transacionador"]
                                            == cliente_selecionado]
    pesagem_dia = pesagem_dia[pesagem_dia["Transacionador"]
                              == cliente_selecionado]
    veiculos_dia = veiculos_dia[veiculos_dia["Transacionador"]
                                == cliente_selecionado]
    dados_sap_filt = dados_sap_filt[dados_sap_filt["Nome"]
                                    == cliente_selecionado]
    tempos_siab = tempos_siab[tempos_siab["Transacionador"]
                              == cliente_selecionado]
    analise_prazo = analise_prazo[analise_prazo["Nome"] == cliente_selecionado]
    relatorio_wa = relatorio_wa[relatorio_wa["Transacionador"]==cliente_selecionado]

if armazem_selecionado:
    patio_interno_filt = patio_interno_filt[patio_interno_filt["Centro"].isin(
        armazem_selecionado)]
    pesagem_dia = pesagem_dia[pesagem_dia["Centro-Armazem"].isin(
        armazem_selecionado)]
    veiculos_dia = veiculos_dia[veiculos_dia["Centro-Armazem"].isin(
        armazem_selecionado)]
    patio_externo = patio_externo[patio_externo["Centro-Armazem"].isin(
        armazem_selecionado)]
    tempos_siab = tempos_siab[tempos_siab["Centro"].isin(armazem_selecionado)]
    dados_sap_filt = dados_sap_filt[dados_sap_filt["Centro"].isin(
        armazem_selecionado)]
    analise_prazo = analise_prazo[analise_prazo["Centro-Armazem"].isin(
        armazem_selecionado)]
    relatorio_wa = relatorio_wa[relatorio_wa["Centro-Armazem"].isin(armazem_selecionado)]

if status_prazo:
    analise_prazo = analise_prazo[analise_prazo["Status Atraso"].isin(
        status_prazo)]

if tipo_pesagem_sel:
    patio_interno_filt = patio_interno_filt[patio_interno_filt["TipoPesagem"]
                                            == tipo_pesagem_sel]
    pesagem_dia = pesagem_dia[pesagem_dia["Tipo Pesagem"] == tipo_pesagem_sel]
    veiculos_dia = veiculos_dia[veiculos_dia["Tipo Pesagem"]
                                == tipo_pesagem_sel]
    patio_externo = patio_externo[patio_externo["TipoPesagem"]
                                  == tipo_pesagem_sel]
    tempos_siab = tempos_siab[tempos_siab["TipoPesagem"] == tipo_pesagem_sel]
    relatorio_wa = relatorio_wa[relatorio_wa["Tipo Pesagem"]==tipo_pesagem_sel]

tmp_entrada = calculo_media(
    tempos_siab, 'Check-in Portaria', 'Entrada Portaria')
tmp_ini_carr = calculo_media(
    tempos_siab, 'Entrada Portaria', 'Pesagem de Entrada')
tmp_carreg = calculo_media(tempos_siab, 'Pesagem de Entrada', 'Pesagem Saída')
tmp_liberacao = calculo_media(tempos_siab, 'Pesagem Saída', 'Saída Portaria')

tab_graficos, tab_whatsapp, tab_tabelas, tab_sunburst = st.tabs(
    ["📊 Painel Gerencial", "📱 Relatório WhatsApp", "⏲️ Analise Prazo", "☀️ Gráfico Explosão Solar"])

with tab_graficos:
    # Gráfico de patio externo e visuais de média de tempo
    with st.container():
        st.markdown("<h1 style='color: ##F8F8FF; font-size: 16px; margin-bottom: 10px;'>TEMPO MÉDIO POR ETAPA</h1>",
                    unsafe_allow_html=True)
        col_med_temp, col_med_temp2, col_med_temp3, col_med_temp4 = st.columns(
            4)
        st.markdown("""
            <style>
            .caixa-metrica {
                background-color: #1C1C1C;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.7);
                margin-bottom: 10px;
            }
            .titulo-metrica {
                font-size: 13px;
                color: #999;
                text-transform: uppercase;
                font-weight: 700;
                margin-bottom: 5px;
            }
            .valor-metrica {
                font-size: 22px;
                font-weight: 900;
                color: #999;
            }
            </style>
        """, unsafe_allow_html=True)

        with col_med_temp:
            st.markdown(f"""
            <div class="caixa-metrica">
                <div class="titulo-metrica">Tempo Espera Entrada</div>
                <div class="valor-metrica">{tmp_entrada}</div>
            </div>
        """, unsafe_allow_html=True)

        with col_med_temp2:
            st.markdown(f"""
            <div class="caixa-metrica">
                <div class="titulo-metrica">Tempo Inicio Carregamento</div>
                <div class="valor-metrica">{tmp_ini_carr}</div>
            </div>
        """, unsafe_allow_html=True)

        with col_med_temp3:
            st.markdown(f"""
            <div class="caixa-metrica">
                <div class="titulo-metrica">Tempo Carregamento</div>
                <div class="valor-metrica">{tmp_carreg}</div>
            </div>
        """, unsafe_allow_html=True)

        with col_med_temp4:
            st.markdown(f"""
            <div class="caixa-metrica">
                <div class="titulo-metrica">Tempo Liberação Saída</div>
                <div class="valor-metrica">{tmp_liberacao}</div>
            </div>
        """, unsafe_allow_html=True)

    # Gráficos de PATIO INTERNO e VEICULOS CARREGADOS POR DIA
    with st.container():
        col_patio_int, col_qtd_dia = st.columns(2)
        with col_patio_int:
            if not patio_interno_filt.empty:  # Gráfico Patio interno
                patio_interno_agrp = patio_interno_filt.groupby(
                    ['Produto','Centro','Próxima Etapa']).size().reset_index(name="Qtd Veiculos")

                fig = px.bar(
                    patio_interno_agrp,
                    x="Centro",
                    y="Qtd Veiculos",
                    color="Próxima Etapa",
                    barmode="group",
                    title="N° Veiculos / Produto / Centro / Etapa Pendente",
                    facet_col="Produto",
                    orientation="v",
                    text="Qtd Veiculos",
                    labels={"Produto,Centro":"Produto / Centro"}
                ).update_traces(
                    textposition='outside',
                    cliponaxis=False,
                ).update_layout(
                    xaxis_showgrid=False,
                    yaxis_visible=True,
                    legend_title="Etapa Pendente",
                ).for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1])
                ).update_xaxes(title_text="")

                # Renderiza o gráfico na tela
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(
                    "Nenhum veículo encontrado para a combinação de filtros selecionada.")

        with col_qtd_dia:
            if not veiculos_dia.empty:  # Gráfico Qtd Veiculos por dia
                veiculos_dia = veiculos_dia[["Produto","Pesagem Saída", "Centro-Armazem", "Placa"]].groupby(
                    ["Produto","Pesagem Saída", "Centro-Armazem"]).count().reset_index().sort_values(["Pesagem Saída"])
                fig_qtd_dia = px.bar(
                    veiculos_dia,
                    x="Centro-Armazem",
                    y="Placa",
                    color="Pesagem Saída",
                    text="Placa",
                    title="Qtd Veiculos Pesados / Produto / Centro / Data",
                    barmode='group',
                    facet_col="Produto",
                    orientation="v",
                    labels={'Placa': 'N° Veiculos'}
                ).update_traces(
                    textposition="outside",
                    cliponaxis=False
                ).update_layout(
                    yaxis_showgrid=True,
                    xaxis_showgrid=False,
                    xaxis_visible=True,
                    legend_title="Data Pesagem",
                    plot_bgcolor="rgba(0,0,0,0)"
                ).for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1])
                ).update_xaxes(title_text="")

                st.plotly_chart(fig_qtd_dia, use_container_width=True)
            else:
                st.warning(
                    "Sem dados de veiculos nesse periodo para essa combinação de filtros (Cliente e Centro)")

    # Gráfico de volume pesado por dia
    if not pesagem_dia.empty:
        pesagem_dia = pesagem_dia[["Produto","Peso Total Liquido", "Pesagem Saída", "Centro-Armazem"]
                                  ].groupby(["Produto","Pesagem Saída", "Centro-Armazem"]).sum().reset_index()
        fig_pesagem = px.bar(
            pesagem_dia,
            x='Centro-Armazem',
            y='Peso Total Liquido',
            color='Pesagem Saída',
            orientation='v',
            facet_col="Produto",
            text='Peso Total Liquido',
            title='Pesagem Semana',
            barmode='group'
        ).update_traces(
            textposition='outside',
            cliponaxis=False
        ).update_layout(yaxis_showgrid=True,
            xaxis_showgrid=False,
            xaxis_visible=True,
            legend_title="Data Pesagem",
            plot_bgcolor="rgba(0,0,0,0)"
        ).for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1])
        ).update_xaxes(title_text="")

        st.plotly_chart(fig_pesagem, use_container_width=True)
    else:
        st.warning(
            "Sem carregamento nesse periodo para a combinação selecionada (Cliente e Armazem)")

    patio_externo_agrp = patio_externo[[
        "Centro-Armazem", "Placa"]].groupby("Centro-Armazem").count().reset_index(col_level="Centro-Armazem")
    st.sidebar.caption("Veiculos Pátio Externo")
    st.sidebar.dataframe(patio_externo_agrp, hide_index=True)
    st.dataframe(dados_sap_filt, hide_index=True)

with tab_whatsapp:
    st.subheader("Gerador de Mensagem")
    st.caption(
        "Filtre conforme Cliente e Armazem, Copie o texto abaixo e cole no WhatsApp.")
# ====================================================================
# RELATÓRIO PARA WHATSAPP
# ====================================================================
    texto_wa = "*RESUMO OPERACIONAL - PÁTIOS E EMBARQUES*\n\n"

    # 1. Volume Carregado na Semana
    if not relatorio_wa.empty:
        resumo_relatorio_wa = relatorio_wa.groupby(["Centro-Armazem","Produto","Pesagem Saída"]).agg({'Peso Total Liquido':'sum','Placa':'count'}).reset_index()
        texto_wa = f"*RESUMO OPERACIONAL -  PÁTIOS E EMBARQUES*\n"
        centros_c_dados = resumo_relatorio_wa["Centro-Armazem"].unique()
        for centro in centros_c_dados:
            texto_wa += f"*📍 {centro}* \n\n"
            dados_centro = resumo_relatorio_wa[resumo_relatorio_wa["Centro-Armazem"]==centro]
            produtos_no_centro = dados_centro["Produto"].unique()
            for produto in produtos_no_centro:
                texto_wa += f"  `{produto}`\n"
                dados_centro = dados_centro[dados_centro["Produto"]==produto]
                for indice, registro in dados_centro.iterrows():
                    texto_wa += f"* {registro["Pesagem Saída"]} - {registro["Peso Total Liquido"]:,.2f} Ton - {registro["Placa"]} Veic.\n"
                texto_wa += f"\n"
    else: texto_wa += " `Sem registro de embarque nos ultimos 7 dias`\n"
    # 3. Status Pátio Interno
    texto_wa += "\n> 📊​ Patio Interno / Etapa Pendente:\n"
    if not patio_interno_filt.empty:
        # Agrupa por Centro e Próxima Etapa, contando as ocorrências
        etapas_centro = patio_interno_filt.groupby(
            ["Centro", "Próxima Etapa"]).size().reset_index(name="Qtd")

        # Cria uma lista apenas com os centros que têm caminhões no momento
        centros_ativos = etapas_centro["Centro"].unique()

        for centro in centros_ativos:
            # Imprime o nome do Centro em negrito
            texto_wa += f"\n📍 *{centro}*\n"

            # Filtra as etapas apenas desse centro específico
            dados_do_centro = etapas_centro[etapas_centro["Centro"] == centro]

            # Imprime as etapas e quantidades abaixo do centro
            for _, row in dados_do_centro.iterrows():
                texto_wa += f"   - {row['Próxima Etapa']} = {row['Qtd']} veíc.\n"
    else:
        texto_wa += "  `Pátio vazio ⚠️​⚠️​⚠️`\n"

    # 4. Saldos de Contratos SAP
    texto_wa += "\n> 📜 Saldos contratos:\n"
    if not dados_sap_filt.empty:
        # Itera linha por linha da tabela do SAP
        for _, row in dados_sap_filt.iterrows():
            contrato = row.get("Pedido", "-")
            centro = str(row.get("Centro", "-")).replace(".0",
                                                         "")  # Limpa a formatação do centro
            venc = row.get("Vál.até", "-")
            um = row.get("UM", "-")

            # Tenta converter o volume para número. Se for um texto não numérico ou vazio, assume 0.0
            try:
                vol = float(row.get("Qtd.Pendente", 0))
            except (ValueError, TypeError):
                vol = 0.0

            texto_wa += f"  Contrato {contrato} - Centro {centro} - Venc. {venc} - Vol: {vol:,.2f} - {um} \n"
    else:
        texto_wa += "  `Sem saldos pendentes`\n"
    st.code(texto_wa, language="markdown")

with tab_tabelas:
    st.dataframe(analise_prazo, hide_index=True)

    analise_prazo_agrp_cliente = (analise_prazo[["Nome", "Vál.até", "Centro-Armazem", "Qtd.Pendente",
                                  "Status Atraso"]].groupby(["Nome", "Status Atraso", "Vál.até", "Centro-Armazem"]).sum())
    analise_prazo_agrp_centro = (analise_prazo[["Nome", "Vál.até", "Centro-Armazem", "Qtd.Pendente",
                                 "Status Atraso"]].groupby(["Centro-Armazem", "Status Atraso", "Vál.até", "Nome"]).sum())

    st.markdown(analise_prazo_agrp_cliente.to_html(), unsafe_allow_html=True)

with tab_sunburst:
    col_sunburst_cliente, col_sunburst_centro = st.columns(2)
    with col_sunburst_cliente:
        if not analise_prazo_agrp_cliente.empty:
            fig_sunburst_cliente = px.sunburst(analise_prazo_agrp_cliente.reset_index(), path=[
                                               "Nome", "Status Atraso", "Vál.até", "Centro-Armazem"], values="Qtd.Pendente", color="Qtd.Pendente", color_continuous_scale="aggrnyl_r", title="Distribuição por Status de Vencimento (Cliente)")
            st.plotly_chart(fig_sunburst_cliente, use_container_width=True)
        else:
            st.warning(
                "Nenhum dados disponivel para essa combinação de filtros")
    with col_sunburst_centro:
        if not analise_prazo_agrp_centro.empty:
            fig_sunburst_centro = px.sunburst(analise_prazo_agrp_centro.reset_index(), path=[
                                              "Centro-Armazem", "Status Atraso", "Vál.até", "Nome"], values="Qtd.Pendente", color="Qtd.Pendente", color_continuous_scale="aggrnyl_r", title="Distribuição por Status de Vencimento (Centro)")
            st.plotly_chart(fig_sunburst_centro, use_container_width=True,)
        else:
            st.warning(
                "Nenhum dados disponivel para essa combinação de filtros")