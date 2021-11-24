import streamlit as st
import altair as alt
from load_data import df, df_piv, get_top_perc
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from fuzzywuzzy import process

st.markdown(
    """
    <h1 style='text-align: center;'>
        Canadian Foods Dashboard
    </h1>
    <br><br>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([3, 1])

with col2:
    macro_select = st.radio(
        "Select macro:",
        ('Calories', 'Protein', 'Fats', 'Saturated fats', 'Carbs', 'Fibre')
    )
if macro_select == 'Calories':
    df_nutri = df[df['NutrientName'] == 'Calories']
    df_nutri = df_nutri.groupby('FoodGroupName').mean()['NutrientValue'].sort_values(ascending=False).reset_index()
elif macro_select == 'Protein':
    df_nutri = df[df['NutrientName'] == 'Protein']
    df_nutri = df_nutri.groupby('FoodGroupName').mean()['NutrientValue'].sort_values(ascending=False).reset_index()
elif macro_select == 'Fats':
    df_nutri = df[df['NutrientName'] == 'Fats']
    df_nutri = df_nutri.groupby('FoodGroupName').mean()['NutrientValue'].sort_values(ascending=False).reset_index()
elif macro_select == 'Saturated fats':
    df_nutri = df[df['NutrientName'] == 'Saturated fats']
    df_nutri = df_nutri.groupby('FoodGroupName').mean()['NutrientValue'].sort_values(ascending=False).reset_index()
elif macro_select == 'Carbs':
    df_nutri = df[df['NutrientName'] == 'Carbs']
    df_nutri = df_nutri.groupby('FoodGroupName').mean()['NutrientValue'].sort_values(ascending=False).reset_index()
elif macro_select == 'Fibre':
    df_nutri = df[df['NutrientName'] == 'Fibre']
    df_nutri = df_nutri.groupby('FoodGroupName').mean()['NutrientValue'].sort_values(ascending=False).reset_index()

barchart = alt.Chart(df_nutri).mark_bar().encode(
    x='NutrientValue',
    y=alt.X('FoodGroupName', sort=None)
).properties(
    height=500,
    width=700
).interactive()

barchart.encoding.x.title = macro_select
barchart.encoding.y.title = "Food Group"

with col1:
    st.altair_chart(barchart)

@st.cache(allow_output_mutation=True)
def scatter_plot(x, y, df):
    x_df = df[df['NutrientName'] == x][['FoodID', 'FoodGroupName', 'FoodDescription', 'NutrientValue']]
    y_df = df[df['NutrientName'] == y][['FoodID', 'NutrientValue']]

    merged_df = x_df.merge(y_df, how='inner', left_on='FoodID', right_on='FoodID')
    merged_df.columns = ['FoodID', 'FoodGroupName', 'FoodDescription', 'X', 'Y']
    return merged_df


col3, col4 = st.columns([1, 1])

food_groups = list(df['FoodGroupName'].unique())

with st.form(key='scatter'):
    x_option = st.selectbox(
        'X-axis',
        ('Calories', 'Protein', 'Fats', 'Saturated fats', 'Carbs', 'Fibre'))
    y_option = st.selectbox(
        'Y-axis',
        ('Calories', 'Protein', 'Fats', 'Saturated fats', 'Carbs', 'Fibre'))

    submit_button = st.form_submit_button(label='Submit')
    df_scatter = scatter_plot(x_option, y_option, df)

selection = alt.selection_multi(fields=['FoodGroupName'], bind='legend')
scatter = alt.Chart(df_scatter).mark_circle(size=40).encode(
    x='X',
    y='Y',
    color='FoodGroupName',
    opacity=alt.condition(selection, alt.value(1), alt.value(0.05)),
    tooltip=['FoodDescription', 'FoodGroupName']
).properties(
    height=500,
    width=700
).interactive().add_selection(
    selection
)

if x_option == 'Calories':
    scatter.encoding.x.title = f"{x_option} (kcal)"
else:
    scatter.encoding.x.title = f"{x_option} (g)"

if y_option == 'Calories':
    scatter.encoding.y.title = f"{y_option} (kcal)"
else:
    scatter.encoding.y.title = f"{y_option} (g)"

st.altair_chart(scatter)

id_col, or_col, name_col = st.columns([1, 0.5, 3])

food_id = id_col.text_input("Food ID")
or_col.write("Or")
food_name = name_col.text_input("Food name")

food_id = int(food_id)
if food_id:
    df_select = df_piv[df_piv['FoodID'] == food_id].reset_index()
    if df_select.empty:
        st.write("Food ID doesn't exist, please try another one.")
    else:
        food_name = df_select.at[0, 'FoodDescription']
        food_group = df_select.at[0, 'FoodGroupName']
        protein = df_select.at[0, 'Protein']
        carbs = df_select.at[0, 'Carbs']
        fats = df_select.at[0, 'Fats']
        sat_fats = df_select.at[0, 'Saturated Fats']
        fibre = df_select.at[0, 'Fibre']
        calories = df_select.at[0, 'Calories']

        protein_perc = get_top_perc('Protein', food_id=food_id)
        carbs_perc = get_top_perc('Carbs', food_id=food_id)
        fats_perc = get_top_perc('Fats', food_id=food_id)
        sat_fats_perc = get_top_perc('Saturated Fats', food_id=food_id)
        calories_perc = get_top_perc('Calories', food_id=food_id)
        fibre_perc = get_top_perc('Fibre', food_id=food_id)

        col_table, col_pie = st.columns(2)
        col_table.markdown(
            f"""
            <h2>{food_name} (100g)</h2>
            <h4>Food Group: {food_group}</h4>
            <table>
                <tr>
                    <th>Macro</th>
                    <th>Amount (g)</th>
                    <th>Top Percentage</th>
                </tr>
                <tr>
                    <td>Calories</td>
                    <td>{calories}</td>
                    <td>{calories_perc}%</td>
                </tr>
                <tr>
                    <td>Carbohydrates</td>
                    <td>{carbs}</td>
                    <td>{carbs_perc}%</td>
                </tr>
                <tr>
                    <td>Protein</td>
                    <td>{protein}</td>
                    <td>{protein_perc}%</td>
                </tr>
                <tr>
                    <td>Fats</td>
                    <td>{fats}</td>
                    <td>{fats_perc}%</td>
                </tr>
                <tr>
                    <td>Saturated Fats</td>
                    <td>{sat_fats}</td>
                    <td>{sat_fats_perc}%</td>
                </tr>
                <tr>
                    <td>Fibre</td>
                    <td>{fibre}</td>
                    <td>{fibre_perc}%</td>
                </tr>
            </table>""", unsafe_allow_html=True)

        fig = px.pie(df, values='NutrientValue', names='NutrientName', title='Proportion of Macros')
        fig.update_layout(title_x=0.48, legend={"x": 0.80})
        col_pie.write(fig)

if food_name:
    if df[df['FoodDescription'] == food_name].empty:
        st.write("Can't seem to find that, did you mean any of these?")
    matches = process.extract(food_name, df['FoodDescription'].to_list(), limit=10)
    st.selectbox('Select closest matches:', matches[0])

