from openai import OpenAI
import yaml
import base64
import requests
import os
from datetime import datetime
import constants

current_dir = os.path.dirname(os.path.abspath(__file__))

api_key = yaml.safe_load(open(os.path.join(current_dir, "../key.yaml")))["api_key"]
prompt_lib = yaml.safe_load(open(os.path.join(current_dir, "./assistant_prompt.yaml")))
tagging_instruct = prompt_lib["V2"]["tagging_instruction_2"]

response_dict = {}
tagging_results = {}


def findallfile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            yield root.split("/")[-1], f


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        img = image_file.read()
        return base64.b64encode(img).decode('utf-8')


# Getting the base64 string

def tagging_collections(source_path, target_collections):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    tagging_res = {}
    cnt = 0
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("%s start tagging" % curr_time)
    for collection_name, image_name in findallfile(source_path):
        if collection_name not in target_collections or collection_name == "" or any(
                sub in image_name for sub in ['txt', 'json']):
            continue

        if collection_name not in tagging_res:
            tagging_res[collection_name] = {}

        image_path = source_path + collection_name + "/" + image_name
        base64_image = encode_image(image_path)
        payload = {
            "model": constants.GPT_MODEL,
            "messages": [
                {"role": "system",
                 "content": tagging_instruct},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }

        response = requests.post(f"{constants.gpt_base_url}/v1/chat/completions", headers=headers, json=payload)
        try:
            res = response.json()["choices"][0]["message"]["content"]
        except Exception:
            res = "Bad Request"
        tagging_res[collection_name][image_name] = res
        cnt += 1
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("%s %s images tagged, covering files %s" % (curr_time, cnt, " ".join(list(tagging_res.keys()))))

    return tagging_res


if __name__ == "__main__":
    # Step 1: tagging the images in the {target_collection}, stored in the {source_path} with the {tagging_instruct}
    # Path to your image
    tagging_results[constants.collections_title] = tagging_collections(constants.source_image_path,
                                                                       constants.collections_title)

    # Step 2: check about the tagging results saved in tagging_results[target_collection]
    for k, v in tagging_results[constants.collections_title].items():
        print(k)
        print(v)
        print("----------")

    # Step 3: save the tagging results tagging_results[target_collection] in the {save_file}

    for collection in [constants.collections_title]:  # tagging_results:
        save_file = os.path.join(current_dir, "1_outfit_tagging_res_garment_level/tag_res_%s.txt" % collection)
        if not os.path.exists(os.path.join(current_dir, "1_outfit_tagging_res_garment_level")):
            os.makedirs(os.path.join(current_dir, "1_outfit_tagging_res_garment_level"))
        f = open(save_file, "a")
        for i, tg in tagging_results[collection][collection].items():
            f.write("item:%s\n" % i)
            f.write(tg)
            f.write("\n\n")
        f.close()
