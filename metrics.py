'''
This file for calculating fashion metrics and plot charts.
'''
import json
from matplotlib import pyplot as plt
from constants import category_specific, share_pie_attri, season_abb, years

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()
fig4, ax4 = plt.subplots()
# section graph
fig6, ax6 = plt.subplots()
fig7, ax7 = plt.subplots()

def cal_metrics(year, season, category, brand, sub_category=False):
    '''
    这里的metrics为属性中各个子属性所占比例
    :param year:
    :param season:
    :param category:
    :param brand:
    :return:
    '''
    if season == 'ss':
        season = "springsummer"
    metrics = {}
    data_format = {}
    for b in brand:
        year_cal = year
        if b == 'givenchy' and year == '2022':
            year_cal = str(int(year) - 1)
        with open(
                'data/all_brand_data_2019_2023/' + b + '-' + season + '-' + year_cal +
                '-original/category_attribute_count.json', 'r') as file:
            json_string = file.read()
        data = json.loads(json_string)
        amount = 0
        with open(
                'data/all_brand_data_2019_2023/' + b + '-' + season + '-' + year_cal +
                '-original/category_count.json', 'r') as file2:
            json2 = file2.read()
        data2 = json.loads(json2)
        # convert to specific categories according to dictionary above
        if not sub_category:
            categories = category_specific[category]
            for item in categories:
                if item in data and item in data2:
                    data_format = merge_dictionaries(data[item], data_format)
                    amount += data2[item]
        else:
            if category in data and category in data2:
                data_format = merge_dictionaries(data[category], data_format)
                amount += data2[category]
        attributes = data_format.keys()
        for attribute in attributes:
            sub_metrics = dict()
            types = data_format[attribute].keys()
            for item in types:
                share = data_format[attribute][item] / amount
                sub_metrics[item] = share
            if sub_category and category == 'skirts' and attribute == 'length':
                sub_metrics['maxi/floor-length'] = sub_metrics.get('maxi', 0) + sub_metrics.get('floor-length', 0)
                sub_metrics.pop('maxi', 'no')
                sub_metrics.pop('floor-length', 'no')
                sub_metrics['mini/short'] = sub_metrics.get('mini', 0) + sub_metrics.get('short', 0)
                sub_metrics.pop('mini', 'no')
                sub_metrics.pop('short', 'no')

            # remove values that exist in length in silhouette, e.g, maxi, mini, midi
            if (category == 'skirts' or category == 'dresses') and attribute == 'silhouette':
                sub_metrics.pop('maxi', 'no')
                sub_metrics.pop('mini', 'no')
                sub_metrics.pop('short', 'no')
                sub_metrics.pop('midi', 'no')
            metrics[attribute] = sub_metrics
    return metrics


def cal_share(year, season, category, brand, sub_category=False):
    '''
    calculate the share for specific category in all selected brands

    If sub_category is TRUE, calculate specific categories share in large category,
    e.g, Blouses ard woven tops, knits and jersey tops share in Topweights
    :param year:
    :param season:
    :param category:
    :param brand:
    :param sub_category:
    :return:
    '''
    if not sub_category:
        overall_amount = 0
        amount = 0
        for b in brand:
            if b == 'givenchy' and year == '2022':
                continue
            with open(
                    'data/all_brand_data_2019_2023/' + b + '-' + season + '-' + year +
                    '-original/category_count.json', 'r') as file2:
                json2 = file2.read()
            data2 = json.loads(json2)
            # convert to specific categories according to dictionary above
            categories = category_specific[category]
            for key in data2.keys():
                overall_amount += data2.get(key, 0)

            for item in categories:
                amount += data2[item] if item in data2 else 0
        ratio = amount / overall_amount if overall_amount != 0 else 0
    else:
        overall_amount = 0
        amount = dict()
        ratio_dict = dict()
        for b in brand:
            if b == 'givenchy' and year == '2022':
                continue
            with open(
                    'data/all_brand_data_2019_2023/' + b + '-' + season + '-' + year +
                    '-original/category_count.json', 'r') as file2:
                json2 = file2.read()
            data2 = json.loads(json2)
            # convert to specific categories according to dictionary above
            categories = category_specific[category]
            for item in categories:
                overall_amount += data2.get(item, 0)
                amount[item] = data2.get(item, 0) + amount.get(item, 0)
        for item in category_specific[category]:
            ratio_dict[item] = amount[item] / overall_amount
        ratio = {"x": list(ratio_dict.values()), "y": list(ratio_dict.keys())}
    return ratio


def line_chart_all_category(season, year_cur, brand):
    ax4.clear()
    x_list = list()
    y_list = list()
    label_list = list()
    for category in list(category_specific.keys()):
        shares = list()
        x = list()
        for year in years:
            if int(year) > int(year_cur):
                break
            if brand == ['givenchy'] and year == '2022':
                # Take the average of 2021 and 2023, because lacking 2022
                share = (cal_share('2021', season, category, brand) + cal_share('2023', season, category, brand)) / 2
            else:
                share = cal_share(year, season, category, brand)
            shares.append(share)
            x.append(year)
        ax4.plot(x, shares, label=category)
        for a, b in zip(x, shares):
            ax4.text(a, b, round(b, 2), ha='center', va='bottom', fontsize=10)
        x_list.append(x)
        y_list.append(shares)
        label_list.append(category)
    ax4.legend(fontsize=10)
    chart_path = "data/charts/SS/line/all_category_" + '_'.join([year_cur, season, str(brand)]) + ".png"
    line_dict = {"type": "line", "x": x_list.pop(), "y": y_list, "label": label_list,
                 "title": "Change of Category Mix in 2019-" + year_cur}
    ax4.set_title("Change of Category Mix in 2019-" + year_cur)
    fig4.savefig(chart_path, transparent=True)
    # plt.show()
    return chart_path, line_dict


def pie_chart(year, season, category, brand, sub_category=False):
    '''
    :param year:
    :param season:
    :param category:
    :param brand:
    :return:
    '''
    ax1.clear()
    if sub_category:
        ratio = cal_share(year, season, category, brand, sub_category=True)
        pie_dict = {"type": "pie", "x": ratio["x"], "y": ratio["y"],
                    "title": "Mix of specific categories in " + category}
        ax1.pie(ratio["x"], labels=ratio["y"], autopct='%.2f%%')
        ax1.set_title("Mix of specific categories in " + category)
    else:
        ratio = dict()
        for cate in category_specific.keys():
            ratio[cate] = cal_share(year, season, cate, brand)
        # sub_ratio = cal_share(year, season, category, brand, sub_category=True)
        # for i, cate in enumerate(sub_ratio['y']):
        #     ratio[cate.capitalize()] = ratio.get(category, 0) * sub_ratio['x'][i]
        # ratio.pop(category, 'no')
        title = ' & '.join(category.split('&')) + " Mix"
        pie_dict = {'type': "pie", "x": list(ratio.values()), "y": list(ratio.keys()),
                    "title": title}
        ax1.pie(list(ratio.values()), labels=list(ratio.keys()), autopct='%.2f%%')
        ax1.set_title(title)
    chart_path = "data/charts/SS/pie/" + '_'.join([year, category, str(brand)]) + ".png"
    fig1.savefig(chart_path, transparent=True)
    return chart_path, pie_dict


def bar_char(metrics, year, season, category, brand, sub_metrics_name):
    ax2.clear()
    if int(year) > 2019:
        metrics_previous = cal_metrics(str(int(year) - 1), season, category, brand)
        sub_metrics_previous = metrics_previous.get(sub_metrics_name)
        minus_metrics = minus_dict(metrics, sub_metrics_previous)
        bar_dict = {"type": "bar", "x": list(minus_metrics.keys()), "y": list(minus_metrics.values()),
                    "title": sub_metrics_name.capitalize() + ' shifts YoY'}
        ax2.barh(list(minus_metrics.keys()), list(minus_metrics.values()), align='edge')
        for i, v in enumerate(list(minus_metrics.values())):
            ax2.text(v + 1, i, str(v), va='center', fontsize=3)
        bar_path = "data/charts/SS/bar/" + category + ".png"
        ax2.set_title(sub_metrics_name.capitalize() + ' shifts YoY')
        fig2.savefig(bar_path, transparent=True)
        return bar_path, bar_dict
    else:
        return None


def line_char(season, category, brand):
    ax3.clear()
    share = list()
    for year in years:
        share.append(cal_share(year, season, category, brand))
    ax3.plot(years, share)
    chart_path = "data/charts/SS/line/" + category + ".png"
    ax3.set_title("Change of " + category + " mix in 2019-2023")
    fig3.savefig(chart_path, transparent=True)
    return chart_path


def pie_chart_section(year, season, brand, category):
    pie_list = list()
    ax6.clear()
    ax7.clear()
    metrics1 = cal_metrics(str(int(year) - 1), season, category, brand, sub_category=True)
    data1 = metrics1[share_pie_attri[category]]
    metrics2 = cal_metrics(year, season, category, brand, sub_category=True)
    data2 = metrics2[share_pie_attri[category]]
    ax6.pie(list(data1.values()), labels=list(data1.keys()), autopct='%.2f%%')
    ax6_path = ("data/charts/SS/pie/" + '_'.join(
        [str(int(year) - 1), category, str(brand), share_pie_attri[category]]) + ".png")
    ax6.set_title(
        "Mix of " + ' '.join([share_pie_attri[category].capitalize(), season_abb[season], str(int(year) - 1)]))
    pie_list.append({"attribute": share_pie_attri[category], "season": season_abb[season], "year": str(int(year) - 1),
                     "type": "pie",
                     "x": list(data1.values()), "y": list(
            data1.keys()), "title": "Mix of " + ' '.join(
            [share_pie_attri[category].capitalize(), season_abb[season], str(int(year) - 1)])})
    fig6.savefig(ax6_path, transparent=True)
    ax7.pie(list(data2.values()), labels=list(data2.keys()), autopct='%.2f%%')
    ax7_path = "data/charts/SS/pie/" + '_'.join([year, category, str(brand), share_pie_attri[category]]) + ".png"
    ax7.set_title("Mix of " + ' '.join([share_pie_attri[category].capitalize(), season_abb[season], year]))
    pie_list.append(
        {"attribute": share_pie_attri[category], "season": season_abb[season], "year": year, "type": "pie",
         "x": list(data2.values()),
         "y": list(
             data2.keys()),
         "title": "Mix of " + ' '.join([share_pie_attri[category].capitalize(), season_abb[season], year])})
    fig7.savefig(ax7_path, transparent=True)
    return pie_list

def merge_dictionaries(dict1, dict2):
    merged_dict = {}
    # Combine keys from both dictionaries
    all_keys = set(dict1.keys()).union(set(dict2.keys()))

    for key1 in all_keys:
        merged_dict[key1] = {}
        # Combine keys from the second layer
        dict1_keys = dict1.get(key1, {})
        dict2_keys = dict2.get(key1, {})
        all_keys_layer2 = set(dict1_keys.keys()).union(set(dict2_keys.keys()))

        for key2 in all_keys_layer2:
            # Combine keys from the third layer and sum values if keys match
            value1 = dict1_keys.get(key2, 0)
            value2 = dict2_keys.get(key2, 0)
            merged_dict[key1][key2] = value1 + value2

    return merged_dict


def minus_dict(dict1, dict2):
    minus_dict = {}
    all_keys = set(dict1.keys()).union(set(dict2.keys()))
    for key in all_keys:
        minus_dict[key] = dict1.get(key, 0) - dict2.get(key, 0)
    return minus_dict
