import streamlit as st

from variables import \
    date_range_min, date_range_max, \
    date_ranges, rolling_window_min, rolling_window_max, rolling_window_step, \
    nutrition_levels, nutrition_genres, df_meals, \
    df_exercises

from dataframes import \
    get_df_body, get_s_last_body, \
    get_df_nutrition, \
    get_df_workout, get_df_last_workout, \
    upsert_row, delete_row

from charts import \
    get_chart_body_scatter, \
    get_chart_nutrition_scatter, \
    get_chart_workout_scatter, get_chart_workout_timeline

from apis import \
    get_aliment_from_aliment_id



# App
def app():

    # Sidebar
    with st.sidebar:
        st.title('Sidebar')

        st.header('General')
        date = st.date_input(
            'Date', 
            value=date_range_max(), 
            min_value=date_range_min(), 
            max_value=date_range_max(), 
        )

        st.header('Chart')
        date_range = st.select_slider(
            'Range', 
            options=date_ranges, 
            value=date_ranges[0], 
        )
        rolling_window = st.number_input(
            'Rolling window', 
            min_value=rolling_window_min, 
            max_value=rolling_window_max, 
            value=rolling_window_max, 
            step=rolling_window_step, 
        )

        st.header('Nutriton')
        cols = st.columns(2)
        nutrition_level = cols[0].selectbox(
            'Level', 
            options=nutrition_levels, 
            index=0, 
        )
        nutrition_genre = cols[1].selectbox(
            'Genre', 
            options=nutrition_genres, 
            index=0, 
        )

        st.header('Workout')
        cols = st.columns(2)
        workout_pattern = cols[0].selectbox(
            'Pattern', 
            options=df_exercises.Pattern.unique(), 
            index=0, 
        )
        workout_resistance = cols[1].selectbox(
            'Resistance', 
            options=df_exercises.loc[lambda df: (df.Pattern==workout_pattern)].Resistance.unique(), 
            index=0, 
        )

    # Page
    st.title('Tracker')

    st.header('Dataframes')
    st.subheader('Body')
    st.dataframe(get_df_body(date, date))
    st.subheader('Nutrition')
    st.dataframe(get_df_nutrition(nutrition_level, nutrition_genre, date, date))
    st.subheader('Workout')
    st.dataframe(get_df_workout(date, date))

    st.header('Charts')
    st.subheader('Body')
    st.plotly_chart(get_chart_body_scatter(date_range, rolling_window), use_container_width=True)
    st.subheader('Nutrition')
    st.plotly_chart(get_chart_nutrition_scatter(nutrition_level, nutrition_genre, date_range, rolling_window), use_container_width=True)
    st.subheader('Workout')
    st.plotly_chart(get_chart_workout_timeline(date_range), use_container_width=True)
    st.plotly_chart(get_chart_workout_scatter(workout_resistance, workout_pattern, date_range), use_container_width=True)

    st.header('Database')
    with st.form('Body'):
        st.subheader('Body')
        s_last_body = get_s_last_body(date)
        cols = st.columns(6)
        weight = cols[0].number_input('Weight', min_value=0.0, max_value=None, value=s_last_body.Weight, step=0.1)
        muscle_mass = cols[1].number_input('Muscle mass', min_value=0.0, max_value=None, value=s_last_body.Muscle_mass, step=0.1)
        fat_mass = cols[2].number_input('Fat mass', min_value=0.0, max_value=None, value=s_last_body.Fat_mass, step=0.1)
        water_mass = cols[3].number_input('Water mass', min_value=0.0, max_value=None, value=s_last_body.Water_mass, step=0.1)
        bone_mass = cols[4].number_input('Bone mass', min_value=0.0, max_value=None, value=s_last_body.Bone_mass, step=0.1)
        row_body = {
            'Date': date, 
            'Weight': weight, 
            'Muscle_mass': muscle_mass, 
            'Fat_mass': fat_mass, 
            'Water_mass': water_mass, 
            'Bone_mass': bone_mass, 
        }
        if cols[-1].form_submit_button('Upsert'):
            st.write(row_body)
            upsert_row('BodyTracker', row_body)
        if cols[-1].form_submit_button('Delete'):
            delete_row('BodyTracker', row_body)
    with st.form('Nutrition'):
        st.subheader('Nutrition')
        cols = st.columns(4)
        meal = cols[0].selectbox('Meal', options=df_meals.Meal, index=0)
        aliment_id = cols[1].text_input('Aliment_id', value='', max_chars=None)
        quantity = cols[2].number_input('Quantity', min_value=0, max_value=None, value=0, step=5)
        row_nutrition = {
            'Date': date, 
            'Meal_id': df_meals.set_index('Meal').Id.to_dict().get(meal), 
            'Aliment_id': aliment_id, 
            'Quantity': quantity, 
        }
        if cols[-1].form_submit_button('Upsert'):
            _, row_aliment = get_aliment_from_aliment_id(aliment_id)
            st.write(row_aliment)
            st.write(row_nutrition)
            upsert_row('Aliments', row_aliment)
            upsert_row('NutritionTracker', row_nutrition)
        if cols[-1].form_submit_button('Delete'):
            pass
    with st.form('Workout'):
        st.subheader('Workout')
        s_last_workout = get_df_last_workout(date).loc[(workout_pattern, workout_resistance)]
        cols = st.columns(6)
        progression = cols[0].selectbox('Progression', options=df_exercises.loc[lambda df: (df.Pattern==workout_pattern)&(df.Resistance==workout_resistance)].Progression.unique(), index=int(s_last_workout.Level-1))
        rests = cols[1].number_input('Rests', min_value=0.0, max_value=None, value=s_last_workout.Rests, step=0.5)
        weights = cols[2].number_input('Weights', min_value=0.0, max_value=None, value=s_last_workout.Weights, step=0.5)
        reps = cols[3].text_input('Reps', value=s_last_workout.Reps, max_chars=None)
        order = cols[4].number_input('Order', min_value=1, max_value=None, value=s_last_workout.Order, step=1)
        if cols[-1].form_submit_button('Upsert'):
            row_workout = {
                'Date': date, 
                'Exercise_id': df_exercises.set_index('Progression').Id.to_dict().get(progression), 
                'Rests': rests, 
                'Weights': weights, 
                'Reps': reps, 
                'Order': order, 
            }
            st.write(row_workout)
            upsert_row('WorkoutTracker', row_workout)
        if cols[-1].form_submit_button('Delete'):
            pass
    st.subheader('Download')
    st.download_button(
        label='Download database', 
        data=open('Data/database.db', 'rb'), 
        file_name='database.db', 
        mime='application/octet-stream', 
    )

    st.header('Draft')
    st.write(df_meals)
    st.write(df_exercises)
    st.write(get_df_last_workout(date))



# Main
if __name__ == '__main__':

    st.set_page_config(
        page_title='Tracker', 
        page_icon=None, 
        layout='wide', 
        initial_sidebar_state='auto', 
    )

    app()
