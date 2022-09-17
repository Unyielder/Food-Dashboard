import pandas as pd
import numpy as np


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


def get_top_perc(macro, food_id=None, food_desc=None):
    df_top = df.sort_values(by=macro, ascending=False).reset_index()
    rank = None
    if food_id:
        rank = df_top[df_top['FoodID'] == food_id].index[0] + 1
    if food_desc:
        rank = df_top[df_top['FoodDescription'] == food_id].index[0] + 1
    top_perc = (rank / df.shape[0]) * 100
    return np.round(top_perc, 1)


def rename_cols(df):
    df['NutrientName'] = [
        name.replace('ENERGY (KILOCALORIES)', 'Calories')
            .replace('CARBOHYDRATE, TOTAL (BY DIFFERENCE)', 'Carbs')
            .replace('PROTEIN', 'Protein')
            .replace('FAT (TOTAL LIPIDS)', 'Fats')
            .replace('FATTY ACIDS, SATURATED, TOTAL', 'Saturated Fats')
            .replace('FIBRE, TOTAL DIETARY', 'Fibre') for name in df['NutrientName']
    ]
    print(df.columns)
    df.rename(columns={'FoodDescription': 'Food Description', 'FoodGroupName': 'Food Group'}, inplace=True)
    return df


df = load_data()
df = rename_cols(df)

df_piv = df.pivot_table(values='NutrientValue', index=['FoodID', 'Food Group', 'Food Description'], columns='NutrientName')
df_piv.reset_index(drop=False, inplace=True)
