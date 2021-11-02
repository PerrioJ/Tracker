import pandas as pd

from dataframes import \
    get_df_meals, get_df_exercises



# Dates
date_range_min = lambda: pd.to_datetime('2021-09-01').date()
date_range_max = lambda: pd.to_datetime('today').date()

# Charts
date_ranges = ['Last week', 'Last month', 'Last year', 'All']
chart_types = ['Line', 'Area']
rolling_window_min, rolling_window_max, rolling_window_step = 1, 7, 2

# Nutrition
nutrition_levels = ['Date', 'Meal', 'Aliment']
nutrition_genres = ['Raw']

df_meals = get_df_meals()

# Workout
df_exercises = get_df_exercises()

# Plots
color_map = {
    'Weight': 'gray', 
    'Muscle_mass': 'lightcoral', 
    'Fat_mass': 'lightgreen', 
    'Water_mass': 'lightblue', 
    'Bone_mass': 'lightgray', 

    'Quantity': 'darkgray', 
    'Calories': 'black', 
    'Proteins': 'magenta', 
    'Carbohydrates': 'yellow', 
    'Lipids': 'cyan', 
    'Alcohol': 'white', 

    'Progression': 'blue', 
    'Rests': 'green', 
    'Weights': 'red', 
    'Reps_Set1': 'gray', 
    'Reps_Set2': 'gray', 
    'Reps_Set3': 'gray', 
    'Reps_Set4': 'gray', 

    'Pattern': 'darkred', 
    'Resistance': 'darkgreen', 
    'Progression': 'darkblue', 
}
facet_row_map = {
    'Weight': 'Weight', 
    'Muscle_mass': 'Composition', 
    'Fat_mass': 'Composition', 
    'Water_mass': 'Composition', 
    'Bone_mass': 'Composition', 

    'Quantity': 'Quantity', 
    'Calories': 'Calories', 
    'Proteins': 'Macros', 
    'Carbohydrates': 'Macros', 
    'Lipids': 'Macros', 
    'Alcohol': 'Macros', 

    'Progression': 'Progression', 
    'Weights': 'Weights', 
    'Rests': 'Rests', 
    'Reps_Set1': 'Sets&Reps', 
    'Reps_Set2': 'Sets&Reps', 
    'Reps_Set3': 'Sets&Reps', 
    'Reps_Set4': 'Sets&Reps', 
}