from dash import Input, Output, callback_context
from dash import html, dcc
from the_data.sample_data import data
from utils.api import get_latest_unemployment
from modules.analysis import update_compare

def register_callbacks(app):

    # Navigation entre pages
    @app.callback(
        Output('page-content', 'children'),
        Output('map', 'style'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == "/compare":
            layout = html.Div([
                html.H2("Country Comparator"),
                html.P("Select 2 to 5 countries to compare:"),
                dcc.Dropdown(
                    id='countries',
                    options=[{'label': c, 'value': c} for c in data['Country']],
                    multi=True,
                    placeholder="Choose countries",
                    style={'width': '60%'}
                ),
                html.Div(id='compare-warning', style={'color': 'red', 'margin-top': '10px'}),
                html.Div(id='compare-graphs', style={'margin-top': '30px'}),
                html.Br(),
                html.A("Back to map", href="/")
            ])
            map_style = {'display': 'none'}
        elif pathname.startswith("/country-"):
            code = pathname.split("-")[1]
            row = data[data['ISO_Code'] == code].iloc[0]
            layout = html.Div([
                html.H2(row['Country']),
                html.Div([
                    html.Button("General", id='btn-general', n_clicks=0),
                    html.Button("Economy", id='btn-economy', n_clicks=0),
                    html.Button("Legal", id='btn-legal', n_clicks=0),
                    html.Button("Competition", id='btn-competition', n_clicks=0)
                ], style={'margin-bottom':'20px'}),
                html.Div(id='country-subpage'),
                html.Br(),
                html.A("Back to map", href="/")
            ])
            map_style = {'display': 'none'}
        else:
            layout = html.Div([
                html.H2("Global Map")
            ])
            map_style = {'display': 'block'}

        return layout, map_style

    # Sous-pages d’un pays
    @app.callback(
        Output('country-subpage', 'children'),
        Input('btn-general', 'n_clicks'),
        Input('btn-economy', 'n_clicks'),
        Input('btn-legal', 'n_clicks'),
        Input('btn-competition', 'n_clicks'),
        Input('url', 'pathname')
    )
    def update_country_subpage(n1, n2, n3, n4, pathname):
        code = pathname.split("-")[1]
        row = data[data['ISO_Code'] == code].iloc[0]

        ctx = callback_context
        if not ctx.triggered:
            tab = "general"
        else:
            tab_id = ctx.triggered[0]['prop_id'].split('.')[0]
            tab = tab_id.split('-')[1]

        if tab == "general":
            return html.Div([
                html.H3("General Info"),
                html.P("No description available.")
            ])
        elif tab == "economy":
            unemployment = get_latest_unemployment(code)
            return html.Div([
                html.H3("Economy"),
                html.Ul([
                    html.Li(f"Economy score: {row['Economy']}"),
                    html.Li(f"Attractiveness: {row['Attractiveness']}"),
                    html.Li(f"Unemployment Rate: {unemployment[1]}")                ])
            ])
        elif tab == "legal":
            return html.Div([
                html.H3("Legal"),
                html.P("Legal info placeholder")
            ])
        elif tab == "competition":
            return html.Div([
                html.H3("Competition"),
                html.P("Competition info placeholder")
            ])
        return html.Div("No data")

    # Clic sur la carte → page pays
    @app.callback(
        Output('url', 'pathname'),
        Input('map', 'clickData'),
        prevent_initial_call=True
    )
    def country_click(clickData):
        if clickData:
            code = clickData['points'][0]['location']
            return f"/country-{code}"
        return "/"

    # Comparateur multi-pays avec validation
    @app.callback(
        Output('compare-graphs', 'children'),
        Output('compare-warning', 'children'),
        Input('countries', 'value')
    )
    def update_comparator(selected_countries):
        if not selected_countries:
            return html.Div(), "Please select between 2 and 5 countries."
        if len(selected_countries) < 2:
            return html.Div(), "Select at least 2 countries."
        if len(selected_countries) > 5:
            return html.Div(), "You can compare up to 5 countries only."

        graphs = update_compare(selected_countries)
        return graphs, ""