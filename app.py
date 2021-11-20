import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from load_data import df

app = dash.Dash(__name__)

df_pro = df.groupby("FoodGroupName").mean()['Protein'].sort_values(ascending=False).reset_index()
fig = px.bar(df_pro, x="FoodGroupName", y="Protein")


app.layout = html.Div([
    html.H1('Hello Dash'),

    html.Div('''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)