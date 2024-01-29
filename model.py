import json
import matplotlib.pyplot as plt
import re
import os
import random

from openai import OpenAI

from description_generation import overview_analysis_gen

category_specific = {'Dress&Skirts': ['dresses', 'skirts'],
                     'Jackets&Coats&Outerwear': ['coats', 'jackets'],
                     'Topweights': ['blouses and woven tops', 'knits and jersey tops', 'shirts', 'tops', 'sweaters'],
                     'Trousers&Shorts': ['trousers', 'jumpsuits', 'shorts']}

years = ['2019', '2020', '2021', '2022', '2023']

fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()
fig3, ax3 = plt.subplots()


class Result:
    def __init__(self, description):
        self.description = description


def get_content(year, season, category, brand):
    # plt.clf()
    title = '# Catwalk Analytics: ' + ' '.join([category, season, ' '.join(brand)])
    print(str(year) + str(season) + str(category) + str(brand))
    metrics = cal_metrics(year, season, category, brand)
    sub_metrics_ind = random.randint(0, len(metrics.keys()) - 1)
    sub_metrics_name = list(metrics.keys())[sub_metrics_ind]
    sub_metrics = metrics.get(sub_metrics_name)
    chart_path = pie_chart(year, season, category, brand)
    print(str(metrics))
    bar_path = bar_char(sub_metrics, year, season, category, brand, sub_metrics_name)
    line_path = line_char(season, category, brand)
    img_path = search_img(year, season, category, brand)
    # random select k imgs
    img_ind = random.sample(range(len(img_path)), 3)
    description = description_gen(year, season, category, [chart_path, bar_path, line_path])
    categories = category_specific.get(category)
    return title, description, chart_path, bar_path, line_path, img_path[img_ind[0]], img_path[img_ind[1]], img_path[
        img_ind[2]]


def cal_metrics(year, season, category, brand):
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
        if b == 'givenchy' and year == '2022':
            continue
        with open(
                'data/all_brand_data_2019_2023/' + b + '-' + season + '-' + year +
                '-original/category_attribute_count.json', 'r') as file:
            json_string = file.read()
        data = json.loads(json_string)
        amount = 0
        with open(
                'data/all_brand_data_2019_2023/' + b + '-' + season + '-' + year +
                '-original/category_count.json', 'r') as file2:
            json2 = file2.read()
        data2 = json.loads(json2)
        # convert to specific categories according to dictionary above
        categories = category_specific[category]
        for item in categories:
            if item in data and item in data2:
                data_format = merge_dictionaries(data[item], data_format)
                amount += data2[item]

        attributes = data_format.keys()
        for attribute in attributes:
            sub_metrics = dict()
            types = data_format[attribute].keys()
            # sum = 0
            # for item in types:
            #     sum += data_format[attribute][item]
            for item in types:
                share = data_format[attribute][item] / amount
                sub_metrics[item] = share
            metrics[attribute] = sub_metrics
    return metrics


def cal_share(year, season, category, brand):
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
            overall_amount += data2[key]
        for item in categories:
            amount += data2[item] if item in data2 else 0
    ratio = amount / overall_amount
    return ratio


def pie_chart(year, season, category, brand):
    '''
    :param year:
    :param season:
    :param category:
    :param brand:
    :return:
    '''
    ax1.clear()
    ratio = cal_share(year, season, category, brand)
    ax1.pie([ratio, 1 - ratio], labels=[category, 'other category'], autopct='%.2f%%')
    chart_path = "data/charts/pie/" + category + ".png"
    ax1.set_title("Share of " + category)
    fig1.savefig(chart_path, transparent=True)
    return chart_path


def bar_char(metrics, year, season, category, brand, sub_metrics_name):
    ax2.clear()
    if int(year) > 2019:
        metrics_previous = cal_metrics(str(int(year) - 1), season, category, brand)
        sub_metrics_previous = metrics_previous.get(sub_metrics_name)
        minus_metrics = minus_dict(metrics, sub_metrics_previous)
        ax2.barh(list(minus_metrics.keys()), list(minus_metrics.values()), align='edge')
        for i, v in enumerate(list(minus_metrics.values())):
            ax2.text(v + 1, i, str(v), va='center', fontsize=3)
        bar_path = "data/charts/bar/" + category + ".png"
        ax2.set_title(sub_metrics_name + ' shifts YoY')
        fig2.savefig(bar_path, transparent=True)
        return bar_path
    else:
        return None


def line_char(season, category, brand):
    ax3.clear()
    share = list()
    for year in years:
        share.append(cal_share(year, season, category, brand))
    ax3.plot(years, share)
    chart_path = "data/charts/line/" + category + ".png"
    ax3.set_title("Change of " + category + " share in 2019-2023")
    fig3.savefig(chart_path, transparent=True)
    return chart_path


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
    api_key = ""
    client = OpenAI(api_key=api_key)

    conf = {}
    year = "23_24"
    cate_need_dic = {'Dress&Skirts': "Dresses___Skirts", 'Jackets&Coats&Outerwear': 'Jackets___Coats',
                     'Topweights': 'Topweights', 'Trousers&Shorts': 'Trousers__Shorts'}
    # cate = "Dresses___Skirts"  # "Jackets___Coats" #
    cate = cate_need_dic[cate_need]
    season = "A_W"  # "S_S"
    season_year = season + "_" + year

    conf["name"] = "_".join([cate, season, year])
    conf["overview"] = True
    wgsn_data = json.load(open("description_generation/wgsn_report_data/conf.json"))
    wgsn_report_slot_image = overview_analysis_gen.get_report_slot_image_data(wgsn_data)
    one_data = overview_analysis_gen.get_one_data(wgsn_report_slot_image, conf)
    if one_data is not None:
        name, data = one_data
    else:
        name, data = overview_analysis_gen.get_one_data_category(wgsn_report_slot_image, conf, cate)

    slot = data["slots"]
    # images = data["img_paths"]
    base64_image_list = overview_analysis_gen.encode_image(images)

    example_list = overview_analysis_gen.get_examples(wgsn_report_slot_image, season_year, cate, conf)
    text_instruct = "You are given several charts describing the fashion status specifically for %s of %s. Each chart is about one specific aspect, e.g., fabric, sihloette. You are also given several examples of textual analysis based on charts as follows: %s. Try to generate several paragraphs (less than FIVE) in the format of an article. The length of the article should be around 250 characters. Do not use any key points or subtitles. " % (
        cate_need, "_".join([year_need, season_need]), ";".join(example_list))

    message = [
        {"role": "system",
         "content": "You are an analyst who's expertised in fashion. "
         },
        {"role": "user",
         "content": [
                        {
                            "type": "text",
                            "text": text_instruct
                        }]
                    + base64_image_list
         },
    ]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": message,
        "max_tokens": 1000
    }

    response = overview_analysis_gen.requests.post("https://api.openai.com/v1/chat/completions", headers=headers,
                                                   json=payload)
    results = response.json()["choices"][0]["message"]["content"]
    return results
