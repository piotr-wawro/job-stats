#%%
import json
import numpy as np
import matplotlib.pyplot as plt
import requests

# %%
request = requests.get('https://justjoin.it/api/offers')

if not request.ok:
    request.raise_for_status()

with open(file='offers.json', mode='w', encoding='utf8') as file:
    json.dump(request.json(), file, indent=2)

# %%
with open(file='offers.json', mode='r', encoding='utf8') as file:
    offers = json.load(file)

# %%
markets = {offer['marker_icon'] for offer in offers}
markets = sorted(list(markets))
print(markets)

# %%
experience_levels = {offer['experience_level'] for offer in offers}
experience_levels = sorted(list(experience_levels))
print(experience_levels)

# %%
employment_types = {
    employment_type['type'] \
    for offer           in offers \
    for employment_type in offer['employment_types']}
employment_types = sorted(list(employment_types))
print(employment_types)

# %%
def market_jobs(market: str):
    return [offer for offer in offers if \
            offer['marker_icon'] == market]

# %%
def prepare_data_structure():
    plot_data = {}
    for experience_level in experience_levels:
        plot_data[experience_level] = {}
        plot_data[experience_level]['all_jobs'] = 0
        plot_data[experience_level]['with_salary'] = 0
        plot_data[experience_level]['partial_salary'] = 0
        plot_data[experience_level]['no_salary'] = 0

        for employment_type in employment_types:
            plot_data[experience_level][employment_type] = {'min': [], 'max': [], 'avg': [], 'avg2': []}
    
    return plot_data

# %%
def get_plot_data(market: str):
    jobs_for_market = market_jobs(market)
    plot_data = prepare_data_structure()

    for job in jobs_for_market:
        experience = job['experience_level']
        plot_data[experience]['all_jobs'] += 1

        salary_included = [False if employment_type['salary'] == None else True \
                           for employment_type in job['employment_types']]

        if all(salary_included):
            plot_data[experience]['with_salary'] += 1
        elif any(salary_included):
            plot_data[experience]['partial_salary'] += 1
        else:
            plot_data[experience]['no_salary'] += 1
            continue

        for employment_type in job['employment_types']:
            type = employment_type['type']
            min_v = employment_type['salary']['from']
            max_v = employment_type['salary']['to']
            avg_v = (min_v + max_v)/2
            avg2_v = (min_v + avg_v)/2

            plot_data[experience][type]['min'].append(min_v)
            plot_data[experience][type]['max'].append(max_v)
            plot_data[experience][type]['avg'].append(avg_v)
            plot_data[experience][type]['avg2'].append(avg2_v)

    return plot_data

# %%
def plot_box(plot_data, employment_type, experience_level, data_type, position):
    plt.boxplot(x=[plot_data[experience_level][employment_type][data_type]],
                positions=      [position],
                boxprops=       {'color': 'g'},
                whiskerprops=   {'color': 'g'},
                capprops=       {'color': 'g'},
                medianprops=    {'color': 'm'},
                flierprops=     {'marker': '.', 
                                'markerfacecolor': 'g', 
                                'markeredgecolor': 'none'})

# %%
for market in markets:
    fig = plt.figure(figsize=(15,5))
    fig.suptitle(market)
    plot_data = get_plot_data(market)

    for idx1, employment_type in enumerate(employment_types):
        plt.subplot(1, len(employment_types), idx1+1)

        for idx2, experience_level in enumerate(experience_levels):
            plot_box(plot_data, employment_type, experience_level, 'avg2', idx2)

        plt.xticks(np.arange(0, len(experience_levels)), experience_levels)
        plt.minorticks_on()
        plt.grid(visible=True, which='both', axis='y')
        plt.title(employment_type)

    plt.show()
    plt.close()

# %%
