import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

[tallies, numbers, tallies_u, numbers_u] = pickle.load(open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/rxnorm.pkl', 'rb'))
[tallies, numbers, tallies_u, numbers_u] = pickle.load(open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/procedure.pkl', 'rb'))
[tallies, numbers, tallies_u, numbers_u] = pickle.load(open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/medication.pkl', 'rb'))

vals, names, xs = [],[],[]
i = 0
for name, nums in numbers.items():
    vals.append(nums)
    names.append(name.replace(' ', ''))
    xs.append(np.random.normal(i + 1, 0.04, len(nums)))
    i += 1

plt.figure(figsize=(10,4), dpi=80)

sns.set_style("whitegrid")  # "white","dark","darkgrid","ticks"
boxprops = dict(linestyle='-', linewidth=1.5, color='#00145A')
flierprops = dict(marker='o', markersize=1,
                  linestyle='none')
whiskerprops = dict(color='#00145A')
capprops = dict(color='#00145A')
medianprops = dict(linewidth=1.5, linestyle='-', color='#01FBEE')

plt.boxplot(vals, labels=names, notch=False, boxprops=boxprops,
            whiskerprops=whiskerprops,capprops=capprops, flierprops=flierprops, medianprops=medianprops,showmeans=False)
plt.ylabel("Cost Quotient", fontweight='normal', fontsize=14)

palette = ['r', 'g', 'b', 'y', '#FF2709', '#09FF10', '#0030D7']
for x, val, c in zip(xs, vals, palette):
    plt.scatter(x, val, alpha=0.4, color=c)
plt.title('Medication Mention Price Comparison')
plt.show()