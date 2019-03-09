# exploratory analysis of Eater NY "Restaurants to Try This Weekend"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mca

figpath = 'figures/'

data = pd.read_csv('data/recommendations.csv')

# visualize reviewer preferences with respect to cuisine type
recommender_cuisine_data = data[['name','recommender','cuisine']].pivot_table(index='recommender', columns='cuisine', values='name', aggfunc='count')
recommender_cuisine_data = recommender_cuisine_data.replace(np.nan,0) 
colors = ['#d16ba5', '#c777b9', '#ba83ca', '#aa8fd8', '#9a9ae1', '#8aa7ec', '#79b3f4', '#69bff8', '#52cffe', '#41dfff', '#46eefa', '#5ffbf1']
labels = recommender_cuisine_data.index
          
fig, ax = plt.subplots(figsize=(12,6))  

bottom = np.zeros(len(recommender_cuisine_data.columns))
for i in range(len(recommender_cuisine_data)):
    row = recommender_cuisine_data.iloc[i]
    row.plot.bar(x='cuisine',stacked=True,ax=ax,bottom=bottom,label=labels[i], color=colors[i])
    bottom += row.values

plt.legend(loc='upper right')
plt.savefig(figpath + 'recommender_cuisine.pdf')
    
# interpretation:
# italian, american, and cocktail bars are most frequently recommended.
# r. sietsema, s. tuder, k. kumari upadhyaya make up the majority of said recs.
# r.sietsema recommends plurality of less-"typical" cuisines (for americans).

# visualize proportion of recs given be each recommender for each cuisine type
# (clearly some recommenders (e.g. r.sietsema, s. tuder) give more total recs)
recommender_cuisine_prop_data = recommender_cuisine_data.div(recommender_cuisine_data.sum(axis=1),axis=0)

fig, ax = plt.subplots(figsize=(12,6))  

bottom = np.zeros(len(recommender_cuisine_prop_data.columns))
for i in range(len(recommender_cuisine_prop_data)):
    row = recommender_cuisine_prop_data.iloc[i]
    row.plot.bar(x='cuisine',stacked=True,ax=ax,bottom=bottom,label=labels[i], color=colors[i])
    bottom += row.values

plt.legend(loc='upper right')
plt.savefig(figpath + 'recommender_cuisine_prop.pdf')

# interpretation:
# r. sietsema and s. tuder both recommend italian most frequently, but this
# category does not dominate either of their recs.
# of most frequent recommender, k. kumari upadhyaya's recs are most focused:
# recommends cocktail bars ~ 25% of the time.
# other frequent recommender (e.g. s. dai, r.sietsema) give recs in roughly
# equal proportions across cuisine types.

# visualize reviewer preferences with respect to location (nyc neighborhood)
recommender_neighborhood_data = data[['name','recommender','neighborhood']].pivot_table(index='recommender', columns='neighborhood', values='name', aggfunc='count')
recommender_neighborhood_data = recommender_neighborhood_data.replace(np.nan,0) 

fig, ax = plt.subplots(figsize=(12,6))  

bottom = np.zeros(len(recommender_neighborhood_data.columns))
for i in range(len(recommender_neighborhood_data)):
    row = recommender_neighborhood_data.iloc[i]
    row.plot.bar(x='cuisine',stacked=True,ax=ax,bottom=bottom,label=labels[i], color=colors[i])
    bottom += row.values

plt.legend(loc='upper left')
plt.savefig(figpath + 'recommender_neighborhood.pdf')

# interpretation:
# restaurants in hip, young neighborhoods (greenwich village, les, w. village, 
# williamsburg) are most frequently recommended. (clearly this is endogenous.)
# r. sietsema recommends plurality of restaurants in less-"hip" outer boroughs.
# this is potentially related to r. sietsema's variety of cuisine recs (above).
# most frequent recommenders (somewhat) balance recs in manhattan and brooklyn,
# but k. kumari upadhyaya recommends almost exclusively in brooklyn.

# visualize proportion of recs given be each recommender for each neighborhood
recommender_neighborhood_prop_data = recommender_neighborhood_data.div(recommender_neighborhood_data.sum(axis=1),axis=0)

fig, ax = plt.subplots(figsize=(12,6))  

bottom = np.zeros(len(recommender_neighborhood_prop_data.columns))
for i in range(len(recommender_neighborhood_prop_data)):
    row = recommender_neighborhood_prop_data.iloc[i]
    row.plot.bar(x='cuisine',stacked=True,ax=ax,bottom=bottom,label=labels[i], color=colors[i])
    bottom += row.values

plt.legend(loc='upper right')
plt.savefig(figpath + 'recommender_neighborhood_prop.pdf')

# interpretation:
# most top recommenders don't seem to have strongly "preferred" neighborhoods.
# k. kumari upadhyaya is exception: 33% of recs are in crown heights.
# (but, can't say this is significantly greater than her second-greatest prop.)

# visualize reviewer preferences with respect to price
data.loc[data['price'] == '$','price'] = 'cheapest'
data.loc[data['price'] == '$$','price'] = 'lower-priced'
data.loc[data['price'] == '$$$','price'] = 'moderately-priced'
data.loc[data['price'] == '$$$$','price'] = 'most expensive'
recommender_price_data = data[['name','recommender','price']].pivot_table(index='recommender', columns='price', values='name', aggfunc='count')
recommender_price_data = recommender_price_data.replace(np.nan,0) 

fig, ax = plt.subplots(figsize=(12,6))  

bottom = np.zeros(len(recommender_price_data.columns))
for i in range(len(recommender_price_data)):
    row = recommender_price_data.iloc[i]
    row.plot.bar(x='cuisine',stacked=True,ax=ax,bottom=bottom,label=labels[i], color=colors[i])
    bottom += row.values

plt.legend(loc='upper left')
plt.savefig(figpath + 'recommender_price.pdf')

# interpretation:
# (unsurprisingly) lower-priced restaurants are most frequently recommended

# visualize proportion of recs given by each recommender in each price category
recommender_price_prop_data = recommender_price_data.div(recommender_price_data.sum(axis=1),axis=0)

fig, ax = plt.subplots(figsize=(12,6))  

bottom = np.zeros(len(recommender_price_prop_data.columns))
for i in range(len(recommender_price_prop_data)):
    row = recommender_price_prop_data.iloc[i]
    row.plot.bar(x='cuisine',stacked=True,ax=ax,bottom=bottom,label=labels[i], color=colors[i])
    bottom += row.values

plt.legend(loc='upper right')
plt.savefig(figpath + 'recommender_price_prop.pdf')

# interpretation:
# (also unsurprisingly) all of the most frequent recommenders give the vast
# majority of their recs in the lower-priced category.

# perform multiple correspondance analysis to visualize recs (row profiles)
# with respect to principal axes (orthogonal summary vectors, along which 
# majority of review heterogeneity lies).

cuisine_grouped = data.groupby('cuisine').name.count()
other_cuisines = list(cuisine_grouped[cuisine_grouped <= 3].index)
data.loc[data['cuisine'].isin(other_cuisines),'cuisine'] = 'other'

neighborhood_grouped = data.groupby('neighborhood').name.count()
other_neighborhoods = list(neighborhood_grouped[neighborhood_grouped <= 3].index)
data.loc[data['neighborhood'].isin(other_neighborhoods),'neighborhood'] = 'other'

varlist = ['cuisine','neighborhood','price'] 

# only analyze recs from the most frequent recommenders
top_recommenders = list(data.groupby('recommender').name.count().sort_values().index[-4:])

X = np.asmatrix(pd.get_dummies(data.loc[data['recommender'].isin(top_recommenders),varlist]).values)
mca_out = mca.mca(X)
F = mca_out[0]
G = mca_out[1]
s = mca_out[2]

# specify the coloring of the row profiles that we'll plot 
colors = ['#d16ba5', '#aa8fd8', '#79b3f4','#41dfff']
for i in range(len(top_recommenders)):
    data.loc[data['recommender'] == top_recommenders[i],'color_plot'] = colors[i]
color_vec = data.loc[data['recommender'].isin(top_recommenders), 'color_plot']

recommenders = data.loc[data['recommender'].isin(top_recommenders),'recommender'].values

# plot only row profiles (i.e. recommendations)
figname = 'top_recommenders'
mca.plot_mca(figpath,figname,F,color=True,color_vec=color_vec,legend=recommenders)

# interpretation: 
# k. kumari upadhyaya's recs are least disperse along the principal axes: i.e.
# her recs show the greatest level of within-recommender similarity.
# s. dai's recs are the most disperse along the principal axes: i.e. her recs
# show the lowest level of within-recommender similarity.
# in general, recs from the different recommenders are not particularly
# well-differentiated when projected onto the principal axes.












