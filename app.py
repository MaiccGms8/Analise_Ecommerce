import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configurações iniciais

st.set_page_config(page_title="Análise E-commerce", layout="wide")

@st.cache_data
def carregar_e_tratar_dados():

    # Carregamento 

    df = pd.read_excel("data/vendas_ecommerce.xlsx")
    df.columns = df.columns.str.strip()
    
    # --- CÁLCULOS

    df['Data'] = pd.to_datetime(df['Data'])

    # Cálculo da conversão 

    df['conversao'] = df['N° de vendas'] / df['Qtd de acessos'].replace(0, np.nan)

    # Coluna de mês 

    df['mes_idx'] = df['Data'].dt.month
    df['mes_nome'] = df['Data'].dt.strftime('%b/%Y')
    
    return df

try:
    df = carregar_e_tratar_dados()

    st.title(" Dashboard de Performance de Vendas")
    st.markdown("Análise comparativa de faturamento, conversão e impacto promocional.")

    # --- 1. MÉTRICAS GERAIS 

    total_gmv = df['GMV'].sum()
    total_vendas = df['N° de vendas'].sum()
    ticket_medio = total_gmv / total_vendas
    conv_geral = df['conversao'].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("GMV Total", f"R$ {total_gmv:,.2f}")
    m2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    m3.metric("Conv. Média Geral", f"{conv_geral:.2%}")
    m4.metric("Total de Lojas", df['Parceiro'].nunique())

    st.divider()

    # --- 2. ANÁLISE MENSAL 

    st.subheader(" Comparativo Mensal: Abril vs Maio")
    
    col_a, col_b = st.columns(2)
    
    # Variação

    abril = df[df['mes_idx'] == 4].groupby('Parceiro')['conversao'].mean()
    maio = df[df['mes_idx'] == 5].groupby('Parceiro')['conversao'].mean()
    variacao = ((maio - abril) / abril) * 100
    
    with col_a:
        st.write("**Variação de Conversão por Parceiro (%)**")
        st.bar_chart(variacao.dropna().head(15)) # Mostrando os 15 primeiros para não poluir
        
    with col_b:
        st.write("**GMV Total por Mês**")
        faturamento_mensal = df.groupby('mes_nome')['GMV'].sum().reset_index()
        fig_mes = px.pie(faturamento_mensal, values='GMV', names='mes_nome', hole=.3)
        st.plotly_chart(fig_mes, use_container_width=True)

    st.divider()

    # --- 3. ANÁLISE PROMOCIONAL

    st.subheader(" Impacto das Promoções")
    
    c1, c2 = st.columns([1, 2])
    
    promo_df = df[df['Tipo'] == 'Promocional']
    
    with c1:
        st.info(f"**Início:** {promo_df['Data'].min().date()}")
        st.info(f"**Término:** {promo_df['Data'].max().date()}")
        st.success(f"**GMV Promocional:** R$ {promo_df['GMV'].sum():,.2f}")

    with c2:
        top_10_promo = promo_df.groupby('Parceiro')['GMV'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_promo = px.bar(top_10_promo, x='GMV', y='Parceiro', orientation='h', 
                           title="Top 10 Lojas no Período Promocional",
                           color_continuous_scale='Viridis', color='GMV')
        st.plotly_chart(fig_promo, use_container_width=True)

    # --- 4. INSIGHTS ADICIONAIS
    
    with st.expander(" Ver Detalhes e Insights"):
        melhor_dia = df.loc[df['GMV'].idxmax()]
        st.write(f"**Melhor dia de venda geral:** {melhor_dia['Data'].date()} (Loja: {melhor_dia['Parceiro']})")
        st.write("**Top 5 Parceiros por Faturamento Total:**")
        st.table(df.groupby('Parceiro')['GMV'].sum().sort_values(ascending=False).head(5))

except Exception as e:
    st.error(f"Erro ao carregar o dashboard: {e}")
    st.info("Certifique-se de que o arquivo 'vendas_ecommerce.xlsx' está na pasta 'data/'.")