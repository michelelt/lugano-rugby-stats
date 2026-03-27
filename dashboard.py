import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math

# Importa la funzione dal tuo file preprocessing.py
from preprocessing import crea_dataframe_giocatori

# --------------------------
# Configurazione della pagina
# --------------------------
st.set_page_config(page_title="Statistiche Lugano Rugby", layout="wide")

# --------------------------
# Caricamento Dati
# --------------------------
@st.cache_data
def load_data(path):
    return crea_dataframe_giocatori(path)

file_path = './data/lugano_stats.xlsx'
df = load_data(file_path)

st.title("Statistiche Lugano Rugby")

# Otteniamo tutte le colonne numeriche delle statistiche
stats_columns = [col for col in df.columns if col != 'Nome Giocatore']

# --------------------------
# Creazione dei Tab
# --------------------------
tab1, tab2, tab3 = st.tabs([
    "🏆 Top N Statistiche", 
    "🎯 Confronto Giocatori", 
    "🫧 Analisi Relazionale"
])

# ==========================
# TAB 1: Top N Dinamico
# ==========================
with tab1:
    st.header("🏆 Top Giocatori per Statistica")
    st.markdown("*Usa i controlli qui sotto per personalizzare la visualizzazione.*")

    # --- CONTROLLI ---
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
    
    with col_ctrl1:
        # Mostra le prime 4 metriche di default, o tutte se sono di meno
        default_stats = stats_columns[:4] if len(stats_columns) >= 4 else stats_columns
        metriche_selezionate = st.multiselect(
            "1. Seleziona le metriche:", 
            options=stats_columns, 
            default=default_stats
        )
        
    with col_ctrl2:
        top_n = st.slider(
            "2. Quanti giocatori visualizzare? (Top N):", 
            min_value=3, max_value=30, value=10
        )
        
    with col_ctrl3:
        tipo_grafico = st.selectbox(
            "3. Tipo di grafico:", 
            options=["Treemap", "Bar Chart", "Pie Chart"]
        )

    st.divider()

    if not metriche_selezionate:
        st.warning("⚠️ Seleziona almeno una metrica per visualizzare i grafici.")
    else:
        def crea_grafico(statistica, dataframe):
            if tipo_grafico == "Treemap":
                fig = px.treemap(dataframe, path=['Nome Giocatore'], values=statistica, 
                                 color=statistica, color_continuous_scale='Viridis', title=statistica)
                fig.update_traces(textinfo="label+value", textfont=dict(size=14))
                fig.update_layout(coloraxis_showscale=False)
                
            elif tipo_grafico == "Bar Chart":
                fig = px.bar(dataframe, x='Nome Giocatore', y=statistica, 
                             color=statistica, color_continuous_scale='Viridis', title=statistica, text=statistica)
                fig.update_traces(texttemplate='%{text:g}', textposition='outside')
                fig.update_layout(coloraxis_showscale=False, xaxis_title="")
                
            elif tipo_grafico == "Pie Chart":
                fig = px.pie(dataframe, names='Nome Giocatore', values=statistica, title=statistica, hole=0.3)
                fig.update_traces(textinfo="label+percent")
            
            fig.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=350)
            return fig

        n_stats = len(metriche_selezionate)
        meta = math.ceil(n_stats / 2)
        
        stats_riga_1 = metriche_selezionate[:meta]
        stats_riga_2 = metriche_selezionate[meta:]

        # --- CREAZIONE RIGA 1 ---
        if len(stats_riga_1) > 0:
            cols1 = st.columns(len(stats_riga_1))
            for i, stat in enumerate(stats_riga_1):
                top_df = df[['Nome Giocatore', stat]].sort_values(by=stat, ascending=False).head(top_n)
                top_df = top_df[top_df[stat] > 0]
                
                if not top_df.empty:
                    fig = crea_grafico(stat, top_df)
                    cols1[i].plotly_chart(fig, use_container_width=True)

        st.write("") 

        # --- CREAZIONE RIGA 2 ---
        if len(stats_riga_2) > 0:
            cols2 = st.columns(len(stats_riga_2))
            for i, stat in enumerate(stats_riga_2):
                top_df = df[['Nome Giocatore', stat]].sort_values(by=stat, ascending=False).head(top_n)
                top_df = top_df[top_df[stat] > 0]
                
                if not top_df.empty:
                    fig = crea_grafico(stat, top_df)
                    cols2[i].plotly_chart(fig, use_container_width=True)


# ==========================
# TAB 2: Confronto Giocatori
# ==========================
with tab2:
    st.header("🎯 Analisi e Confronto Giocatori")
    st.markdown("Seleziona i giocatori e le metriche per confrontare i loro profili.")

    # --- CONTROLLI CONFRONTO ---
    col_conf1, col_conf2, col_conf3 = st.columns(3)
    
    with col_conf1:
        giocatori_selezionati = st.multiselect(
            "1. Cerca giocatori:",
            options=df['Nome Giocatore'].unique()
        )
        
    with col_conf2:
        default_stats_conf = stats_columns[:6] if len(stats_columns) >= 6 else stats_columns
        metriche_confronto = st.multiselect(
            "2. Seleziona le metriche:", 
            options=stats_columns, 
            default=default_stats_conf
        )
        
    with col_conf3:
        tipo_grafico_confronto = st.selectbox(
            "3. Tipo di grafico:", 
            options=["Faceted Barplot", "Radar Chart"]
        )

    st.divider()

    if giocatori_selezionati and metriche_confronto:
        # Filtriamo il dataframe
        df_selezionati = df[df['Nome Giocatore'].isin(giocatori_selezionati)]
        
        # Melt per Plotly
        df_melted = df_selezionati.melt(
            id_vars=['Nome Giocatore'], 
            value_vars=metriche_confronto, 
            var_name='Statistica', 
            value_name='Valore'
        )
        
        if tipo_grafico_confronto == "Faceted Barplot":
            # GRAFICO A BARRE AFFIANCATE
            fig_conf = px.bar(
                df_melted, 
                x='Nome Giocatore', 
                y='Valore', 
                color='Nome Giocatore', 
                facet_col='Statistica', 
                facet_col_wrap=3,       
                text='Valore',          
                title="Confronto Multi-Statistica"
            )
            fig_conf.update_traces(texttemplate='%{text:g}', textposition='outside')
            fig_conf.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig_conf.update_yaxes(matches=None, showticklabels=True)
            fig_conf.update_xaxes(showticklabels=False, title="")
            fig_conf.update_layout(height=800, showlegend=True, margin=dict(t=80))
            
        else:
            # RADAR CHART (Ragnatela)
            fig_conf = px.line_polar(
                df_melted, 
                r='Valore', 
                theta='Statistica', 
                color='Nome Giocatore', 
                line_close=True,
                markers=True,
                title="Confronto Profili (Radar Chart)"
            )
            fig_conf.update_traces(fill='toself', opacity=0.5)
            fig_conf.update_layout(
                polar=dict(radialaxis=dict(visible=True, showticklabels=True)),
                height=600,
                margin=dict(t=80)
            )

        st.plotly_chart(fig_conf, use_container_width=True)
    else:
        st.info("👆 Seleziona almeno un giocatore e una metrica qui sopra per visualizzare il grafico.")


# ==========================
# TAB 3: Analisi Relazionale
# ==========================
with tab3:
    st.header("🫧 Analisi Efficienza e Relazioni")

    col_sel1, col_sel2, col_sel3 = st.columns(3)
    with col_sel1:
        x_axis = st.selectbox("Asse X (Orizzontale):", stats_columns, index=0)
    with col_sel2:
        default_y = stats_columns.index('Punti All Time (dal 2011/12)') if 'Punti All Time (dal 2011/12)' in stats_columns else 1
        y_axis = st.selectbox("Asse Y (Verticale):", stats_columns, index=default_y)
    with col_sel3:
        default_size = stats_columns.index('Mete All Time (dal 2011/12)') if 'Mete All Time (dal 2011/12)' in stats_columns else 2
        size_axis = st.selectbox("Dimensione Bolla:", stats_columns, index=default_size)

    df_scatter = df[(df[x_axis] > 0) | (df[y_axis] > 0) | (df[size_axis] > 0)]

    fig_scatter = px.scatter(
        df_scatter, x=x_axis, y=y_axis, size=size_axis, color=size_axis, 
        color_continuous_scale="Viridis", hover_name="Nome Giocatore",
        hover_data={x_axis: True, y_axis: True, size_axis: True},
        title=f"Relazione tra {x_axis} e {y_axis}"
    )

    fig_scatter.update_traces(marker=dict(sizeref=2.*max(df_scatter[size_axis])/(40.**2), sizemin=4))
    fig_scatter.update_layout(height=600, coloraxis_showscale=True)
    st.plotly_chart(fig_scatter, use_container_width=True)