from openai import OpenAI
import pdb, json
import base64, requests


api_key = ""
client = OpenAI(api_key = api_key)


def get_one_data(wgsn_data, conf):

    for k, v in wgsn_data.items():
        if conf["name"] in k:
            for data in v:

                if data["overview"] == conf["overview"]:

                    return k, data

def get_one_data_category(wgsn_data, conf, category):
    '''
    If cannot find with specific cate, year, season, just use category
    :param wgsn_data:
    :param conf:
    :param category:
    :return:
    '''
    for k, v in wgsn_data.items():
        if category in k:
            for data in v:

                if data["overview"] == conf["overview"]:

                    return k, data

def get_report_slot_image_data(wgsn_data):
    report_slot_image = {}
    for one in wgsn_data:
        report_name= one["pdf_paths"]
        if report_name not in report_slot_image:
            report_slot_image[report_name] = []
        report_slot_image[report_name].append(one)
    return report_slot_image


def encode_image(image_path_list):
    enc_img_list = []
    for image_path in image_path_list:
        if image_path is not None:
            with open(image_path, "rb") as image_file:
                img = image_file.read()
                enc_img_list.append(
                        {"type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(img).decode('utf-8')}"}})
    return enc_img_list


def get_examples(wgsn_data, season_year, cate, conf):
    def get_data(wgsn_data, conf, cate):
        examples = {}
        for k, v in wgsn_data.items():
            if cate in k:
                examples[k] = []
                for data in v:
                    if data["overview"] is True:
                        examples[k].append(data)
        return examples

    examples = get_data(wgsn_data, conf, cate)
    valid_example_list = []
    for exa, exa_data in examples.items():
        if season_year in exa:
            continue
        valid_example_list.append(exa_data[0]["slots"][0])
    return valid_example_list


# conf = {}
# year = "23_24"
# cate = "Dresses___Skirts" #"Jackets___Coats" #
# season = "A_W"#"S_S"
# season_year = season + "_" + year
#
# conf["name"] = "_".join([cate, season, year])
# conf["overview"] = True
# wgsn_data = json.load(open("description_generation/wgsn_report_data/conf.json"))
# wgsn_report_slot_image = get_report_slot_image_data(wgsn_data)
# name, data = get_one_data(wgsn_report_slot_image, conf)
#
#
# slot = data["slots"]
# images = data["img_paths"]
# base64_image_list = encode_image(images)
#
#
# example_list = get_examples(wgsn_report_slot_image, season_year, cate)
# text_instruct = "You are given several charts describing the fashion status specifically for %s of %s. Each chart is about one specific aspect, e.g., fabric, sihloette. You are also given several examples of textual analysis based on charts as follows: %s. Try to generate several paragraphs (less than FIVE) in the format of an article. The length of the article should be around 250 characters. Do not use any key points or subtitles. "%(cate, "_".join([year, season]), ";".join(example_list))
#
# message = [
#             {"role": "system",
#              "content": "You are an analyst who's expertised in fashion. "
#              },
#             {"role": "user",
#              "content": [
#                   {
#                     "type": "text",
#                     "text": text_instruct
#                   }]
#              + base64_image_list
#              },
#             ]
#
# headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}"
#     }
#
# payload = {
#             "model": "gpt-4-vision-preview",
#             "messages": message,
#             "max_tokens": 1000
#         }
#
#
#
# response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
# results = response.json()["choices"][0]["message"]["content"]
# out_f = open("1_gen_description/%s_%s_%s.txt"%(cate, season, year), "a")
# out_f.write("\n -----------------------------------------------------------------------------------\n")
# out_f.write(results)
# out_f.close()