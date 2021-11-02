import pandas as pd

from variables import \
    date_range_min, date_range_max, \
    color_map, facet_row_map, \
    df_exercises

from dataframes import \
    get_df_body, get_df_nutrition, get_df_workout

import plotly.express as px



#
def get_date_range(date_range):
    date_max = date_range_max()
    if date_range == 'Last week':
        date_min = (date_max - pd.DateOffset(weeks=1, days=-1)).date()
    elif date_range == 'Last month':
        date_min = (date_max - pd.DateOffset(months=1, days=-1)).date()
    elif date_range == 'Last year':
        date_min = (date_max - pd.DateOffset(years=1, days=-1)).date()
    else:
        date_min = date_range_min()
    return((date_min, date_max))

#
def prepare_df_plotly_scatter(df):
    df_scatter = (
        df
        .melt(
            id_vars=None, 
            value_vars=None, 
            var_name='Variable', 
            value_name='Value', 
            col_level=None, 
            ignore_index=False, 
        )
        
        .assign(
            X=lambda df: pd.to_datetime(df.index.get_level_values('Date')), 
            Y=lambda df: df.Value, 
            Color=lambda df: df.Variable, 
            Facet_row=lambda df: df.Variable.map(facet_row_map), 
        )
    )
    return(df_scatter)

def prepare_df_plotly_timeline(df):
    df_plotly = (
        df
        
        .melt(
            id_vars=None, 
            value_vars=None, 
            var_name='Variable', 
            value_name='Value', 
            col_level=None, 
            ignore_index=False, 
        )
        
         .assign(
            X_start=lambda df: pd.to_datetime(df.index.get_level_values('Date')), 
            X_end=lambda df: df.X_start + pd.DateOffset(days=1), 
            Y=lambda df: df.Value, 
            Color=lambda df: df.Variable, 
            Facet_row=lambda df: df.Variable, 
        )
    )
    return(df_plotly)

#
def get_chart_scatter(df, title):
   
    fig = (
        px.scatter(
            data_frame=df, 
            x='X', 
            y='Y', 

			color='Color', 
			text=None, 
			facet_row='Facet_row', 
			facet_col=None, 
            
			hover_name='Variable', 
			hover_data={col: col in ['X', 'Y'] for col in df.columns}, 

			category_orders={}, 
			labels={'X': 'Date', 'Y': 'Value'}, 

			color_discrete_sequence=None, 
			color_discrete_map=color_map, 

            trendline='rolling' if title!= 'Workout' else None, 
            trendline_options=dict(window=7, center=True, min_periods=1), 

			range_x=None, 
			range_y=None, 

			title=title, 
        )
    )
    return(fig)

def get_chart_area(df, title):
    
    fig = (
        px.area(
            data_frame=df[df.Value_type=='Value_roll'], 
			x='X', 
			y='Y', 

			#line_group='Line_group', 
			color='Color', 
			text=None, 
			facet_row='Facet_row', 
			facet_col=None, 

			hover_name='Variable', 
			hover_data={col: col in ['X', 'Y'] for col in df.columns}, 

			category_orders=None, 
			labels={'X': 'Date', 'Y': 'Value'}, 

			color_discrete_sequence=None, 
			color_discrete_map=color_map, 

			range_x=None, 
			range_y=None, 

			title=title, 
        )
    )
    return(fig)

def get_chart_timeline(df, title):

    fig = (
        px.timeline(
            data_frame=df, 
            x_start='X_start', 
            x_end='X_end', 
            y='Y', 

            color='Color', 
            text=None, 
            facet_row='Facet_row', 
            facet_col=None, 

            hover_name='Variable', 
            hover_data={col: col in ['X_start', 'Y'] for col in df.columns}, 

            category_orders={
                'Y': df_exercises.query('Pattern in @df.Y.unique()').Pattern.unique().tolist()+df_exercises.query('Progression in @df.Y.unique()').Progression.unique().tolist(), 
            }, 
            labels={'X_start': 'Date', 'Y': 'Value'}, 

            #color_discrete_sequence=None, 
            color_discrete_map=color_map, 

            #range_x=None, 
            #range_y=None, 
            
            title=title, 
        )
    )
    return(fig)

def get_chart(df_plot, chart_type, title):

    if chart_type=='Scatter':
        fig = get_chart_scatter(df_plot, title)
    #elif chart_type=='Area':
        #fig = get_chart_area(df_plot, title)
    elif chart_type=='Timeline':
        fig = get_chart_timeline(df_plot, title)
    else:
        fig = None

    fig = (
        fig
        .update_xaxes(
            tickangle=45, 
        )
        .update_yaxes(
            matches=None, 
            tickangle=-45, 
        )
        .for_each_annotation(
            lambda annotation: annotation.update(text=annotation.text.split('=')[1])
        )
        .update_layout(
            showlegend=False, 
        )
    )

    return(fig)

#
def get_chart_body_scatter(date_range, rolling_window):

    date_min, date_max = get_date_range(date_range)

    fig_body = (
        get_df_body(date_min, date_max)
        .pipe(prepare_df_plotly_scatter)
        .pipe(get_chart, 'Scatter', 'Body')
    )

    return(fig_body)

def get_chart_nutrition_scatter(level, genre, date_range, rolling_window):

    level = 'Date'

    date_min, date_max = get_date_range(date_range)

    fig_nutrition = (
        get_df_nutrition(level, genre, date_min, date_max)
        .drop('Quantity', axis=1)
        .pipe(prepare_df_plotly_scatter)
        .pipe(get_chart, 'Scatter', 'Nutrition')
    )

    return(fig_nutrition)

def get_chart_workout_scatter(resistance, pattern, date_range):

    date_min, date_max = get_date_range(date_range)
    
    fig_workout = (
        get_df_workout(date_min, date_max)
        
        .loc[lambda df: 
            (df.Resistance == resistance) 
            & 
            (df.Pattern == pattern)
        ]
        [['Progression', 'Rests', 'Weights', 'Reps']]

        .assign(
            Reps=lambda df: df.Reps.str.split('-'), 
            Nb_sets=lambda df: df.Reps.apply(len), 
        )
        .pipe(lambda df: (
            df
            .assign(**{
                'Reps_Set{}'.format(set+1): lambda df, set=set: df.Reps.apply(lambda l: l[set])
                for set in range(df.Nb_sets.max())
            })
        ))
        .drop(['Reps', 'Nb_sets'], axis=1)

        .pipe(prepare_df_plotly_scatter)
        .pipe(get_chart, 'Scatter', 'Workout')
    )

    return(fig_workout)

#
def get_chart_workout_timeline(date_range):

    date_min, date_max = get_date_range(date_range)
    
    fig_workout = (
        get_df_workout(date_min, date_max)
        [['Pattern']]
        .pipe(prepare_df_plotly_timeline)
        .pipe(get_chart, 'Timeline', 'Workout')
    )

    return(fig_workout)
