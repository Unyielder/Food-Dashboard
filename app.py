import dash
from dash import dcc, html, dash_table
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions import EventListener
from load_data import df, df_piv
from fuzzywuzzy import process


app = dash.Dash(__name__, suppress_callback_exceptions=True)

macro_list = ['Calories', 'Carbs', 'Protein', 'Fats', 'Saturated Fats', 'Fibre']
listen_prop = "srcElement.innerText"

app.layout = html.Div([
    html.H1(
        children='Canadian Foods Dashboard',
        style={
            'textAlign': 'center'
        }
    ),
    dcc.RadioItems(
        id='macro-radio',
        options=[{'label': macro, 'value': macro} for macro in macro_list],
        value='Protein'
    ),
    dcc.Graph(id='group-mean'),

    html.Div(id='table_div'),

    html.Div(
        children="Food name",
        id='food-name'),
    dcc.Input(
        id="text-input",
        type="text",
        value=""
    ),

    html.Button('Food search', id='submit-val', n_clicks=0),
    html.Div(id='search-results'),

    html.Div(
        id='query-results'
    ),

    html.Div(id='pie-container', children=[
        dcc.Graph(id='pie-chart')
    ]),


    dcc.Dropdown(
        id='nutrient-dropdown-1',
        options=[{'label': macro, 'value': macro} for macro in macro_list],
        value='Protein'
    ),
    dcc.Dropdown(
        id='nutrient-dropdown-2',
        options=[{'label': macro, 'value': macro} for macro in macro_list],
        value='Carbs'
    ),

    dcc.Graph(id='scatter-matrix')
])


@app.callback(Output('group-mean', 'figure'), Input('macro-radio', 'value'))
def update_macro_mean(radio_val):
    df_select = df_piv.groupby("FoodGroupName").mean()[radio_val].sort_values(ascending=True).reset_index()
    fig = px.bar(df_select, x=radio_val, y="FoodGroupName", width=1000, height=650)
    return fig


@app.callback(Output('table_div', 'children'), Input('macro-radio', 'value'))
def filter_df(radio_val):
    df_filter = df_piv[["FoodID", "FoodDescription", radio_val]].sort_values(by=radio_val, ascending=False)

    return html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df_filter.columns],
            data=df_filter[:10].to_dict("records")
        )
    ])


@app.callback(Output('search-results', 'children'),
              [Input('submit-val', 'n_clicks')],
              [State('text-input', 'value')])
def button_click(n_clicks, text_val):
    if text_val:
        matches = process.extract(text_val, df_piv['FoodDescription'].to_list(), limit=150)
        matches = sorted([match[0] for match in matches if int(match[1]) >= 85])
        df_matches = df_piv[df_piv['FoodDescription'].isin(matches)]
        df_matches = df_matches[["FoodDescription"]]

        return html.Div([EventListener(id="el", events=[{"event": "click", "props": [listen_prop]}], children=[
            dash_table.DataTable(
                id='search-table',
                columns=[{"name": i, "id": i} for i in df_matches.columns],
                page_current=0,
                page_size=10,
                data=df_matches.to_dict("records")
            )
        ])
        ])
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

    df_event = df_piv[df_piv['FoodDescription'] == food_name].reset_index()
    #calories = df_event.at[0, 'Calories']
    carbs = df_event.at[0, 'Carbs']
    protein = df_event.at[0, 'Protein']
    fats = df_event.at[0, 'Fats']
    sat_fats = df_event.at[0, 'Saturated Fats']
    fibre = df_event.at[0, 'Fibre']

    fig = px.pie(
        df[df['FoodDescription'] == food_name],
        values='NutrientValue',
        names='NutrientName',
        title='Proportion of Macros'
    )
    return html.Div([
        html.H4(food_name),
        html.Ul([
            #html.Li(f"{calories} kcal Calories"),
            html.Li(f"{carbs} g Carbs"),
            html.Li(f"{protein} g Protein"),
            html.Li(f"{fats} g Fats"),
            html.Li(f"{sat_fats} g Saturated fats"),
            html.Li(f"{fibre} g Fibre")
        ])
    ]), fig


@app.callback(
    Output('pie-container', 'style'), Input('pie-chart', 'figure'))
def hide_graph(fig):
    if fig:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output('scatter-matrix', 'figure'),
              [Input('nutrient-dropdown-1', 'value'),
               Input('nutrient-dropdown-2', 'value')])
def scatter_matrix(x, y):
    x_df = df[df['NutrientName'] == x][['FoodID', 'FoodGroupName', 'FoodDescription', 'NutrientValue']]
    y_df = df[df['NutrientName'] == y][['FoodID', 'NutrientValue']]

    merged_df = x_df.merge(y_df, how='inner', left_on='FoodID', right_on='FoodID')
    merged_df.columns = ['FoodID', 'FoodGroupName', 'FoodDescription', 'X', 'Y']

    fig = px.scatter(
        merged_df,
        x="X",
        y="Y",
        color="FoodGroupName"
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
