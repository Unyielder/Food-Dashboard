import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions import EventListener
from load_data import df, df_piv
from fuzzywuzzy import process


app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Food Dashboard"
server = app.server

macro_list = ['Calories', 'Carbs', 'Protein', 'Fats', 'Saturated Fats', 'Fibre']
listen_prop = "srcElement.innerText"

app.layout = html.Div([
    html.Ul([
        html.Li("Canadian Foods Dashboard", id="nav-title"),
        html.Li(html.A(
            "Food Query", href="https://food-queryx.herokuapp.com/query"), id="food-query-link")
    ], className="nav"),

    html.Div([
        html.P(html.I("Serving size of all food items: 100 grams (g). / Macronutrient unit: grams (g).")),
        html.Div([
            html.H6("Top Food Groups per Nutrient", className="component-title"),
            dcc.RadioItems(
                id='macro-radio',
                options=[{'label': macro, 'value': macro} for macro in macro_list],
                value='Protein',
                labelStyle={'margin-left': '10px'}
            ),
            html.Div([
                dcc.Graph(id='group-mean', className='food-group-chart', style={}),
                html.Div(id='table_div', className='table-top-10', style={'margin-top': '100px', 'width': '45%'}),
            ], style={'display': 'flex', 'flex-direction': 'row', 'margin-bottom': '50px'}, className='div-1'),
        ], className='component'),

        html.Div([
            html.H6("Food Macro Query", className="component-title"),
            html.Div([
                html.P("Please enter food description and SELECT search item:"),
                dcc.Input(
                    id="text-input",
                    type="text",
                    value=""
                ),
                html.Button('Food search', id='submit-val', n_clicks=0),
            ], style={'margin-bottom': '30px'}),

            html.Div([
                html.Div(id='search-results'),
                html.Div(id='query-results'),
                dcc.Graph(id='pie-chart', style={'width': '35%'})
            ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-around', 'gap': '10px'}),

        ], className='component'),

        html.Div([
            html.H6("Nutrient Scatter Plot", className="component-title"),
            html.Div([
                dcc.Dropdown(
                    id='nutrient-dropdown-1',
                    options=[{'label': macro, 'value': macro} for macro in macro_list],
                    value='Protein',
                ),
                dcc.Dropdown(
                    id='nutrient-dropdown-2',
                    options=[{'label': macro, 'value': macro} for macro in macro_list],
                    value='Carbs',
                )
            ], style={'width': '20%'}),
            dcc.Graph(
                id='scatter-matrix',
                style={'width': '100%'}
            )
        ], className='component')
    ], className='container'),


])


@app.callback(Output('group-mean', 'figure'), Input('macro-radio', 'value'))
def update_macro_mean(radio_val):
    df_select = df_piv.groupby("Food Group").mean()[radio_val].sort_values(ascending=True).reset_index()
    fig = px.bar(df_select, x=radio_val, y="Food Group", width=650, height=650)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig


@app.callback(Output('table_div', 'children'), Input('macro-radio', 'value'))
def filter_df(radio_val):
    df_filter = df_piv[["Food Description", radio_val]].sort_values(by=radio_val, ascending=False)

    return html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df_filter.columns],
            data=df_filter[:10].to_dict("records"),
            style_cell={"background-color": 'white'},
            style_data={'whiteSpace':'normal', 'height':'auto'},
            style_header={"background-color": '#54504c', 'color': 'white'}
        )
    ])


@app.callback(Output('search-results', 'children'),
              [Input('submit-val', 'n_clicks')],
              [State('text-input', 'value')])
def button_click(n_clicks, text_val):
    if text_val:
        matches = process.extract(text_val, df_piv['Food Description'].to_list(), limit=150)
        matches = sorted([match[0] for match in matches if int(match[1]) >= 85])
        df_matches = df_piv[df_piv['Food Description'].isin(matches)]
        df_matches = df_matches[["Food Description"]]

        return html.Div([EventListener(id="el", events=[{"event": "click", "props": [listen_prop]}], children=[
            dash_table.DataTable(
                id='search-table',
                columns=[{"name": i, "id": i} for i in df_matches.columns],
                page_current=0,
                page_size=10,
                data=df_matches.to_dict("records"),
                style_cell={"background-color": 'white'},
                style_header={"background-color": '#54504c', 'color': 'white'}
            )
        ])])
    else:
        return dash.no_update


@app.callback(
    [Output('query-results', 'children'),
    Output('pie-chart', 'figure')],
    Input("el", "event"), prevent_initial_call=True)
def query_results(event):
    if event is None:
        raise PreventUpdate

    food_name = event[listen_prop]
    df_stats = df_piv[df_piv['Food Description'] == food_name].reset_index()
    df_fig = df[(df['NutrientName'] != 'Calories') & (df['Food Description'] == food_name)].reset_index()

    carbs = round(df_stats.at[0, 'Carbs'], 2)
    protein = round(df_stats.at[0, 'Protein'], 2)
    fats = round(df_stats.at[0, 'Fats'], 2)
    sat_fats = round(df_stats.at[0, 'Saturated Fats'], 2)
    fibre = round(df_stats.at[0, 'Fibre'], 2)

    fig = px.pie(
        df_fig,
        values='NutrientValue',
        names='NutrientName',
        title='Macro Breakdown'
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return html.Div([
        html.H4(food_name),
        html.Ul([
            html.Li(f"{carbs} g Carbs"),
            html.Li(f"{protein} g Protein"),
            html.Li(f"{fats} g Fats"),
            html.Li(f"{sat_fats} g Saturated fats"),
            html.Li(f"{fibre} g Fibre")
        ])
    ]), fig


@app.callback(
    Output('pie-chart', 'style'), Input('pie-chart', 'figure'))
def hide_graph(fig):
    if fig:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output('scatter-matrix', 'figure'),
              [Input('nutrient-dropdown-1', 'value'),
               Input('nutrient-dropdown-2', 'value')])
def scatter_matrix(x, y):
    x_df = df[df['NutrientName'] == x][['FoodID', 'Food Group', 'Food Description', 'NutrientValue']]
    y_df = df[df['NutrientName'] == y][['FoodID', 'NutrientValue']]

    merged_df = x_df.merge(y_df, how='inner', left_on='FoodID', right_on='FoodID')
    merged_df.columns = ['FoodID', 'Food Group', 'Food Description', 'X', 'Y']
    merged_df.rename(columns={'X': x, 'Y': y}, inplace=True)

    fig = px.scatter(
        merged_df,
        x=f'{x}',
        y=f'{y}',
        color="Food Group"
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
