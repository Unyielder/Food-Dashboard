import dash
from dash import dcc, html
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
    dcc.Graph(id='group-mean')

])


@app.callback(
    Output(component_id='group-mean', component_property='figure'),
    Input(component_id='macro-radio', component_property='value')
)
def update_macro_mean(radio_val):
    df_select = df.groupby("FoodGroupName").mean()[radio_val].sort_values(ascending=True).reset_index()
    fig = px.bar(df_select, x=radio_val, y="FoodGroupName")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
