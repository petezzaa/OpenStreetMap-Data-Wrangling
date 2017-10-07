import sqlite3
from pprint import pprint
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
%pylab inline

conn = sqlite3.connect('hawaii_county.db')
c = conn.cursor()

QUERY = 'SELECT COUNT(*) \
         FROM node;'

number_of_nodes = c.execute(QUERY).fetchall()

print 'Number of Nodes:  {}'.format(number_of_nodes[0][0])

QUERY = 'SELECT COUNT(*) \
         FROM way;'

number_of_ways = c.execute(QUERY).fetchall()

print 'Number of Ways:  {}'.format(number_of_ways[0][0])

def barplot_two_colors(xvar, xvar2, yvar, yvar2, xlab, ylab, title, ticks):
    plt.bar(xvar, yvar)
    plt.bar(xvar2, yvar2, color = 'lightgreen')
    plt.xlabel(xlab)    
    plt.ylabel(ylab)
    plt.title(title)
    plt.xticks([xvar, xvar2], ticks)
    plt.show()

barplot_two_colors([0], [1], [number_of_nodes[0][0]], [number_of_ways[0][0]], '', '', 'Number of Nodes and Ways', ['Nodes', 'Ways'])

QUERY = 'SELECT COUNT(*) \
         FROM (SELECT * FROM node_tags UNION ALL SELECT * FROM way_tags) all_tags \
         WHERE all_tags.key == "tourism" and all_tags.value == "attraction";'

tourism = c.execute(QUERY).fetchall()

print ''
print 'Number of Tourism Attractions:  {}'.format(tourism[0][0])

QUERY = 'SELECT COUNT(*) \
         FROM (SELECT * FROM node_tags UNION ALL SELECT * FROM way_tags) all_tags \
         WHERE all_tags.key == "historic";'

historic = c.execute(QUERY).fetchall()

print ''
print 'Number of Historic Sites:  {}'.format(historic[0][0])

QUERY = 'SELECT COUNT(*) \
         FROM (SELECT * FROM node_tags UNION ALL SELECT * FROM way_tags) all_tags \
         WHERE all_tags.key == "natural" and all_tags.value == "beach";'

beaches = c.execute(QUERY).fetchall()

print ''
print 'Number of Beaches:  {}'.format(beaches[0][0])

QUERY = 'SELECT all_tags.value, COUNT(*) as num \
         FROM (SELECT * FROM node_tags UNION ALL SELECT * FROM way_tags) all_tags \
         WHERE all_tags.key == "postcode" \
         GROUP BY all_tags.value \
         ORDER BY num DESC'

zip_codes = pd.read_sql_query(QUERY, conn)
zip_codes.columns = ['Zip Code', 'Frequency']
zip_codes.index = np.arange(1, len(zip_codes) + 1)  #Reset index of dataframe to start at 1

print ''
print 'Frequency of Zip Codes'
print zip_codes

QUERY = 'SELECT COUNT(DISTINCT(nodes_and_ways.user)) \
         FROM (SELECT user FROM node UNION ALL SELECT user FROM way) nodes_and_ways;'

users = c.execute(QUERY).fetchall()

print ''
print 'Number of unique users:  {}'.format(users[0][0])

QUERY = 'SELECT nodes_and_ways.user as unq_user, COUNT(*) as num \
         FROM (SELECT user FROM node UNION ALL SELECT user FROM way) nodes_and_ways \
         GROUP BY unq_user \
         ORDER BY num DESC \
         LIMIT 10;'

top_users = pd.read_sql_query(QUERY, conn)
top_users.columns = ['User Name', 'Frequency']
top_users.index = np.arange(1, len(top_users) + 1)

print ''
print 'Top 10 Users'
print top_users

QUERY = 'SELECT value, COUNT(*) as num \
         FROM (SELECT * FROM node_tags UNION ALL SELECT * FROM way_tags) all_tags \
         WHERE all_tags.key == "amenity" \
         GROUP BY value \
         ORDER BY num DESC \
         LIMIT 10'

top_amenities = pd.read_sql_query(QUERY, conn)
top_amenities.columns = ['Amenity', 'Frequency']
top_amenities.index = np.arange(1, len(top_amenities) + 1)

print ''
print 'Top 10 Amenities'
print top_amenities

QUERY = 'SELECT value, COUNT(*) as num \
         FROM node_tags \
         WHERE node_tags.key == "cuisine" \
         GROUP BY value \
         ORDER BY num DESC \
         LIMIT 10'

top_cuisines = pd.read_sql_query(QUERY, conn)
top_cuisines.columns = ['Cuisine', 'Frequency']
top_cuisines.index = np.arange(1, len(top_cuisines) + 1)

print ''
print 'Top 10 Cuisines'
print top_cuisines

conn.close()