import json, datetime, os


def check_exist_repost(year, season, category, brand, generative_model):
    if season == 'Spring/Summer (S/S)':
        season = 'springsummer'
    file_direct = 'gen_report/' + generative_model + '/'
    brand.sort()
    search_name = '_'.join([year, season, category, str(brand), generative_model])
    file_names = os.listdir(file_direct)
    for file in file_names:
        if search_name in file:
            # data = load_file(year, season, category, brand, generative_model)
            # overview_dict = data['overview_dict']
            # section_dict = data['section_dict']
            return True
    return False

def return_exist_report(year, season, category, brand, generative_model):
    if season == 'Spring/Summer (S/S)':
        season = 'springsummer'
    if check_exist_repost(year, season, category, brand, generative_model):
        data = load_file(year, season, category, brand, generative_model)
        return (
            data['cover_img'], data['content'], data['description'], data['chart_path'], data['line_path'],
            data['img1'], data['img2'], data['img3'], data['section_fig1'], data['section_fig2'],
            data['section_fig3'], data['section_fig4'], data['section_description'], data['section_fig5'],
            data['section_fig6'], data['section_fig7'], data['section_fig8'], data['section_description2'],
            data['overview_dict'], data['section_dict'])

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
    brand.sort()
    with open("gen_report/" + generative_model + '/' + '_'.join(
            [year, season, category, str(brand), generative_model, str(datetime.datetime.now())]) + '.json',
              'w') as json_file:
        json.dump(data, json_file)


def load_file(year, season, category, brand, generative_model):
    file_direct = 'gen_report/' + generative_model + '/'
    brand.sort()
    search_name = '_'.join([year, season, category, str(brand), generative_model])
    file_names = os.listdir(file_direct)
    file_names.sort(reverse=True)
    for file in file_names:
        if search_name in file:
            with open(file_direct + file, 'r') as json_file:
                json_data = json_file.read()
            data = json.loads(json_data)
            return data
