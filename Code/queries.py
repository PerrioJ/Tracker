from database import \
    BodyTracker, \
    Meals, Aliments, NutritionTracker, \
    Exercises, WorkoutTracker

from sqlalchemy.sql import \
    select, exists, insert, update, delete, \
    func, and_, case, null, \
    literal



# Date
def get_query_date(date_min, date_max):
    
    query_date = (
        select([
            literal(date_min).label('Date'), 
        ])
        .cte(name='Date', recursive=True)
    )
    query_date = (
        query_date
        .union_all(
            select([
                func.Date(query_date.c.Date, '+1 day')
            ])
            .where(func.Date(query_date.c.Date, '+1 day') <= date_max)
        )
    )

    return(query_date)

# Body
def get_query_body(date_min, date_max):

    query_date = get_query_date(date_min, date_max)

    index_cols = [
        query_date.c.Date.label('Date'), 
    ]

    cols = [
        BodyTracker.c.Weight.label('Weight'), 
        BodyTracker.c.Muscle_mass.label('Muscle_mass'), 
        BodyTracker.c.Fat_mass.label('Fat_mass'), 
        BodyTracker.c.Water_mass.label('Water_mass'), 
        (BodyTracker.c.Bone_mass/BodyTracker.c.Weight).label('Bone_mass'), 
    ]

    query_body = (
        # SELECT
        select([
            *index_cols, 
            *cols, 
        ])
        # FROM
        .select_from(
            query_date
            # OUTER JOIN
            .outerjoin(
                BodyTracker, 
                # ON
                query_date.c.Date == BodyTracker.c.Date, 
            )
        )
        # WHERE
        .where(
            and_(query_date.c.Date >= date_min, query_date.c.Date <= date_max)
        )
        # ORDER BY
        .order_by(
            *index_cols, 
        )
    )

    return(query_body)

def get_query_last_body(date):

    query_last_body = (
        # SELECT
        select([
            func.last_value(column).over(order_by=BodyTracker.c.Date).label(column.name)
            for column in BodyTracker.columns if column.name!='Date'
        ])
        # FROM
        .select_from(
            BodyTracker
        )
        # WHERE
        .where(
            BodyTracker.c.Date<=date
        )
    )
    return(query_last_body)

# Nutrition
def get_query_meals():

    query_meals = (
        # SELECT
        select([
            Meals, 
        ])
        # FROM
        .select_from(
            Meals
        )
        # ORDER BY
        .order_by(
            Meals.c.Order, 
        )
    )
    return(query_meals)
"""def get_query_aliments():

    query_aliments = (
        # SELECT
        select([
            Aliments, 
        ])
        # FROM
        .select_from(
            Aliments
        )
    )
    return(query_aliments)"""
def get_query_nutrition(level, genre, date_min, date_max):

    query_date = get_query_date(date_min, date_max)

    index_cols = {
        'Date': [
            query_date.c.Date.label('Date'), 
        ], 
        'Meal': [
            query_date.c.Date.label('Date'), 
            Meals.c.Meal.label('Meal'), 
        ], 
        'Aliment': [
            query_date.c.Date.label('Date'), 
            Meals.c.Meal.label('Meal'), 
            Aliments.c.Aliment.label('Aliment'), 
        ], 
    }.get(level, [])

    none_sum = lambda expression: case([(func.Count(expression) == func.Count(), func.Sum(expression))], else_=null())
    raw_from_ref = lambda ref, quantity=NutritionTracker.c.Quantity, sum=none_sum: sum(ref * quantity/100)
    ref_from_ref = lambda ref, quantity=NutritionTracker.c.Quantity, sum=none_sum: sum(ref * quantity) / sum(quantity)
    cols = (
        [none_sum(NutritionTracker.c.Quantity).label('Quantity')]
        +
        {
            'Raw': [
                raw_from_ref(Aliments.c.Calories_ref).label('Calories'), 
                raw_from_ref(Aliments.c.Proteins_ref).label('Proteins'), 
                raw_from_ref(Aliments.c.Carbohydrates_ref).label('Carbohydrates'), 
                raw_from_ref(Aliments.c.Lipids_ref).label('Lipids'), 
                raw_from_ref(Aliments.c.Alcohol_ref).label('Alcohol'), 
            ], 
            'Reference': [
                ref_from_ref(Aliments.c.Calories_ref).label('Calories'), 
                ref_from_ref(Aliments.c.Proteins_ref).label('Proteins'), 
                ref_from_ref(Aliments.c.Carbohydrates_ref).label('Carbohydrates'), 
                ref_from_ref(Aliments.c.Lipids_ref).label('Lipids'), 
                ref_from_ref(Aliments.c.Alcohol_ref).label('Alcohol'), 
            ], 
            'Proportion': [
            ], 
        }.get(genre, [])
    )

    query_nutrition = (
        # SELECT
        select([
            *index_cols, 
            *cols, 
        ])
        # FROM
        .select_from(
            query_date
            # OUTER JOIN
            .outerjoin(
                NutritionTracker, 
                # ON
                query_date.c.Date == NutritionTracker.c.Date, 
            )
            # OUTER JOIN
            .outerjoin(
                Meals, 
                # ON
                NutritionTracker.c.Meal_id == Meals.c.Id, 
            )
            # OUTER JOIN
            .outerjoin(
                Aliments, 
                # ON
                NutritionTracker.c.Aliment_id == Aliments.c.Id, 
            )
        )
        # GROUP BY
        .group_by(
            *index_cols, 
        )
        # WHERE
        .where(
            and_(query_date.c.Date >= date_min, query_date.c.Date <= date_max)
        )
        # ORDER BY
        .order_by(
            #*index_cols, 
            query_date.c.Date, 
            Meals.c.Order, 
            Aliments.c.Aliment, 
        )
    )

    return(query_nutrition)

# Workout
def get_query_exercises():

    query_exercises = (
        # SELECT
        select([
            Exercises, 
        ])
        # FROM
        .select_from(
            Exercises
        )
        # ORDER BY
        .order_by(
            Exercises.c.Order, 
        )
    )
    return(query_exercises)
def get_query_workout(date_min, date_max):

    query_date = get_query_date(date_min, date_max)

    index_cols = [
        query_date.c.Date.label('Date'), 
    ]

    cols = [
        Exercises.c.Pattern.label('Pattern'), 
        Exercises.c.Resistance.label('Resistance'), 
        Exercises.c.Progression.label('Progression'), 
        #Exercises.c.Level.label('Level'), 

        WorkoutTracker.c.Rests.label('Rests'), 
        WorkoutTracker.c.Weights.label('Weights'), 
        WorkoutTracker.c.Reps.label('Reps'), 

        #WorkoutTracker.c.Order.label('Order'),     
    ]

    query_workout = (
        # SELECT
        select([
            *index_cols, 
            *cols, 
        ])
        # FROM
        .select_from(
            query_date
            # OUTER JOIN
            .outerjoin(
                WorkoutTracker, 
                # ON
                WorkoutTracker.c.Date==query_date.c.Date, 
            )
            # OUTER JOIN
            .outerjoin(
                Exercises, 
                # ON
                WorkoutTracker.c.Exercise_id==Exercises.c.Id
            )
        )
        # ORDER BY
        .order_by(
            query_date.c.Date, 
            WorkoutTracker.c.Order, 
        )
    )

    return(query_workout)

def get_query_last_workout(date):

    query_last_workout = (
        # SELECT
        select(
            [Exercises.c.Pattern, Exercises.c.Resistance]
            +
            [
                func.last_value(column).over(partition_by=[Exercises.c.Pattern, Exercises.c.Resistance], order_by=WorkoutTracker.c.Date).label(column.name)
                for column in [Exercises.c.Level, WorkoutTracker.c.Rests, WorkoutTracker.c.Weights, WorkoutTracker.c.Reps, WorkoutTracker.c.Order]
            ]
        )
        # FROM
        .select_from(
            WorkoutTracker
            # JOIN
            .join(
                Exercises, 
                # ON
                WorkoutTracker.c.Exercise_id==Exercises.c.Id
            )
        )
        # WHERE
        .where(
            WorkoutTracker.c.Date<=date
        )
        # ORDER BY
        .order_by(
            WorkoutTracker.c.Date
        )
    )
    return(query_last_workout)

# Edit
tables = {
    'BodyTracker': BodyTracker, 

    'Aliments': Aliments, 
    'NutritionTracker': NutritionTracker, 

    'Exercises': Exercises, 
    'WorkoutTracker': WorkoutTracker, 
}

def get_query_exists(table, row):
 
    table = tables[table]

    query_exists = (
        exists()
        .where(and_(*[col == row[col.name] for col in table.primary_key]))
        .select()
    )

    return(query_exists)

def get_query_insert(table, row):
    
    table = tables[table]

    query_insert = (
        insert(table)
        .values(**row)
    )

    return(query_insert)

def get_query_update(table, row):

    table = tables[table]

    query_update = (
        update(table)
        .where(and_(*[col == row[col.name] for col in table.primary_key]))
        .values(**row)
    )

    return(query_update)

def get_query_delete(table, row):
    
    table = tables[table]

    query_delete = (
        delete(table)
        .where(and_(*[col == row[col.name] for col in table.primary_key]))
    )

    return(query_delete)
