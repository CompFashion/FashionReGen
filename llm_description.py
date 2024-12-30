import json
from description_generation import overview_analysis_gen, section_analysis_gen
import requests
import PIL.Image
import google.generativeai as genai
from constants import gpt_base_url
from prompt import OVERVIEW_DESCRIPTION, DESCRIPTION_INSTRUCTION, SECTION_DESCRIPTION


def description_gen_GPT(year_need, season_need, cate_need, images, api_key):
    season = "S_S"
    year = "23_24"
    conf, wgsn_report_slot_image, data = generate_config_and_data(cate_need, season, year)

    base64_image_list = overview_analysis_gen.encode_image(images)

    example_list = overview_analysis_gen.get_examples(wgsn_report_slot_image, f"{season}_{year}", cate_need, conf)
    text_v3 = OVERVIEW_DESCRIPTION % (cate_need, "_".join([year_need, season_need]), ";".join(example_list))
    message = [
        {"role": "system",
         "content": DESCRIPTION_INSTRUCTION
         },
        {"role": "user",
         "content": [
                        {
                            "type": "text",
                            "text": text_v3
                        }]
                    + base64_image_list
         },
    ]

    headers, payload = create_headers_payload(api_key, message)
    response = requests.post(f"{gpt_base_url}/v1/chat/completions", headers=headers, json=payload, timeout=60)
    try:
        results = response.json()["choices"][0]["message"]["content"]
    except KeyError:
        results = 'LLM api error: ' + response.json()['error']['message']
    return results


def description_gen_gemini(year_need, season_need, cate_need, images, api_key):
    model = genai.GenerativeModel('gemini-pro-vision')
    genai.configure(api_key=api_key)

    season = "S_S"
    year = "23_24"
    conf, wgsn_report_slot_image, data = generate_config_and_data(cate_need, season, year)

    example_list = overview_analysis_gen.get_examples(wgsn_report_slot_image, f"{season}_{year}", cate_need, conf)
    text_instruct = OVERVIEW_DESCRIPTION % (cate_need, "_".join([year_need, season_need]), ";".join(example_list))

    prompt = [text_instruct] + [PIL.Image.open(image) for image in images]

    try:
        response = model.generate_content(prompt).text
    except Exception as e:
        response = f'LLM API error: {str(e)}'

    return response


def section_description_gen_GPT(sub_cate, year_need, season_need, cate_need, images, api_key):
    season = "S_S"
    year = "24"
    conf, wgsn_report_slot_image, data = generate_config_and_data(cate_need, season, year, sub_cate)

    example_list = section_analysis_gen.get_examples(wgsn_report_slot_image, f"{season}_{year}", cate_need, sub_cate,
                                                     conf)

    base64_image_list = section_analysis_gen.encode_image(images)

    text_instruct = SECTION_DESCRIPTION % (sub_cate, "_".join([year_need, season_need]), ";;".join(example_list))

    message = [
        {"role": "system",
         "content": DESCRIPTION_INSTRUCTION
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

    headers, payload = create_headers_payload(api_key, message)
    response = requests.post(f"{gpt_base_url}/v1/chat/completions", headers=headers, json=payload)
    try:
        results = response.json()["choices"][0]["message"]["content"]
    except KeyError:
        results = 'LLM api error: ' + response.json()['error']['message']
    return results


def section_description_gen_gemini(sub_cate, year_need, season_need, cate_need, images, api_key):
    model = genai.GenerativeModel('gemini-pro-vision')
    genai.configure(api_key=api_key)

    season = "S_S"
    year = "24"
    conf, wgsn_report_slot_image, data = generate_config_and_data(cate_need, season, year, sub_cate)

    example_list = section_analysis_gen.get_examples(wgsn_report_slot_image, f"{season}_{year}", cate_need, sub_cate,
                                                     conf)

    text_instruct = SECTION_DESCRIPTION % (sub_cate, "_".join([year_need, season_need]), ";;".join(example_list))

    prompt = [text_instruct] + [PIL.Image.open(image) for image in images]

    try:
        response = model.generate_content(prompt).text
    except Exception as e:
        response = f'LLM API error: {str(e)}'

    return response


def generate_config_and_data(cate_need, season, year, sub_cate=None):
    '''
    Helper function to generate configuration and data retrieval
    :param cate_need:
    :param season:
    :param year:
    :param sub_cate:
    :return:
    '''
    cate_need_dic = {
        'Dresses&Skirts': "Dresses___Skirts",
        'Jackets&Coats&Outerwear': 'Jackets___Coats',
        'Topweights': 'Topweights',
        'Trousers&Shorts': 'Trousers__Shorts',
        'Suits&Sets': 'Suits___Sets'
    }

    cate = cate_need_dic[cate_need]
    if cate == 'Trousers__Shorts_Suits___Sets' and sub_cate:
        year = "23"

    conf = {"name": "_".join([cate, season, year]), "overview": True}
    wgsn_data = json.load(open("description_generation/wgsn_report_data/conf.json"))
    wgsn_report_slot_image = overview_analysis_gen.get_report_slot_image_data(wgsn_data)

    if sub_cate:
        name, data = section_analysis_gen.get_one_data(wgsn_report_slot_image, conf, sub_cate)
    else:
        one_data = overview_analysis_gen.get_one_data(wgsn_report_slot_image, conf)
        if one_data is not None:
            name, data = one_data
        else:
            name, data = overview_analysis_gen.get_one_data_category(wgsn_report_slot_image, conf, cate)

    return conf, wgsn_report_slot_image, data


def create_headers_payload(api_key, message, max_tokens=1000):
    '''
    Helper function to create the API request header and payload
    :param api_key:
    :param message:
    :param max_tokens:
    :return:
    '''
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "messages": message,
        "max_tokens": max_tokens
    }
    return headers, payload
