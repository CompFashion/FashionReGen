import json
import os
import random
import re

import datetime
import matplotlib.pyplot as plt

import existed_report
import llm_description
import gradio as gr

GPT_gen = False
# f = open(r'./key.yaml', encoding='utf-8')
# key_data = yaml.load(f.read(), Loader=yaml.FullLoader)
# api_key = key_data['api_key']
api_key = ''
model_selection = 'GPT'
plt.rcParams['figure.figsize'] = [6.4, 4.8]  # [6.4, 4.8]
category_specific = {'Dresses&Skirts': ['dresses', 'skirts'],
                     'Jackets&Coats&Outerwear': ['coats', 'jackets'],
                     'Topweights': ['blouses and woven tops', 'knits and jersey tops', 'sweaters'],
                     # , 'shirts', 'tops'
                     'Trousers&Shorts': ['trousers', 'shorts']}  # 'jumpsuits',
# For those do not have corresponding data in conf, using relevant subcategory
section_gpt_conf = {'knits and jersey tops': 'blouses and woven tops'}
# attributes needed in yoy calculation to make bar charts
yoy_bar_attri = {'dresses': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'skirts': ['silhouette', 'detail'],
                 'blouses and woven tops': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'knits and jersey tops': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'sweaters': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'trousers': ['silhouette', 'detail', 'print and pattern'],
                 'shorts': ['silhouette', 'detail'],
                 'jackets': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'coats': ['silhouette', 'detail', 'neckline', 'sleeve']}
share_pie_attri = {"skirts": "length", "coats": "length"}
years = ['2019', '2020', '2021', '2022', '2023']
all_brands = ['chanel', 'christian-dior', 'givenchy', 'louis-vuitton', 'saint-laurent', 'valentino']
season_abb = {"springsummer": "S/S"}

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()
fig4, ax4 = plt.subplots()
# section graph
fig6, ax6 = plt.subplots()
fig7, ax7 = plt.subplots()
fig8, ax8 = plt.subplots()


def get_content(year, season, category, brand, new_report, generative_model, api_key_user):
    brand.sort()
    if season == 'Spring/Summer (S/S)':
        season = 'springsummer'

    # return already generated report
    if not new_report and existed_report.check_exist_repost(year, season, category, brand, generative_model) == 'True':
        data = existed_report.load_file(year, season, category, brand, generative_model)
        return (
            data['cover_img'], data['content'], data['description'], data['chart_path'], data['line_path'],
            data['img1'], data['img2'], data['img3'], data['section_fig1'], data['section_fig2'],
            data['section_fig3'], data['section_fig4'], data['section_description'], data['section_fig5'],
            data['section_fig6'], data['section_fig7'], data['section_fig8'], data['section_description2'],
            data['overview_dict'], data['section_dict'])

    global api_key
    api_key = api_key_user
    all_figure = list()
    global model_selection
    model_selection = generative_model

    cover_img = search_cover_img(year, season, brand)
    section_description_list = list()
    if category == 'Dresses&Skirts' or category == 'Topweights':
        section_dict = get_section_content(year, season, category, brand)
        for sub_cate in category_specific[category]:
            if sub_cate != 'skirts':
                section_fig1 = "data/charts/SS/bar/" + '_'.join([year, sub_cate, str(brand)]) + "_silhouette.png"
                section_fig2 = "data/charts/SS/bar/" + '_'.join([year, sub_cate, str(brand)]) + "_detail.png"
                section_fig3 = "data/charts/SS/bar/" + '_'.join([year, sub_cate, str(brand)]) + "_neckline.png"
                section_fig4 = "data/charts/SS/bar/" + '_'.join([year, sub_cate, str(brand)]) + "_sleeve.png"
                if GPT_gen:
                    section_description = section_description_gen(section_gpt_conf.get(sub_cate, sub_cate), year,
                                                                  season,
                                                                  category,
                                                                  [section_fig1, section_fig2, section_fig3,
                                                                   section_fig4])
                    all_figure = all_figure + [section_fig1, section_fig2, section_fig3, section_fig4]
                else:
                    section_description = 'to be generated'
                section_description_list.append({"section": sub_cate, "description": section_description})
    else:
        section_fig1 = section_fig2 = section_fig3 = section_fig4 = section_description = section_fig5 = section_fig6 = \
            section_fig7 = section_fig8 = section_description2 = section_dict = None
        section_dict = get_section_content(year, season, category, brand)
        for sub_cate in category_specific[category]:
            section_fig = list()
            for attri in yoy_bar_attri[sub_cate]:
                section_fig.append("data/charts/SS/bar/" + "_".join([year, sub_cate, str(brand), attri]) + ".png")
            if sub_cate in share_pie_attri.keys():
                attri = share_pie_attri[sub_cate]
                section_fig.append(
                    "data/charts/SS/pie/" + '_'.join([str(int(year) - 1), sub_cate, str(brand), attri]) + '.png')
                section_fig.append("data/charts/SS/pie/" + '_'.join([year, sub_cate, str(brand), attri]) + '.png')
            if GPT_gen:
                section_description = section_description_gen(section_gpt_conf.get(sub_cate, sub_cate), year, season,
                                                              category, section_fig)
                all_figure = all_figure + section_fig
            else:
                section_description = 'to be generated'
            section_description_list.append({"section": sub_cate, "description": section_description})
    if category == 'Dresses&Skirts':
        section_fig5 = "data/charts/SS/bar/" + '_'.join([year, 'skirts', str(brand)]) + "_silhouette.png"
        section_fig6 = "data/charts/SS/bar/" + '_'.join([year, 'skirts', str(brand)]) + "_detail.png"
        section_fig7 = "data/charts/SS/pie/" + '_'.join(
            [str(int(year) - 1), 'skirts', str(brand), share_pie_attri['skirts']]) + ".png"
        section_fig8 = "data/charts/SS/pie/" + '_'.join(
            [year, 'skirts', str(brand), share_pie_attri['skirts']]) + ".png"
        if GPT_gen:
            section_description2 = section_description_gen('skirts', year, season, category,
                                                           [section_fig5, section_fig6, section_fig7, section_fig8])
            all_figure = all_figure + [section_fig5, section_fig6, section_fig7, section_fig8]
        else:
            section_description2 = 'to be generated'
        section_description_list.append({"section": "skirts", "description": section_description2})
    else:
        section_fig5 = section_fig6 = section_fig7 = section_fig8 = section_description2 = None
    section_dict['description'] = section_description_list
    content, description, chart_path, line_path, img1, img2, img3, overview_dict = get_overview_content(year,
                                                                                                        season,
                                                                                                        category,
                                                                                                        brand,
                                                                                                        all_figure)

    # save to json file
    if not description.startswith('LLM api error: ') and GPT_gen:
        existed_report.save_to_file(year, season, category, brand, generative_model, cover_img, content, description,
                                    chart_path, line_path, img1, img2, img3, section_fig1, section_fig2,
                                    section_fig3, section_fig4, section_description, section_fig5, section_fig6,
                                    section_fig7,
                                    section_fig8, section_description2, overview_dict, section_dict)
    else:
        raise gr.Error(description[15:])

    return (cover_img, content, description, chart_path, line_path, img1, img2, img3, section_fig1, section_fig2,
            section_fig3, section_fig4, section_description, section_fig5, section_fig6, section_fig7,
            section_fig8, section_description2, overview_dict, section_dict)


def get_overview_content(year, season, category, brand, all_figure):
    # plt.clf()
    # sub_cate = category.split('&')
    # cate_str = str()
    # for item in sub_cate:
    #     cate_str = cate_str + item
    if season == 'springsummer':
        title = '# Catwalk Analytics: ' + category + ' S/S ' + year[-2:]
    else:
        title = '# Catwalk Analytics: ' + category + ' ' + season + ' ' + year[-2:]
    time = datetime.datetime.now().strftime('%d-%m-%Y')
    title += ' \n \n <br> <br> generated by: %s <br> ' % model_selection + time
    print(str(year) + str(season) + str(category) + str(brand))
    metrics = cal_metrics(year, season, category, brand)
    sub_metrics_ind = random.randint(0, len(metrics.keys()) - 1)
    sub_metrics_name = list(metrics.keys())[sub_metrics_ind]
    sub_metrics = metrics.get(sub_metrics_name)
    if category == 'Dresses&Skirts':
        pie_path, pie_dict = pie_chart(year, season, category, brand)
    else:
        pie_path, pie_dict = pie_chart(year, season, category, brand, sub_category=True)
    # print(str(metrics))
    # bar_path, bar_dict = bar_char(sub_metrics, year, season, category, brand, sub_metrics_name)
    # if category == 'Dresses&Skirts':
    line_path, line_dict = line_chart_all_category(season, year, brand)
    # else:
    #     line_path, line_dict = charts_calculation.element_trend_plot(year, season, category, brand)
    img_path = search_img(year, season, category, brand)
    # random select k imgs
    img_ind = random.sample(range(len(img_path)), 3)
    if GPT_gen:

        description = description_gen(year, season, category, [pie_path, line_path] + all_figure)
    else:
        description = 'to be generated'
    if description.startswith('LLM api error: '):
        raise gr.Error(description[15:])
    categories = category_specific.get(category)
    overview_dict = {"type": "overview", "data": [pie_dict, line_dict]}
    return title, description, pie_path, line_path, img_path[img_ind[0]], img_path[img_ind[1]], img_path[
        img_ind[2]], overview_dict


def get_section_content(year, season, category, brand):
    cates = category_specific[category]
    dict_list = list()
    for cate in cates:
        cate_dict = {"category": cate.capitalize()}
        metrics = cal_metrics(year, season, cate, brand, sub_category=True)
        metrics_previous = cal_metrics(str(int(year) - 1), season, cate, brand, sub_category=True)
        if metrics:
            dict_data = list()
            for item in yoy_bar_attri[cate]:
                if item not in metrics.keys() or item not in metrics_previous.keys():
                    continue

                data = minus_dict(metrics[item], metrics_previous[item])
                x = list(data.keys())
                y = list(data.values())
                # Combine keys and values and sort by values
                sorted_data = sorted(zip(x, y), key=lambda item: item[1], reverse=False)
                x_sorted, y_sorted = zip(*sorted_data)
                if len(x_sorted) > 17:
                    # plt.rcParams['figure.figsize'] = [4.4, len(x_sorted)]
                    params = {'figure.figsize': [6.4, 0.3*len(x_sorted)]}
                    plt.rcParams.update(params)
                fig5, ax5 = plt.subplots()
                ax5.barh(x_sorted, y_sorted, align='edge')
                ax5_path = "data/charts/SS/bar/" + "_".join([year, cate, str(brand), item]) + ".png"
                ax5.set_title(item.capitalize() + " shift YoY")
                item_dict = {"attribute": item, "type": "bar", "x": x_sorted, "y": y_sorted,
                             "title": item.capitalize() + " shift YoY"}
                dict_data.append(item_dict)
                fig5.savefig(ax5_path, transparent=True)
                ax5.clear()
                params = {'figure.figsize': [6.4, 4.8]}
                plt.rcParams.update(params)
        if cate in share_pie_attri.keys():
            pie_list = pie_chart_section(year, season, brand, cate)
            for item in pie_list:
                dict_data.append(item)
        cate_dict["data"] = dict_data
        dict_list.append(cate_dict)

    section_dict = {"type": "section", "data": dict_list}
    return section_dict


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
            if brand == 'givenchy' and year == '2022':
                continue
            shares.append(cal_share(year, season, category, brand))
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
    plt.show()
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


def search_cover_img(year, season, brands):
    directory_path = 'data/cover-image-all-brands/'
    file_names = os.listdir(directory_path)
    year_pattern = re.compile(year[-2:])
    if season == 'springsummer':
        season_pattern = re.compile('ss', re.IGNORECASE)
    brand_pattern = re.compile(brands[0], re.IGNORECASE)
    for file in file_names:
        if year_pattern.search(file) and season_pattern.search(file) and brand_pattern.search(file):
            return directory_path + file


def search_img(year, season, category, brands):
    categories = category_specific[category]
    directory_path = "data/refined_tag_files/"
    img_path = list()
    file_names = os.listdir(directory_path)
    if season == 'ss':
        season = "springsummer"
    for cata in categories:
        for brand in brands:
            brand_pattern = re.compile(brand, re.IGNORECASE)
            year_pattern = re.compile(year)
            season_pattern = re.compile(season, re.IGNORECASE)
            for file in file_names:
                if brand_pattern.search(file) and year_pattern.search(file) and season_pattern.search(file):
                    img_name = find_items_with_category(file, cata, directory_path)
                    for item in img_name:
                        item = item[5:]
                        img_path.append('data/2019-2023ss/' + brand + '-' + season + '-' + year + '-original/' + item)
    return img_path


def find_items_with_category(filename, category, directory_path):
    with open(directory_path + filename, 'r') as file:
        lines = file.readlines()

    # Trim whitespace and newlines
    lines = [line.strip() for line in lines]

    # List to hold items that contain the category
    items_with_category = []

    # Find and store lines that contain the category
    for i, line in enumerate(lines):
        if 'item' in line.lower():
            item = line
        if category.lower() in line.lower():
            # Extract only the item part from the line
            items_with_category.append(item)

    return items_with_category


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


def description_gen(year_need, season_need, cate_need, images):
    if model_selection == 'GPT':
        return llm_description.description_gen_GPT(year_need, season_need, cate_need, images, api_key)
    elif model_selection == 'gemini':
        return llm_description.description_gen_gemini(year_need, season_need, cate_need, images, api_key)


def section_description_gen(sub_cate, year_need, season_need, cate_need, images):
    if model_selection == 'GPT':
        return llm_description.section_description_gen_GPT(sub_cate, year_need, season_need, cate_need, images, api_key)
    elif model_selection == 'gemini':
        return llm_description.section_description_gen_gemini(sub_cate, year_need, season_need, cate_need, images,
                                                              api_key)
