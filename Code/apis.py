import requests
import openfoodfacts

import pandas as pd

import re



# OpenFoodFacts
def get_aliment_from_openfoodfacts(aliment_id):
    
    product = openfoodfacts.products.get_product(aliment_id)
    status = bool(product['status'])
    
    if status:
        product = product['product']
        aliment = dict()
        
        aliment['Id'] = aliment_id
        aliment['Id_origin'] = 'OpenFoodFacts'
        aliment['Aliment'] = product.get('product_name')
        aliment['Brand'] = product.get('brands')
        
        #print(product.get('generic_name'))
        #print(product.get('categories'))
        #print(product.get('serving_size'))
        #print(product.get('categories_properties').get('ciqual_food_code:en'))
        
        aliment['Calories_ref'] = product.get('nutriments').get('energy-kcal_100g')
        aliment['Proteins_ref'] = product.get('nutriments').get('proteins_100g')
        aliment['Carbohydrates_ref'] = product.get('nutriments').get('carbohydrates_100g')
        aliment['Lipids_ref'] = product.get('nutriments').get('fat_100g')
        aliment['Alcohol_ref'] = product.get('nutriments').get('alcohol_100g', 0)
        #aliment['Fibers_ref'] = product.get('nutriments').get('fiber_100g')
        
    else:
        aliment = dict()
    
    return(status, aliment)

# Ciqual
df_ciqual = (
    pd.read_excel('Data/Table Ciqual 2020_FR_2020 07 07.xls')
    [[
        'alim_code', 'alim_nom_fr', 
        
        'Energie, N x facteur Jones, avec fibres  (kcal/100 g)', 
        'Protéines, N x facteur de Jones (g/100 g)', 
        'Glucides (g/100 g)', 
        'Lipides (g/100 g)', 
        'Alcool (g/100 g)', 
        #'Fibres alimentaires (g/100 g)', 
    ]]
    .assign(
        alim_code=lambda df: df.alim_code.astype(str), 
    )
    .set_index('alim_code')
    
    .mask(lambda df: df=='-')
    .mask(lambda df: df=='traces', 0)
    
    .replace('< ', '', regex=True)
    .replace(',', '.', regex=True)
    
    .set_index('alim_nom_fr', append=True)
    .astype('float', errors='ignore')
    .reset_index('alim_nom_fr')

    .assign(**{
        'Energie, N x facteur Jones, avec fibres  (kcal/100 g)': lambda df: df['Energie, N x facteur Jones, avec fibres  (kcal/100 g)'].fillna(4*df['Protéines, N x facteur de Jones (g/100 g)']+4*df['Glucides (g/100 g)']+9*df['Lipides (g/100 g)']+7*df['Alcool (g/100 g)']), 
    })
)

def get_aliment_from_ciqual(aliment_id):
    
    status = aliment_id in df_ciqual.index
    
    if status:
        product = df_ciqual.loc[aliment_id]
        aliment = dict()
                
        aliment['Id'] = aliment_id
        aliment['Id_origin'] = 'Ciqual'
        aliment['Aliment'] = product.get('alim_nom_fr')
        
        aliment['Calories_ref'] = product.get('Energie, N x facteur Jones, avec fibres  (kcal/100 g)')
        aliment['Proteins_ref'] = product.get('Protéines, N x facteur de Jones (g/100 g)')
        aliment['Carbohydrates_ref'] = product.get('Glucides (g/100 g)')
        aliment['Lipids_ref'] = product.get('Lipides (g/100 g)')
        aliment['Alcohol_ref'] = product.get('Alcool (g/100 g)')
        #aliment['Fibers_ref'] = product.get('Fibres alimentaires (g/100 g)')
        
    else:
        aliment = dict()
    
    return(status, aliment)

# FatSecret
"""fs = Fatsecret(
    consumer_key='816042664c54461e98a6142daca01784', 
    consumer_secret='192f7a0d915642f0a24a13ec040b0f9c', 
)

def get_aliment_from_nutritionix(aliment_id):
    
    product = (
        fs.food_get(
            food_id=aliment_id, 
        )
    )
    status = True
    
    if status:
        aliment = dict()
        
        aliment['Id'] = aliment_id
        aliment['Id_origin'] = 'FatSecret'
        aliment['Aliment'] = product.get('food_name')
        
        serving_size = float(product.get('servings').get('serving')[0].get('metric_serving_amount'))
        aliment['Calories_ref'] = float(product.get('servings').get('serving')[0].get('calories')) * 100/serving_size
        aliment['Proteins_ref'] = float(product.get('servings').get('serving')[0].get('protein')) * 100/serving_size
        aliment['Carbohydrates_ref'] = float(product.get('servings').get('serving')[0].get('carbohydrate')) * 100/serving_size
        aliment['Lipids_ref'] = float(product.get('servings').get('serving')[0].get('fat')) * 100/serving_size
        #aliment['Alcohol_ref'] = product.get('nf_alc')
        #aliment['Fibers_ref'] = product.get('nf_dietary_fiber')
        
    else:
        aliment = dict()
    
    return(status, aliment)"""

# Nutritionix
appId = '5abb275c'
appKey = 'f07fa95294d803103a53c122f13eac88'

def get_aliment_from_nutritionix(aliment_id):
    
    product = (
        requests.post(
            'https://trackapi.nutritionix.com/v2/natural/nutrients', 
            headers={
                'x-app-id': appId, 
                'x-app-key': appKey, 
            }, 
            data={
                'query': aliment_id, 
            }, 
        )
        .json()
        .get('foods')
        [0]
    )
    status = True
    
    if status:
        aliment = dict()
        
        aliment['Id'] = aliment_id
        aliment['Id_origin'] = 'Nutritionix'
        aliment['Aliment'] = product.get('food_name')
        
        aliment['Calories_ref'] = product.get('nf_calories') * 100/product.get('serving_weight_grams')
        aliment['Proteins_ref'] = product.get('nf_protein') * 100/product.get('serving_weight_grams')
        aliment['Carbohydrates_ref'] = product.get('nf_total_carbohydrate') * 100/product.get('serving_weight_grams')
        aliment['Lipids_ref'] = product.get('nf_total_fat') * 100/product.get('serving_weight_grams')
        aliment['Alcohol_ref'] = product.get('nf_alc')
        #aliment['Fibers_ref'] = product.get('nf_dietary_fiber')
        
    else:
        aliment = dict()
    
    return(status, aliment)

#
def get_aliment_from_aliment_id(aliment_id):
    
    if re.match(r'^(\d{4}-\d{4})|(\d-\d{6}-\d{6})$', aliment_id):
        status, aliment = get_aliment_from_openfoodfacts(aliment_id)
    elif aliment_id.isdigit():
        status, aliment = get_aliment_from_ciqual(aliment_id)
    elif True:
        status, aliment = get_aliment_from_nutritionix(aliment_id)
    else:
        status, aliment = False, dict()

    return(status, aliment)
