import pandas as pd
import streamlit as st
import altair as alt
from load_data import df

df_nutri = None

st.title("Food Groups")

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
)

st.write(barchart)

