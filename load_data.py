import pandas as pd
import streamlit as st
import numpy as np


#st.set_page_config(layout="wide")

@st.cache(allow_output_mutation=True)
def load_data():
    engine = r"sqlite:///db/Canadian_Foods.db"
    sql = f"""SELECT DISTINCT
            fn.FoodID, fg.FoodGroupName, fn.FoodDescription, 
            nn.NutrientName, na.NutrientValue, nn.NutrientUnit
            FROM FOOD_NAME fn
            LEFT JOIN FOOD_GROUP fg ON
                fn.FoodGroupID = fg.FoodGroupID
            LEFT JOIN CONVERSION_FACTOR cf ON
                fn.FoodID = cf.FoodID
            LEFT JOIN MEASURE_NAME mn ON 
    	        cf.MeasureID = mn.MeasureID
            LEFT JOIN NUTRIENT_AMOUNT na ON 
    	        fn.FoodID = na.FoodID
            LEFT JOIN NUTRIENT_NAME nn ON
    	        na.NutrientID = nn.NutrientID
            WHERE nn.NutrientCode IN (208, 203, 204, 606, 291, 205)
            ORDER BY fn.FoodID
                """
    data = pd.read_sql(sql, engine)
    return data


def category_cleanup(cat):
    if cat == 'PROTEIN':
        cat = cat.replace('PROTEIN', 'Protein')
    elif cat == 'ENERGY (KILOCALORIES)':
        cat = cat.replace('ENERGY (KILOCALORIES)', 'Calories')
    elif cat == 'CARBOHYDRATE, TOTAL (BY DIFFERENCE)':
        cat = cat.replace('CARBOHYDRATE, TOTAL (BY DIFFERENCE)', 'Carbs')
    elif cat == 'FIBRE, TOTAL DIETARY':
        cat = cat.replace('FIBRE, TOTAL DIETARY', 'Fibre')
    elif cat == 'FAT (TOTAL LIPIDS)':
        cat = cat.replace('FAT (TOTAL LIPIDS)', 'Fats')
    elif cat == 'FATTY ACIDS, SATURATED, TOTAL':
        cat = cat.replace('FATTY ACIDS, SATURATED, TOTAL', 'Saturated fats')
    return cat


def get_top_perc(macro, food_id=None, food_desc=None):
    df_top = df_piv.sort_values(by=macro, ascending=False).reset_index()
    rank = None
    if food_id:
        rank = df_top[df_top['FoodID'] == food_id].index[0] + 1
    if food_desc:
        rank = df_top[df_top['FoodDescription'] == food_id].index[0] + 1
    top_perc = (rank / df_piv.shape[0]) * 100
    return np.round(top_perc, 1)


df = load_data()
df['NutrientName'] = df['NutrientName'].apply(lambda x: category_cleanup(x))

df_piv = df.pivot_table(values='NutrientValue', index=['FoodID', 'FoodGroupName', 'FoodDescription'], columns='NutrientName')
df_piv.reset_index(drop=False, inplace=True)
df_piv = df_piv.reindex([
    'FoodID', 'FoodGroupName', 'FoodDescription',
    'Calories', 'Carbs', 'Protein', 'Fats', 'Saturated Fats',
    'Fibre', ], axis=1)
