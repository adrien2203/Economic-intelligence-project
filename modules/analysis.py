import plotly.express as px
from dash import dcc, html
from the_data.sample_data import data

def update_compare(selected_countries):
    # ✅ Vérifications de sélection
    if not selected_countries or len(selected_countries) < 2:
        return dcc.Markdown("**Veuillez sélectionner au moins 2 pays.**")
    if len(selected_countries) > 5:
        return dcc.Markdown("**Vous pouvez sélectionner jusqu'à 5 pays maximum.**")

    rows = data[data['Country'].isin(selected_countries)].copy()
    graphs = []

    # ✅ Renommage clair pour cohérence
    rows['UnemploymentRate'] = rows['Unemployment']  # déjà un float
    # UnemploymentText est déjà présent dans les données

    # 🧠 Résumé dynamique par indicateur
    def get_summary(col):
        if col == 'Unemployment':
            valid_rows = rows.dropna(subset=['UnemploymentRate'])
            if valid_rows.empty:
                return "**Aucune donnée de chômage disponible.**"
            lowest = valid_rows.sort_values(by='UnemploymentRate').iloc[0]
            return f"**{lowest['Country']}** affiche le taux de chômage le plus bas ({lowest['UnemploymentText']})."
        else:
            top = rows.sort_values(by=col, ascending=False).iloc[0]
            return f"**{top['Country']}** a le meilleur score en **{col.lower()}** ({top[col]})."

    # 📊 Liste des indicateurs à comparer
    indicators = ['Attractiveness', 'Economy', 'Stability', 'Unemployment']

    for col in indicators:
        y_col = 'UnemploymentRate' if col == 'Unemployment' else col
        text_col = 'UnemploymentText' if col == 'Unemployment' else col

        fig = px.bar(
            rows,
            x='Country',
            y=y_col,
            color='Country',
            text=text_col,
            title=f"{col} Comparison",
            template='plotly_white'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            height=220,
            margin={"r": 10, "t": 40, "l": 10, "b": 10},
            showlegend=False,
            font=dict(family="Arial", size=12),
            title_font=dict(size=16)
        )

        graphs.append(
            html.Div([
                html.Div(
                    dcc.Markdown(get_summary(col)),
                    style={'width': '30%', 'padding': '10px', 'textAlign': 'left'}
                ),
                html.Div(
                    dcc.Graph(figure=fig),
                    style={'width': '70%', 'padding': '10px'}
                )
            ], style={
                'display': 'flex',
                'flexDirection': 'row',
                'alignItems': 'center',
                'marginBottom': '30px',
                'borderBottom': '1px solid #ccc',
                'paddingBottom': '20px'
            })
        )

    return graphs