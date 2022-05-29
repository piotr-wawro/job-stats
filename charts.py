#%%
import json
import numpy as np
import matplotlib.pyplot as plt
import requests
import random

# %%
# request = requests.get('https://justjoin.it/api/offers')

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
            if employment_type['salary'] == None:
                continue

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
for market in markets:
    plot_data = get_plot_data(market)
    print(f'Market: {market}'.ljust(30,'.'), end='')

    count = []
    for experience in experience_levels:
        count.append(len(plot_data[experience]['b2b']['avg2']))
        count.append(len(plot_data[experience]['permanent']['avg2']))
    print(f'{min(count)}')

# %%
stat_headers = []
stat_data: list[list[float]] = []

for market in ['net', 'java', 'javascript']:
    plot_data = get_plot_data(market)

    for experience in experience_levels:
        stat_headers.append(f'{market} {experience} b2b')
        random.shuffle(plot_data[experience]['b2b']['avg2'])
        stat_data.append(plot_data[experience]['b2b']['avg2'])

        stat_headers.append(f'{market} {experience} permanent')
        random.shuffle(plot_data[experience]['permanent']['avg2'])
        stat_data.append(plot_data[experience]['permanent']['avg2'])

stat_data_zip = zip(*stat_data)

with open('stat.txt', 'w') as file:
    file.write(';'.join(stat_headers))
    file.write('\n')
    for line in stat_data_zip:
        file.write(';'.join(str(x) for x in line))
        file.write('\n')

# %%
stat_headers = ['technology', 'experience', 'employment_types', 'salary']
stat_data: list[list[str|float]] = []

for market in ['net', 'java', 'javascript']:
    plot_data = get_plot_data(market)

    for experience in experience_levels:
        random.shuffle(plot_data[experience]['b2b']['avg2'])
        for salary in plot_data[experience]['b2b']['avg2']:
            stat_data.append([market, experience, 'b2b', salary])

        random.shuffle(plot_data[experience]['permanent']['avg2'])
        for salary in plot_data[experience]['permanent']['avg2']:
            stat_data.append([market, experience, 'permanent', salary])

with open('stat.txt', 'w') as file:
    file.write(';'.join(stat_headers))
    file.write('\n')
    for line in stat_data:
        file.write(';'.join(str(x) for x in line))
        file.write('\n')