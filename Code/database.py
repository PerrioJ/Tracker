from sqlalchemy import \
    create_engine, \
    MetaData, \
    Table, Column, \
    Date, String, Integer, Float, ForeignKey



#
engine = create_engine(
    'sqlite:///Data/database.db', 
)

metadata = MetaData(bind=engine)

# Body
BodyTracker = Table('BodyTracker', metadata, 
    Column('Date', Date, 
        primary_key=True), 
    Column('Weight', Float), 
    Column('Muscle_mass', Float), 
    Column('Fat_mass', Float), 
    Column('Water_mass', Float), 
    Column('Bone_mass', Float), 
)

# Nutrition
Meals = Table('Meals', metadata, 
    Column('Id', Integer, 
        primary_key=True), 
    Column('Meal', String), 
    Column('Order', Integer), 
)
Aliments = Table('Aliments', metadata, 
    Column('Id', String, 
        primary_key=True), 
    Column('Id_origin', String), 
    Column('Aliment', String), 
    Column('Brand', String), 
    Column('Calories_ref', Float), 
    Column('Proteins_ref', Float), 
    Column('Carbohydrates_ref', Float), 
    Column('Lipids_ref', Float), 
    Column('Alcohol_ref', Float), 
)
NutritionTracker = Table('NutritionTracker', metadata, 
    Column('Date', Date, 
        primary_key=True), 
    Column('Meal_id', Integer, ForeignKey(Meals.c.Id), 
        primary_key=True), 
    Column('Aliment_id', String, ForeignKey(Aliments.c.Id), 
        primary_key=True), 
    Column('Quantity', Float), 
)

# Workout
Exercises = Table('Exercises', metadata, 
    Column('Id', Integer, 
        primary_key=True, autoincrement='auto'), 
    #Column('Mechanic', String), # Coumpound vs Isolation vs Conditionning vs Cardio? vs Skill
    Column('Pattern', String), 
    Column('Resistance', String), 
    #Column('Variation', String), 
    Column('Progression', String, unique=True), 
    Column('Level', Integer), 
    Column('Order', Integer), 
)
WorkoutTracker = Table('WorkoutTracker', metadata, 
    Column('Date', Date, 
        primary_key=True), 
    #Column('Split', String, 
        #primary_key=True), 
    #Column('Attribute', String), 
    Column('Exercise_id', String, ForeignKey('Exercises.Id')), 
    Column('Rests', Float), 
    Column('Weights', Float), 
    Column('Reps', String), 
    Column('Order', Integer, 
        primary_key=True), 
)

#
metadata.create_all(engine)