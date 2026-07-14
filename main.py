import streamlit as st
import pandas as pd
import plotly.express as px
from gestao_patio import exe_etl_siab, calculo_media


@st.cache_data(ttl=30)
def carregar_dados_api():
    patio_interno, patio_externo, mov_ticket, his_siab, dados_sap = exe_etl_siab()
    return patio_interno, patio_externo, mov_ticket, his_siab, dados_sap


with st.spinner("Conectando ao Siab e carregando dados..."):
    patio_interno, patio_externo, mov_ticket, his_siab, dados_sap = carregar_dados_api()
st.success("Dados atualizados com sucesso!")

# Titulo do app
st.title("Painel de Pátios e Embarques", text_alignment="center")

st.set_page_config(layout='wide', page_icon="logo_comigo.jpg",
                   page_title='Gestão de Embarques', menu_items={"About": "Autoria: ALEFF ANDRADE COSTA"})

# Definindo lista de clientes e de armazens para uso no sidebar
lista_clientes = ["Todos"] + list(pd.concat([patio_interno["Transacionador"],
                                  his_siab["Transacionador"], mov_ticket["Transacionador"], dados_sap["Nome"]]).unique())
ARMAZENS = ['0005-ARMAZEM SANTA HELENA',	'0012-ARMAZEM JATAI',	'0013-ARMAZEM ACREUNA',	'0017-ARMAZEM MONTIVIDIU',	'0022-ARMAZEM PARAUNA',	'0024-ARMAZEM INDIARA',	'0031-ARMAZEM ESTRELA DALVA',	'0033-ARMAZEM CINQUENTÃO',	'0034-ARMAZEM PONTE DE PEDRA',
            '0036-ARMAZEM PARAISO',	'0042-ARMAZEM MONTES CLAROS',	'0046-ARMAZEM CAIAPONIA',	'0048-ARMAZEM BOM JARDIM',	'0052-ARMAZEM COMIGO/PAGEL',	'0053-ARMAZEM PALMEIRAS',	'0057-ARMAZEM SERRANOPOLIS',	'0062-ARMAZEM IPORA',	'0065-ARMAZEM MINEIROS']
TIPO_PESAGEM = ["CARGA DE PRODUTOS", "DESCARGA DE LENHA", "SIMPLES PESAGEM",
                "DESCARGA DE GRÃOS - PRODUTOR",  "DESCARGA DE TERCEIROS", "DESCARGA DE GRÃOS - FILIAIS"]

# Aparencia barra de filtros/sidebar
st.sidebar.caption("Cooperativa Comigo", text_alignment="left")
st.sidebar.image(image="logo_comigo.jpg", width=150)
st.sidebar.title("Filtros:")
st.sidebar.caption("Filtre por Armazém ou Cliente")

# Filtros para o Sidebar
cliente_selecionado = st.sidebar.selectbox("Cliente:", lista_clientes)
armazem_selecionado = st.sidebar.multiselect("Armazem", ARMAZENS)
tipo_pesagem_sel = st.sidebar.selectbox("Tipo de Pesagem", TIPO_PESAGEM)

# Definição de Dataframes
patio_interno_filt = patio_interno.copy()
pesagem_dia = mov_ticket[["Placa", "Transacionador", "Produto", "Tipo Pesagem",
                          "Peso Total Liquido", "Pesagem Saída", "Centro-Armazem"]].copy().dropna(subset="Pesagem Saída")
veiculos_dia = pesagem_dia.copy()
dados_sap_filt = dados_sap[['Material', 'Docto.', 'Pedido',
                            'Vál.até', 'Cidade', 'Nome', 'Centro', 'UM', 'Qtd.Pendente']]
tempos_siab = his_siab


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

if tipo_pesagem_sel:
    patio_interno_filt = patio_interno_filt[patio_interno_filt["TipoPesagem"]
                                            == tipo_pesagem_sel]
    pesagem_dia = pesagem_dia[pesagem_dia["Tipo Pesagem"] == tipo_pesagem_sel]
    veiculos_dia = veiculos_dia[veiculos_dia["Tipo Pesagem"]
                                == tipo_pesagem_sel]
    patio_externo = patio_externo[patio_externo["TipoPesagem"]
                                  == tipo_pesagem_sel]
    tempos_siab = tempos_siab[tempos_siab["TipoPesagem"] == tipo_pesagem_sel]

tmp_entrada = calculo_media(
    tempos_siab, 'Check-in Portaria', 'Entrada Portaria')
tmp_ini_carr = calculo_media(
    tempos_siab, 'Entrada Portaria', 'Pesagem de Entrada')
tmp_carreg = calculo_media(tempos_siab, 'Pesagem de Entrada', 'Pesagem Saída')
tmp_liberacao = calculo_media(tempos_siab, 'Pesagem Saída', 'Saída Portaria')

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
                ['Próxima Etapa', 'Centro']).size().reset_index(name="Qtd Veiculos")

            fig = px.bar(
                patio_interno_agrp,
                # Eixo Y = Etapa (Fica na vertical do gráfico horizontal)
                x='Centro',
                y='Qtd Veiculos',             # Eixo X = Quantidade
                color='Próxima Etapa',              # Cada armazém terá uma cor diferente
                orientation='v',              # Transforma a barra em Horizontal
                text="Qtd Veiculos",
                title="Qtd Veículos/Etapa Pendente/Armazém",
                # 'group' deixa as barras lado a lado, mude para 'stack' para empilhar
                barmode='stack'
            )

        # Customizações visuais solicitadas: posicionar número acima e remover as linhas
            fig.update_traces(
                textposition='outside',       # Força o número a ficar ACIMA da coluna vertical
                cliponaxis=False              # Evita que números altos sumam no topo do gráfico
            )

            fig.update_layout(
                yaxis_showgrid=False,
                xaxis_showgrid=False,
                yaxis_visible=False,
                xaxis_title="Centro-Armazem",
                legend_title="Etapas da Operação",
                plot_bgcolor='rgba(0,0,0,0)'
            )

            # Renderiza o gráfico na tela
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(
                "Nenhum veículo encontrado para a combinação de filtros selecionada.")

    with col_qtd_dia:
        if not veiculos_dia.empty:  # Gráfico Qtd Veiculos por dia
            veiculos_dia = veiculos_dia[["Pesagem Saída", "Centro-Armazem", "Placa"]].groupby(
                ["Pesagem Saída", "Centro-Armazem"]).count().reset_index()
            fig_qtd_dia = px.bar(
                veiculos_dia,
                x="Centro-Armazem",
                y="Placa",
                color="Pesagem Saída",
                text="Placa",
                title="Qtd Veiculos Pesados",
                barmode='group',
                orientation="v",
                labels={'Placa': 'N° Veiculos'}
            )
            fig_qtd_dia.update_traces(
                textposition="outside",
                cliponaxis=False
            )
            fig_qtd_dia.update_layout(
                yaxis_showgrid=False,
                xaxis_showgrid=False,
                xaxis_visible=True,
                legend_title="Data Pesagem",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_qtd_dia, use_container_width=True)
        else:
            st.warning(
                "Sem dados de veiculos nesse periodo para essa combinação de filtros (Cliente e Centro)")

# Gráfico de volume pesado por dia
if not pesagem_dia.empty:
    pesagem_dia = pesagem_dia[["Peso Total Liquido", "Pesagem Saída", "Centro-Armazem"]
                              ].groupby(["Pesagem Saída", "Centro-Armazem"]).sum().reset_index()
    fig_pesagem = px.bar(
        pesagem_dia,
        x='Centro-Armazem',
        y='Peso Total Liquido',
        color='Pesagem Saída',
        orientation='v',
        text='Peso Total Liquido',
        title='Pesagem Semana',
        barmode='group')

    fig_pesagem.update_traces(
        textposition='outside',
        cliponaxis=False)

    fig_pesagem.update_layout(yaxis_showgrid=False,
                              xaxis_showgrid=False,
                              xaxis_visible=True,
                              legend_title="Data Pesagem",
                              plot_bgcolor="rgba(0,0,0,0)")

    st.plotly_chart(fig_pesagem, use_container_width=True)
else:
    st.warning(
        "Sem carregamento nesse periodo para a combinação selecionada (Cliente e Armazem)")

patio_externo_agrp = patio_externo[[
    "Centro-Armazem", "Placa"]].groupby("Centro-Armazem").count().reset_index(col_level="Centro-Armazem")
st.sidebar.caption("Veiculos Pátio Externo")
st.sidebar.dataframe(patio_externo_agrp, hide_index=True)

st.table(dados_sap_filt)
