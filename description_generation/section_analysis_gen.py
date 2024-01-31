from openai import OpenAI
import pdb, json
import base64, requests




def get_one_data(wgsn_data, conf, sub_cate):
    for k, v in wgsn_data.items():
        if conf["name"] in k:
            for data in v:
                if data["overview"] != conf["overview"] and data["title"] == sub_cate:
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
        image_path = image_path
        with open(image_path, "rb") as image_file:
            img = image_file.read()
            enc_img_list.append(
                    {"type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(img).decode('utf-8')}"}})
    return enc_img_list


def get_examples(wgsn_data, season_year, cate, sub_cate, conf):
    
    def get_data(wgsn_data, conf, cate):
        examples = {}
        for k, v in wgsn_data.items():
            if cate in k:
                examples[k] = []
                for data in v:
                    if data["overview"] is False:
                        examples[k].append(data)
        return examples
        
    examples = get_data(wgsn_data, conf, cate)   
    valid_example_list = []
    for exa, exa_data in examples.items():
        sub_c= exa_data[0]["title"]
        if season_year in exa and sub_c == sub_cate:
            continue
        valid_example_list.append(exa_data[0]["slots"][0])
    return valid_example_list
       
        

# conf = {}
# year = "23_24"
# cate = "Dresses___Skirts"  #"Jackets___Coats" #
# sub_cate = "skirts"
# season = "A_W" #"S_S"
# season_year = season + "_" + year
# conf["name"] = "_".join([cate, season, year])
# conf["overview"] = True
# wgsn_data = json.load(open("../0_report_data/wgsn_report_data/conf.json"))
# wgsn_report_slot_image = get_report_slot_image_data(wgsn_data)
# name, data = get_one_data(wgsn_report_slot_image, conf, sub_cate)
#
# slot = data["slots"]
# images = data["img_paths"]
#
# example_list = get_examples(wgsn_report_slot_image, season_year, cate, sub_cate)
#
#
# base64_image_list = encode_image(images)
#
# text_instruct = "You are given several charts describing the fashion status specifically for %s of %s. Each chart is about one specific aspect, e.g., fabric, sihloette. Try to generate a very short and neat piece of description (MUST less than 2 sentence) that can give an overview of the category or highlight the most significant trend in more general tone. Please DO NOT make it too specific on specific aspects. I will give you several examples for reference: [%s]. please try to get the tone and style of the descriptions and apply then in your generation. "%(sub_cate, "_".join([year, season]), ";;".join(example_list))
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
# out_f = open("1_gen_section_description/%s_%s_%s_%s.txt"%(cate, sub_cate, season, year), "a")
# out_f.write("\n -----------------------------------------------------------------------------------\n")
# out_f.write(results)
# out_f.close()