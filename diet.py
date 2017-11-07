"""
Diet LP problem
"""

from pulp import *

import pandas as pd

df = pd.read_excel('diet.xls', sheet_name='Sheet1')

"""
print(df.columns)

Index(['Foods', 'Price/ Serving', 'Serving Size', 'Calories', 'Cholesterol mg',
       'Total_Fat g', 'Sodium mg', 'Carbohydrates g', 'Dietary_Fiber g',
       'Protein g', 'Vit_A IU', 'Vit_C IU', 'Calcium mg', 'Iron mg'],
      dtype='object')

"""

foods = df['Foods'].values.tolist()[:64]

price = df['Price/ Serving'].values.tolist()[:64]

calories = df['Calories'].values.tolist()[:64]

cholesterol = df['Cholesterol mg'].values.tolist()[:64]

fat = df['Total_Fat g'].values.tolist()[:64]

sodium = df['Sodium mg'].values.tolist()[:64]

carbohydrates = df['Carbohydrates g'].values.tolist()[:64]

fiber = df['Dietary_Fiber g'].values.tolist()[:64]

protein = df['Protein g'].values.tolist()[:64]

vitamin_a = df['Vit_A IU'].values.tolist()[:64]

vitamin_c = df['Vit_C IU'].values.tolist()[:64]

calcium = df['Calcium mg'].values.tolist()[:64]

iron = df['Iron mg'].values.tolist()[:64]

#making dicts

price_dict = dict(zip(foods,price))

calories_dict = dict(zip(foods,calories))

cholesterol_dict = dict(zip(foods,cholesterol))

fat_dict = dict(zip(foods,fat))

sodium_dict = dict(zip(foods,sodium))

carbohydrates_dict = dict(zip(foods,carbohydrates))

fiber_dict = dict(zip(foods,fiber))

protein_dict = dict(zip(foods,protein))

vitamin_a_dict = dict(zip(foods,vitamin_a))

vitamin_c_dict = dict(zip(foods,vitamin_c))

calcium_dict = dict(zip(foods,calcium))

iron_dict = dict(zip(foods,iron))

#Defining the LP minimization problem

prob = LpProblem ("Diet problem", LpMinimize)

#Defining the decision variables

foods_dict = LpVariable.dict("Food quantity", foods, lowBound = 0)

select_dict = LpVariable.dict("Food selection", foods, 0,1, LpInteger)

#Defining the objective function

prob+= lpSum([price_dict[x] * foods_dict[x] for x in foods]),"Total cost of diet"

#Defining the constraints

prob+= lpSum([calories_dict[x] * foods_dict[x] for x in foods]) >=1500, "Calorie requirement"

prob+= lpSum([calories_dict[x] * foods_dict[x] for x in foods]) <=2500, "Calorie requirement 2"

prob+= lpSum([cholesterol_dict[x] * foods_dict[x] for x in foods]) >=30, "Cholesterol requirement"

prob+= lpSum([cholesterol_dict[x] * foods_dict[x] for x in foods]) <=240, "Cholesterol requirement 2"

prob+= lpSum([fat_dict[x] * foods_dict[x] for x in foods]) >=20, "Fat requirement"

prob+= lpSum([fat_dict[x] * foods_dict[x] for x in foods]) <=70, "Fat requirement 2"

prob+= lpSum([sodium_dict[x] * foods_dict[x] for x in foods]) >=800, "Sodium requirement"

prob+= lpSum([sodium_dict[x] * foods_dict[x] for x in foods]) <=2000, "Sodium requirement 2"

prob+= lpSum([carbohydrates_dict[x] * foods_dict[x] for x in foods]) >=130, "Carbohydrate requirement"

prob+= lpSum([carbohydrates_dict[x] * foods_dict[x] for x in foods]) <=450, "Carbohydrate requirement 2"

prob+= lpSum([fiber_dict[x] * foods_dict[x] for x in foods]) >=125, "Fiber requirement"

prob+= lpSum([fiber_dict[x] * foods_dict[x] for x in foods]) <=250, "Fiber requirement 2"

prob+= lpSum([protein_dict[x] * foods_dict[x] for x in foods]) >=60, "Protein requirement"

prob+= lpSum([protein_dict[x] * foods_dict[x] for x in foods]) <=100, "Protein requirement 2"

prob+= lpSum([vitamin_a_dict[x] * foods_dict[x] for x in foods]) >=1000, "Vitamin A requirement"

prob+= lpSum([vitamin_a_dict[x] * foods_dict[x] for x in foods]) <=10000, "Vitamin A requirement 2"

prob+= lpSum([vitamin_c_dict[x] * foods_dict[x] for x in foods]) >=400, "Vitamin C requirement"

prob+= lpSum([vitamin_c_dict[x] * foods_dict[x] for x in foods]) <=5000, "Vitamin C requirement 2"

prob+= lpSum([calcium_dict[x] * foods_dict[x] for x in foods]) >=700, "Calcium requirement"

prob+= lpSum([calcium_dict[x] * foods_dict[x] for x in foods]) <=1500, "Calcium requirement 2"

prob+= lpSum([iron_dict[x] * foods_dict[x] for x in foods]) >=10, "Iron requirement"

prob+= lpSum([iron_dict[x] * foods_dict[x] for x in foods]) <=40, "Iron requirement 2"

L = 1000000

for x in foods:
    prob += foods_dict[x] <= L* select_dict[x] + (1 - select_dict[x])*(1/L) #binding decision variables to binary decision variables
    prob+= foods_dict[x] >= 0.1* select_dict[x] #Minimum serving of 0.1 if a food is chosen

#At most celery or frozen broccoli can be choosen

prob+= select_dict['Frozen Broccoli'] + select_dict['Celery, Raw'] <= 1

#At least 3 kinds of meat/poultry/fish/eggs must be choosen

prob+= select_dict['Roasted Chicken'] + select_dict['Kielbasa,Prk'] + select_dict['Poached Eggs'] + select_dict['Scrambled Eggs'] + select_dict['Bologna,Turkey'] + select_dict['Frankfurter, Beef'] + select_dict['Ham,Sliced,Extralean']+ select_dict['Pork'] + select_dict['Sardines in Oil'] + select_dict['White Tuna in Water'] >= 3

#Solving the LP

prob.solve()

#printing out results

for var in foods_dict:
    var_value = foods_dict[var].varValue
    if var_value >0:
        print "The amount of {0} in diet is {1}".format(var, var_value)

total_cost = pulp.value(prob.objective)

print "The total cost is ${}".format(round(total_cost, 2))


"""
Output:

The amount of Popcorn,Air-Popped in diet is 13.214473
The amount of Oranges in diet is 3.0856009
The amount of Lettuce,Iceberg,Raw in diet is 82.673927
The amount of Celery, Raw in diet is 42.423026
The amount of Poached Eggs in diet is 0.1
The amount of Scrambled Eggs in diet is 0.1
The amount of Bologna,Turkey in diet is 0.1
The amount of Peanut Butter in diet is 1.9590978
The total cost is $4.51
"""


