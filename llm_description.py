from openai import OpenAI
import json
from description_generation import overview_analysis_gen, section_analysis_gen
import requests
import PIL.Image
import google.generativeai as genai


def description_gen_GPT(year_need, season_need, cate_need, images, api_key):
    client = OpenAI(api_key=api_key)

    conf = {}
    year = "23_24"
    cate_need_dic = {'Dresses&Skirts': "Dresses___Skirts", 'Jackets&Coats&Outerwear': 'Jackets___Coats',
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

    response = overview_analysis_gen.requests.post("https://api.openai.one/v1/chat/completions", headers=headers,
                                                   json=payload)
    try:
        results = response.json()["choices"][0]["message"]["content"]
    except KeyError:
        results = 'LLM api error: ' + str(response.json()['error'])
    return results


def description_gen_gemini(year_need, season_need, cate_need, images, api_key):
    model = genai.GenerativeModel('gemini-pro-vision')
    genai.configure(api_key=api_key)
    prompt = list()
    conf = {}
    year = "23_24"
    cate_need_dic = {'Dresses&Skirts': "Dresses___Skirts", 'Jackets&Coats&Outerwear': 'Jackets___Coats',
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

    example_list = overview_analysis_gen.get_examples(wgsn_report_slot_image, season_year, cate, conf)
    text_instruct = "You are given several charts describing the fashion status specifically for %s of %s. Each chart is about one specific aspect, e.g., fabric, sihloette. You are also given several examples of textual analysis based on charts as follows: %s. Try to generate several paragraphs (less than FIVE) in the format of an article. The length of the article should be around 250 characters. Do not use any key points or subtitles. " % (
        cate_need, "_".join([year_need, season_need]), ";".join(example_list))

    prompt.append(text_instruct)
    for image in images:
        prompt.append(PIL.Image.open(image))

    try:
        response = model.generate_content(prompt).text
    except Exception as e:
        response = 'LLM api error: ' + str(e)
    return response


def section_description_gen_GPT(sub_cate, year_need, season_need, cate_need, images, api_key):
    client = OpenAI(api_key=api_key)

    conf = {}
    year = "23"
    cate_need_dic = {'Dresses&Skirts': "Dresses___Skirts", 'Jackets&Coats&Outerwear': 'Jackets___Coats',
                     'Topweights': 'Topweights', 'Trousers&Shorts': 'Trousers__Shorts_Suits___Sets'}
    # cate = "Dresses___Skirts"  # "Jackets___Coats" #
    cate = cate_need_dic[cate_need]
    # sub_cate = "skirts"
    season = "A_W"  # "S_S"
    if sub_cate == "shorts" or sub_cate == 'trousers':
        season = "S_S"
    season_year = season + "_" + year
    conf["name"] = "_".join([cate, season, year])
    conf["overview"] = True
    wgsn_data = json.load(open("description_generation/wgsn_report_data/conf.json"))
    wgsn_report_slot_image = section_analysis_gen.get_report_slot_image_data(wgsn_data)
    name, data = section_analysis_gen.get_one_data(wgsn_report_slot_image, conf, sub_cate)

    slot = data["slots"]
    # images = data["img_paths"]

    example_list = section_analysis_gen.get_examples(wgsn_report_slot_image, season_year, cate, sub_cate, conf)

    base64_image_list = section_analysis_gen.encode_image(images)

    text_instruct = "You are given several charts describing the fashion status specifically for %s of %s. Each chart is about one specific aspect, e.g., fabric, sihloette. Try to generate a very short and neat piece of description (MUST less than 2 sentence) that can give an overview of the category or highlight the most significant trend in more general tone. Please DO NOT make it too specific on specific aspects. I will give you several examples for reference: [%s]. please try to get the tone and style of the descriptions and apply then in your generation. " % (
        sub_cate, "_".join([year, season]), ";;".join(example_list))

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

    response = requests.post("https://api.openai.one/v1/chat/completions", headers=headers, json=payload)
    try:
        results = response.json()["choices"][0]["message"]["content"]
    except KeyError:
        results = 'LLM api error: ' + str(response.json()['error'])
    return results


def section_description_gen_gemini(sub_cate, year_need, season_need, cate_need, images, api_key):
    model = genai.GenerativeModel('gemini-pro-vision')
    genai.configure(api_key=api_key)
    prompt = list()

    conf = {}
    year = "23"
    cate_need_dic = {'Dresses&Skirts': "Dresses___Skirts", 'Jackets&Coats&Outerwear': 'Jackets___Coats',
                     'Topweights': 'Topweights', 'Trousers&Shorts': 'Trousers__Shorts_Suits___Sets'}
    # cate = "Dresses___Skirts"  # "Jackets___Coats" #
    cate = cate_need_dic[cate_need]
    # sub_cate = "skirts"
    season = "A_W"  # "S_S"
    if sub_cate == "shorts" or sub_cate == 'trousers':
        season = "S_S"
    season_year = season + "_" + year
    conf["name"] = "_".join([cate, season, year])
    conf["overview"] = True
    wgsn_data = json.load(open("description_generation/wgsn_report_data/conf.json"))
    wgsn_report_slot_image = section_analysis_gen.get_report_slot_image_data(wgsn_data)
    name, data = section_analysis_gen.get_one_data(wgsn_report_slot_image, conf, sub_cate)

    slot = data["slots"]
    # images = data["img_paths"]

    example_list = section_analysis_gen.get_examples(wgsn_report_slot_image, season_year, cate, sub_cate, conf)

    text_instruct = "You are given several charts describing the fashion status specifically for %s of %s. Each chart is about one specific aspect, e.g., fabric, sihloette. Try to generate a very short and neat piece of description (MUST less than 2 sentence) that can give an overview of the category or highlight the most significant trend in more general tone. Please DO NOT make it too specific on specific aspects. I will give you several examples for reference: [%s]. please try to get the tone and style of the descriptions and apply then in your generation. " % (
        sub_cate, "_".join([year, season]), ";;".join(example_list))

    prompt.append(text_instruct)
    for image in images:
        prompt.append(PIL.Image.open(image))
    try:
        response = model.generate_content(prompt).text
    except Exception as e:
        response = 'LLM api error: ' + str(e)

    return response
