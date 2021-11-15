import streamlit as st
import altair as alt
from load_data import df

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


def scatter_plot(x, y, df):
    x_df = df[df['NutrientName'] == x][['FoodID', 'FoodGroupName', 'FoodDescription', 'NutrientValue']]
    y_df = df[df['NutrientName'] == y][['FoodID', 'NutrientValue']]

    merged_df = x_df.merge(y_df, how='inner', left_on='FoodID', right_on='FoodID')
    merged_df.columns = ['FoodID', 'FoodGroupName', 'FoodDescription', 'X', 'Y']
    # return merged_df.plot(kind='scatter', x='X', y='Y', xlabel=x, ylabel=y, figsize=(12, 6))
    return merged_df


col3, col4 = st.columns([1, 1])


with st.form(key='my_form'):
    with col3:
        x_option = st.selectbox(
            'X-axis',
            ('Calories', 'Protein', 'Fats', 'Saturated fats', 'Carbs', 'Fibre'))
    with col4:
        y_option = st.selectbox(
            'Y-axis',
            ('Calories', 'Protein', 'Fats', 'Saturated fats', 'Carbs', 'Fibre'))
    submit_button = st.form_submit_button(label='Submit')

    df_scatter = scatter_plot(x_option, y_option, df)

scatter = alt.Chart(df_scatter).mark_circle(size=30).encode(
    x='X',
    y='Y',
    color='FoodGroupName',
    tooltip=['FoodDescription', 'FoodGroupName']
).properties(
    height=500,
    width=700
).interactive()

if x_option == 'Calories':
    scatter.encoding.x.title = f"{x_option} (kcal)"
else:
    scatter.encoding.x.title = f"{x_option} (g)"

if y_option == 'Calories':
    scatter.encoding.y.title = f"{y_option} (kcal)"
else:
    scatter.encoding.y.title = f"{y_option} (g)"



st.altair_chart(scatter)
