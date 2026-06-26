import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="KM Morto Biomata",
    layout="wide"
)

st.title("🚛 Painel de KM Morto - Biomata")

arquivo = st.file_uploader(
    "Envie o relatório de macros da Maxtrack",
    type=["xlsx"]
)

if arquivo:
    df = pd.read_excel(arquivo)

    st.subheader("Prévia do relatório")
    st.dataframe(df.head())

    st.subheader("Colunas encontradas")
    st.write(df.columns.tolist())

    coluna_referencia = "Referência"
    coluna_macro = "Macro"
    coluna_frota = "Frota"

    df[coluna_referencia] = df[coluna_referencia].astype(str).str.upper()
    df[coluna_macro] = df[coluna_macro].astype(str).str.upper()

    regra_mandacaia = (
        df[coluna_referencia].str.contains("TELÊMACO - MANDAÇAIA", na=False)
        & df[coluna_macro].isin(["FIM DE JORNADA", "TROCA DE MOTORISTA"])
    )

    regra_garagem = (
        df[coluna_referencia].str.contains("GARAGEM - BBM", na=False)
    )

    df["Tipo KM Morto"] = "Não conta"
    df.loc[regra_mandacaia, "Tipo KM Morto"] = "Troca em Mandaçaia"
    df.loc[regra_garagem, "Tipo KM Morto"] = "Retorno Garagem BBM"

    df_km = df[df["Tipo KM Morto"] != "Não conta"].copy()

    col1, col2, col3 = st.columns(3)

    col1.metric("Eventos KM morto", len(df_km))
    col2.metric("Troca em Mandaçaia", len(df_km[df_km["Tipo KM Morto"] == "Troca em Mandaçaia"]))
    col3.metric("Retorno Garagem BBM", len(df_km[df_km["Tipo KM Morto"] == "Retorno Garagem BBM"]))

    st.subheader("Eventos considerados KM morto")
    st.dataframe(df_km)

    st.subheader("Ranking por frota")

    ranking_frota = (
        df_km.groupby([coluna_frota, "Tipo KM Morto"])
        .size()
        .reset_index(name="Quantidade")
        .sort_values("Quantidade", ascending=False)
    )

    st.dataframe(ranking_frota)

    grafico = px.bar(
        ranking_frota,
        x=coluna_frota,
        y="Quantidade",
        color="Tipo KM Morto",
        title="Quantidade de eventos de KM morto por frota"
    )

    st.plotly_chart(grafico, use_container_width=True)

else:
    st.info("Envie o relatório de macros para começar.")
