import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")


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


df = load_data()
df['NutrientName'] = df['NutrientName'].apply(lambda x: category_cleanup(x))
