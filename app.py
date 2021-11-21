import dash
from dash import dcc, html, dash_table
import plotly.express as px
from dash.dependencies import Input, Output
from load_data import df


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

    html.Div(
        id='table_div'),


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


if __name__ == '__main__':
    app.run_server(debug=True)
