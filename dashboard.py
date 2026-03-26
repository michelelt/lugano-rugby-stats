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
# Sezione 1: Top 10 Treemap (Su 2 righe)
# --------------------------
st.header("🏆 Top 10 per ogni Statistica")
st.markdown("*I rettangoli più grandi e luminosi indicano i valori più alti nella Top 10.*")

n_stats = len(stats_columns)
meta = math.ceil(n_stats / 2)

stats_riga_1 = stats_columns[:meta]
stats_riga_2 = stats_columns[meta:]

# --- CREAZIONE RIGA 1 ---
cols1 = st.columns(len(stats_riga_1))
for i, stat in enumerate(stats_riga_1):
    top10 = df[['Nome Giocatore', stat]].sort_values(by=stat, ascending=False).head(10)
    top10 = top10[top10[stat] > 0]
    
    if not top10.empty:
        fig = px.treemap(
            top10, path=['Nome Giocatore'], values=stat, color=stat, 
            color_continuous_scale='Viridis', title=stat
        )
        fig.update_traces(textinfo="label+value", textfont=dict(size=14))
        fig.update_layout(margin=dict(t=40, b=10, l=10, r=10), coloraxis_showscale=False, height=350)
        cols1[i].plotly_chart(fig, use_container_width=True)

st.write("") 

# --- CREAZIONE RIGA 2 ---
if len(stats_riga_2) > 0:
    cols2 = st.columns(len(stats_riga_2))
    for i, stat in enumerate(stats_riga_2):
        top10 = df[['Nome Giocatore', stat]].sort_values(by=stat, ascending=False).head(10)
        top10 = top10[top10[stat] > 0]
        
        if not top10.empty:
            fig = px.treemap(
                top10, path=['Nome Giocatore'], values=stat, color=stat, 
                color_continuous_scale='Viridis', title=stat
            )
            fig.update_traces(textinfo="label+value", textfont=dict(size=14))
            fig.update_layout(margin=dict(t=40, b=10, l=10, r=10), coloraxis_showscale=False, height=350)
            cols2[i].plotly_chart(fig, use_container_width=True)

st.divider()


# --------------------------
# Sezione 2: Confronto Giocatori (Faceted Bar Chart)
# --------------------------
st.header("🎯 Analisi e Confronto Giocatori")
st.markdown("Seleziona due o più giocatori per confrontarli.")

giocatori_selezionati = st.multiselect(
    "Cerca e aggiungi giocatori:",
    options=df['Nome Giocatore'].unique()
)

if giocatori_selezionati:
    # Filtriamo il dataframe
    df_selezionati = df[df['Nome Giocatore'].isin(giocatori_selezionati)]
    
    # "Sciogliamo" il dataframe in formato lungo (Long Format) per Plotly Express
    df_melted = df_selezionati.melt(
        id_vars=['Nome Giocatore'], 
        value_vars=stats_columns, 
        var_name='Statistica', 
        value_name='Valore'
    )
    
    # Creiamo i grafici affiancati
    fig_facets = px.bar(
        df_melted, 
        x='Nome Giocatore', 
        y='Valore', 
        color='Nome Giocatore', # Stesso giocatore = Stesso colore
        facet_col='Statistica', # Crea un mini-grafico per ogni colonna statistica
        facet_col_wrap=3,       # Mette massimo 3 grafici per riga
        text='Valore',          # Mostra il numero direttamente sopra o dentro la barra
        title="Confronto Multi-Statistica"
    )
    
    # Formattiamo il testo sulle barre per evitare troppi decimali
    fig_facets.update_traces(texttemplate='%{text:g}', textposition='outside')
    
    # PULIZIA LAYOUT:
    # 1. Rimuoviamo il prefisso "Statistica=" dai titoli dei mini-grafici
    fig_facets.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    # 2. Svincoliamo le assi Y in modo che ogni grafico abbia la sua scala originale corretta
    fig_facets.update_yaxes(matches=None, showticklabels=True)
    
    # 3. Nascondiamo le etichette dell'asse X (i nomi sono già nella legenda laterale) per fare spazio
    fig_facets.update_xaxes(showticklabels=False, title="")
    
    fig_facets.update_layout(height=800, showlegend=True, margin=dict(t=80))
    
    st.plotly_chart(fig_facets, use_container_width=True)
else:
    st.info("👆 Cerca e seleziona almeno un giocatore qui sopra per visualizzare il grafico di confronto.")

st.divider()

# --------------------------
# Sezione 3: Analisi Relazionale (Scatter Plot a Bolle)
# --------------------------
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

st.divider()