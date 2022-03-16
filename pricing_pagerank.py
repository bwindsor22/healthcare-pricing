import networkx as nx
import pylab as plt
import pickle
import numpy as np
# [tallies, numbers, tallies_u, numbers_u] = pickle.load(open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/rxnorm.pkl', 'rb'))
# [tallies, numbers, tallies_u, numbers_u] = pickle.load(open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/procedure.pkl', 'rb'))
[tallies, numbers, tallies_u, numbers_u] = pickle.load(open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/medication.pkl', 'rb'))

tups = []
for key, values in numbers.items():
    vals_avg = np.mean(values) * np.log(len(values))
    kks = key.split(' / ')
    tups.append((kks[1], kks[0], vals_avg))

# Create blank graph
D=nx.DiGraph()

# Feed page link to graph
# D.add_weighted_edges_from([('A','B',1),('A','C',1),('C','A',1),('B','C',1)])
D.add_weighted_edges_from(tups)

# Print page rank for each pages
print (nx.pagerank(D))
nx.draw(D, with_labels=True)
plt.show()
