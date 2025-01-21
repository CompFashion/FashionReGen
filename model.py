import os
import random
import re

import datetime
import matplotlib.pyplot as plt

import constants
import existed_report
import llm_description
import gradio as gr
from constants import *
from metrics import cal_metrics, pie_chart, line_chart_all_category, pie_chart_section, minus_dict, bar_char

plt.rcParams['figure.figsize'] = [6.4, 4.8]  # [6.4, 4.8]

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

    # get section content
    section_description_list = list()
    section_dict = get_section_content(year, season, category, brand)
    for sub_cate in category_specific[category]:
        # get the generated section part charts from file
        section_fig = list()
        for attri in yoy_bar_attri[sub_cate]:
            section_fig.append("data/charts/SS/bar/" + "_".join([year, sub_cate, str(brand), attri]) + ".png")
        if sub_cate in share_pie_attri.keys():
            attri = share_pie_attri[sub_cate]
            section_fig.append(
                "data/charts/SS/pie/" + '_'.join([str(int(year) - 1), sub_cate, str(brand), attri]) + '.png')
            section_fig.append("data/charts/SS/pie/" + '_'.join([year, sub_cate, str(brand), attri]) + '.png')
        if GENERATED:
            # generate section description with llm
            section_description = section_description_gen(section_gpt_conf.get(sub_cate, sub_cate), year, season,
                                                          category, section_fig)
        else:
            section_description = 'to be generated'
        all_figure = all_figure + section_fig

        section_description_list.append({"section": sub_cate, "description": section_description})

    section_dict['description'] = section_description_list
    content, description, chart_path, line_path, img1, img2, img3, overview_dict = get_overview_content(year,
                                                                                                        season,
                                                                                                        category,
                                                                                                        brand,
                                                                                                        all_figure)

    # save to json file
    if not description.startswith('LLM api error: ') and GENERATED:
        existed_report.save_to_file(year, season, category, brand, generative_model, cover_img, content, description,
                                    chart_path, line_path, img1, img2, img3, all_figure[0], all_figure[1],
                                    all_figure[2], all_figure[3], section_description_list[0]['description'],
                                    all_figure[4], all_figure[5],
                                    all_figure[6], all_figure[7], section_description_list[1]['description'],
                                    overview_dict, section_dict)
    if description.startswith('LLM api error'):
        raise gr.Error(description[15:])

    return (cover_img, content, description, chart_path, line_path, img1, img2, img3, all_figure[0], all_figure[1],
            all_figure[2], all_figure[3], section_description_list[0]['description'],
            all_figure[4], all_figure[5],
            all_figure[6], all_figure[7], section_description_list[1]['description'], overview_dict, section_dict)


def get_overview_content(year, season, category, brand, all_figure):
    """
    The function that generate all contents in overview, including title, time, charts and description.
    :param year:
    :param season:
    :param category:
    :param brand:
    :param all_figure: contain already generated charts in the section part
    :return:
    """
    if season == 'springsummer':
        title = '# Catwalk Analytics: ' + category + ' S/S ' + year[-2:]
    else:
        title = '# Catwalk Analytics: ' + category + ' ' + season + ' ' + year[-2:]
    time = datetime.datetime.now().strftime('%d-%m-%Y')
    title += ' \n \n <br> <br> generated by: %s <br> ' % model_selection + time
    print(str(year) + str(season) + str(category) + str(brand))

    # generate charts, may have difference for different categories
    if category == 'Dresses&Skirts':
        pie_path, pie_dict = pie_chart(year, season, category, brand)
    else:
        pie_path, pie_dict = pie_chart(year, season, category, brand, sub_category=True)
    line_path, line_dict = line_chart_all_category(season, year, brand)

    if GENERATED:
        images = [pie_path, line_path] + all_figure
        description = description_gen(year, season, category, images)
        with open(os.path.join('gen_report/pre_correct', '%s_%s_%s_%s_%s.txt' % (
                year, season, category, str(brand), str(datetime.datetime.now()))), 'w', encoding='utf-8') as file:
            file.write(description)
        # auto-correction module
        # description = corrector.work_flow(description, category, images)
    else:
        description = 'to be generated'
    if description.startswith('LLM api error: '):
        raise gr.Error(description)

    img_path = search_img(year, season, category, brand)
    # random select k imgs
    img_ind = random.sample(range(len(img_path)), min(3, len(img_path)))
    if len(img_path) < 3:
        for i in range(len(img_path), 3):
            img_path.append("Lack related images")
        img1, img2, img3 = img_path[0], img_path[1], img_path[2]
    else:
        img1, img2, img3 = img_path[img_ind[0]], img_path[img_ind[1]], img_path[img_ind[2]]

    overview_dict = {"type": "overview", "data": [pie_dict, line_dict]}
    return title, description, pie_path, line_path, img1, img2, img3, overview_dict


def get_section_content(year, season, category, brand):
    cates = category_specific[category]
    dict_list = list()
    for cate in cates:
        cate_dict = {"category": cate.capitalize()}
        metrics = cal_metrics(year, season, cate, brand, sub_category=True)
        metrics_previous = cal_metrics(str(int(year) - 1), season, cate, brand, sub_category=True, previous=True)
        if metrics:
            dict_data = list()
            for item in yoy_bar_attri[cate]:
                if item not in metrics.keys() or item not in metrics_previous.keys():
                    continue
                data = minus_dict(metrics[item], metrics_previous[item])
                item_dict = bar_char(year, brand, item, cate, data)
                dict_data.append(item_dict)
            if cate in share_pie_attri.keys():
                pie_list = pie_chart_section(year, season, brand, cate)
                for item in pie_list:
                    dict_data.append(item)
            cate_dict["data"] = dict_data
            dict_list.append(cate_dict)

    section_dict = {"type": "section", "data": dict_list}
    return section_dict


def search_cover_img(year, season, brands):
    if not constants.CUSTOMIZED_DATA:
        directory_path = 'data/cover-image-all-brands/'
        file_names = os.listdir(directory_path)
        year_pattern = re.compile(year[-2:])
        if season == 'springsummer':
            season_pattern = re.compile('ss', re.IGNORECASE)
        brand_pattern = re.compile(brands[0], re.IGNORECASE)
        for file in file_names:
            if year_pattern.search(file) and season_pattern.search(file) and brand_pattern.search(file):
                return directory_path + file
    else:
        # randomly select cover img for customized data
        folder_path = os.path.join(constants.source_image_path, constants.collections_title)
        selected_image = random.choice(os.listdir(folder_path))
        return os.path.join(folder_path, selected_image)


def search_img(year, season, category, brands):
    '''
    initial catwalk images selection based on brand, year, season and category
    :param year:
    :param season:
    :param category:
    :param brands:
    :return:
    '''
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
                        item = item.split('item:')[1]
                        img_path.append(os.path.join(constants.source_image_path, constants.collections_title, item))
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
