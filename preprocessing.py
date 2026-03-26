import pandas as pd

def crea_dataframe_giocatori(file_path):
    # Usa read_excel per i file .xlsx (invece di read_csv)
    df = pd.read_excel(file_path, skiprows=2)
    
    all_players_stats = {}
    
    for col_idx in range(0, len(df.columns), 3):
        if col_idx + 1 >= len(df.columns):
            break
            
        stat_name = str(df.columns[col_idx])
        
        # Saltiamo le colonne senza nome
        if stat_name.startswith("Unnamed"):
            continue
            
        name_col = df.columns[col_idx]
        val_col = df.columns[col_idx + 1]
        
        subset = df[[name_col, val_col]].dropna()
        
        for _, row in subset.iterrows():
            player_name = row[name_col]
            stat_val = row[val_col]
            
            if isinstance(player_name, str):
                player_name = player_name.strip()
                
                if player_name not in all_players_stats:
                    all_players_stats[player_name] = {}
                    
                all_players_stats[player_name][stat_name] = stat_val
    
    final_df = pd.DataFrame.from_dict(all_players_stats, orient='index')
    final_df.index.name = 'Nome Giocatore'
    final_df = final_df.reset_index()
    
    final_df = final_df.sort_values(by='Nome Giocatore').reset_index(drop=True)
    final_df = final_df.fillna(0)
    
    return final_df

