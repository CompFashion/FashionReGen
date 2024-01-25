import json
import matplotlib.pyplot as plt
import re
import os
import random

class Result:
    def __init__(self, description):
        self.description = description


def get_content(year, season, category, brand):
    print(str(year) + str(season) + str(category) + str(brand))
    metrics = cal_metrics(year, season, category, brand)
    chart_path = pie_chart(metrics, year, season, category, brand)
    print(str(metrics))
    img_path = search_img(year, season, category, brand)
    # random select k imgs
    img_ind = random.sample(range(len(img_path)), 3)
    return chart_path, img_path[img_ind[0]], img_path[img_ind[1]], img_path[img_ind[2]]


def cal_metrics(year, season, category, brand):
    '''
    这里的metrics为属性中各个子属性所占比例
    :param year:
    :param season:
    :param category:
    :param brand:
    :return:
    '''
    metrics = dict()
    with open("data/2019_data/1_cate_tags/" + category + ".json", "r") as file:
        json_string = file.read()
    data = json.loads(json_string)
    attributes = data.keys()
    for attribute in attributes:
        sub_metrics = dict()
        types = data[attribute].keys()
        sum = 0
        for item in types:
            sum += data[attribute][item]
        for item in types:
            share = data[attribute][item] / sum
            sub_metrics[item] = share
        metrics[attribute] = sub_metrics
    return metrics


def pie_chart(metrics, year, season, category, brand):
    '''
    根据metrics里的share画饼图
    :param metrics:
    :param year:
    :param season:
    :param category:
    :param brand:
    :return:
    '''
    title = list(metrics.keys())[0]
    metrics = metrics[list(metrics.keys())[0]]
    plt.pie(metrics.values(), labels=metrics.keys(), autopct='%.2f%%')

    chart_path = "data/charts/pie/" + category + ".png"
    plt.title(title)
    plt.savefig(chart_path, transparent=True)
    return chart_path


def search_img(year, season, category, brands):
    directory_path = "data/refined_tag_files/"
    img_path = list()
    file_names = os.listdir(directory_path)
    if season == 'ss':
        season = "springsummer"
    for brand in brands:
        brand_pattern = re.compile(brand, re.IGNORECASE)
        year_pattern = re.compile(year)
        season_pattern = re.compile(season, re.IGNORECASE)
        for file in file_names:
            if brand_pattern.search(file) and year_pattern.search(file) and season_pattern.search(file):
                img_name = find_items_with_category(file, category, directory_path)
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