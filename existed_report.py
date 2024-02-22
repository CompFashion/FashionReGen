import json, datetime, os


def check_exist_repost(year, season, category, brand, generative_model):
    if season == 'Spring/Summer (S/S)':
        season = 'springsummer'
    file_direct = 'gen_report/'
    search_name = '_'.join([year, season, category, str(brand), generative_model])
    file_names = os.listdir(file_direct)
    for file in file_names:
        if search_name in file:
            return 'True'
    return 'False'


def save_to_file(year, season, category, brand, generative_model, cover_img, content, description, chart_path,
                 line_path, img1, img2, img3, section_fig1, section_fig2,
                 section_fig3, section_fig4, section_description, section_fig5, section_fig6, section_fig7,
                 section_fig8, section_description2, overview_dict, section_dict):
    params = locals()
    data = dict()
    exclude_params = ['year', 'season', 'category', 'brand', 'generative_model']
    for param_name, param_value in params.items():
        if param_name not in exclude_params:
            data[param_name] = param_value
    with open("gen_report/" + '_'.join(
            [year, season, category, str(brand), generative_model, str(datetime.datetime.now())]) + '.json',
              'w') as json_file:
        json.dump(data, json_file)


def load_file(year, season, category, brand, generative_model):
    file_direct = 'gen_report/'
    search_name = '_'.join([year, season, category, str(brand), generative_model])
    file_names = os.listdir(file_direct)
    for file in file_names:
        if search_name in file:
            with open(file_direct + file, 'r') as json_file:
                json_data = json_file.read()
            data = json.loads(json_data)
            return data
