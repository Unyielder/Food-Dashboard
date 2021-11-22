import dash
from dash import dcc, html, dash_table
import plotly.express as px
from dash.dependencies import Input, Output, State
from load_data import df
from fuzzywuzzy import process


app = dash.Dash(__name__)

macro_list = ['Calories', 'Carbs', 'Protein', 'Fats', 'Saturated Fats', 'Fibre']

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
    html.Div(id='search-results')
])


@app.callback(Output('group-mean', 'figure'), Input('macro-radio', 'value'))
def update_macro_mean(radio_val):
    df_select = df.groupby("FoodGroupName").mean()[radio_val].sort_values(ascending=True).reset_index()
    fig = px.bar(df_select, x=radio_val, y="FoodGroupName", width=1000, height=650)
    return fig


@app.callback(Output('table_div', 'children'), Input('macro-radio', 'value'))
def filter_df(radio_val):
    df_filter = df[["FoodID", "FoodDescription", radio_val]].sort_values(by=radio_val, ascending=False)

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
def on_click(n_clicks, text_val):
    if text_val:
        matches = process.extract(text_val, df['FoodDescription'].to_list(), limit=150)
        matches = sorted([match[0] for match in matches if int(match[1]) >= 85])
        df_matches = df[df['FoodDescription'].isin(matches)]
        df_matches = df_matches[["FoodID", "FoodDescription"]]

        return html.Div([
            dash_table.DataTable(
                id='search-table',
                columns=[{"name": i, "id": i} for i in df_matches.columns],
                row_selectable='single',
                page_current=0,
                page_size=10,
                data=df_matches.to_dict("records")
            )
        ])
    else:
        return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)
