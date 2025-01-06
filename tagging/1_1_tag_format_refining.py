import os
import nltk
import pdb
import yaml
import base64
import requests
import json
import constants

current_dir = os.path.dirname(os.path.abspath(__file__))


def is_plural(word):
    lemma = nltk.WordNetLemmatizer().lemmatize(word, 'n')
    plural = True if word is not lemma else False
    return plural


def find_collections(base):
    collection_list = []
    for root, ds, fs in os.walk(base):
        for d in ds:
            collection_list.append(d)
        return collection_list


def post_format_refine_and_find_unvalid(target_collection, source_path, save_path):
    ignore_cates = ["jewelry", "boots", "swimwear", "footwear", "intimates", "accessories", "belts", "gloves",
                    "lingeries", "scarfs", "bags", "shoes", "swimwears", "footwears", "sandals"]
    included_cates = ["dresses", "shorts", "jackets", "coats", "trousers", "blouses and woven tops",
                      "knits and jersey tops", "skirts", "sweaters", "shirts", "jumpsuits", "tops", "bouses"]
    file = open(source_path + "tag_res_%s.txt" % target_collection).readlines()

    new_tag_dict = {}
    new_tag_dict[target_collection] = {}
    for line in file:
        line = line.lstrip("<").rstrip(">")
        if line.startswith("item"):
            item = line.rstrip("\n").split(":")[-1]
            new_tag_dict[target_collection][item] = {}
            att_str = ""
        elif line.startswith("Category") or line.startswith("category"):
            new_tag = review_refine_item_tag_str_format(line.rstrip("\n")) + "\n\n"
            cate = new_tag.split("; ")[0].split(": ")[-1]

            if cate not in included_cates:
                att_str += "unvalid_cate"
                new_tag_dict[target_collection][item] = att_str
                continue
            att_str += new_tag
            new_tag_dict[target_collection][item] = att_str

        elif line == "\n":
            continue
        else:
            continue

    save_file = save_path + "tag_res_%s.txt" % target_collection
    f = open(save_file, "a")
    unvalid_items = []
    for i, tg in new_tag_dict[target_collection].items():

        if tg == {}:
            unvalid_items.append(i)
            print(i)
            continue

        if "unvalid_cate" in tg:
            #             pdb.set_trace()
            tg_list = tg.split("unvalid_cate")
            tg = "".join(tg_list)
        f.write("item:%s\n" % i)
        f.write(tg)
    f.close()
    return unvalid_items


def re_tag_unvalid_items_save(tagging_instruct, api_key, source_path, target_collection, item_list, source_tag_path):
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            img = image_file.read()
            return base64.b64encode(img).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    tagging_res = {}
    cnt = 0

    for item in item_list:
        image_path = source_path + target_collection + "/" + item
        base64_image = encode_image(image_path)
        payload = {
            "model": constants.GPT_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": tagging_instruct
                        },
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
        tagging_res[item] = res
        cnt += 1

    save_file = source_tag_path + "tag_res_%s.txt" % target_collection
    # save the re-tagged results in the original tagging file, in this case we don't need to re-tag it once when we first time review and refine
    f = open(save_file, "a")
    #     pdb.set_trace()
    for i, tg in tagging_res.items():
        if tg.lstrip("<").lower().startswith("category"):
            f.write("item:%s\n" % i)
            new_tg = review_refine_outfit_tag_str(tg)
            f.write(tg)
            f.write("\n\n")
    f.close()
    return tagging_res


def review_refine_item_tag_str_format(tag_str):
    # this tag_strs is outfit-level, which might contain multiple items connected by "\n\n"
    cate_map = json.load(open(os.path.join(current_dir, "cate_map.json")))
    es_tags = ["dress"]
    plural_target = ["category"]
    es_cates = ["dress"]
    item_tag_str_list = []
    tag_str = tag_str.lstrip("<").rstrip(">")
    tg_list = tag_str.split("; ")
    new_tg_list = []
    for tg in tg_list:
        try:
            tg_key, tg_value = tg.split(": ")
        except Exception:
            continue
            pdb.set_trace()
        tg_key = tg_key.strip(" ").lower()

        if tg_key == "category":
            if "(" in tg_value:
                tg_value = tg_value.split("(")[0].strip(" ")
            if tg_value in cate_map:
                tg_value = cate_map[tg_value]

        if "," in tg_value:
            ele_list = tg_value.split(",")
            new_ele_list = []
            for ele in ele_list:
                new_ele_list.append(ele.lower().strip())
            tg_value = ", ".join(new_ele_list)

        else:
            tg_value = tg_value.lower().strip()
            if tg_key in plural_target:
                if " " in tg_value:
                    pass
                #                     tg_value_list_new = []
                #                     tg_value_list = tg_value.split(" ")
                #                     for tg_v in tg_value_list:
                #                         tg_plural = is_plural(tg_v)
                #                         if not tg_plural:
                #                             if tg_v in es_tags:
                #                                 tg_v += "es"
                #                             else:
                #                                 tg_v += "s"
                #                         tg_value_list_new.append(tg_v)
                #                     pdb.set_trace()
                #                     tg_value = " ".join(tg_value_list_new)
                else:
                    tg_plural = is_plural(tg_value)
                    if not tg_plural:
                        if tg_value in es_tags:
                            tg_value += "es"
                        else:
                            tg_value += "s"
        tg_str = tg_key + ": " + tg_value
        new_tg_list.append(tg_str)
    new_tag_str = "; ".join(new_tg_list)

    return new_tag_str


def review_refine_outfit_tag_str(tag_strs):
    # this tag_strs is outfit-level, which might contain multiple items connected by "\n\n"

    item_tag_str_list = []
    split_str = "\n\n"
    if "\n" in tag_strs and "\n\n" not in tag_strs:
        split_str = "\n"

    for tag_str in tag_strs.split(split_str):
        new_tag_str = review_refine_item_tag_str_format(tag_str)
        item_tag_str_list.append(new_tag_str)

    return "\n\n".join(item_tag_str_list)


if __name__ == "__main__":

    # FUNCTIONS: 
    # 1. merge category name denoting same category with "cate_map.json"
    # 1. fix the capitalization and plural of words: making all word lower and nouns for category plural
    # 2. remove those uninterested categories such as swimwear, and others
    # 3. fix those non-standard data format such as the <>, unexpected spaces or others in the tags

    prompt_lib = yaml.safe_load(open(os.path.join(current_dir, "./assistant_prompt.yaml")))
    # source_image_path = "../data/2019-2023ss/"
    # target_collections = find_collections(constants.source_image_path)
    target_collections = constants.collections_title

    source_tag_path = os.path.join(current_dir,"1_outfit_tagging_res_garment_level/")
    new_tag_path = os.path.join(current_dir,"1_outfit_tagging_res_garment_level_refined/")

    if not os.path.exists(new_tag_path):
        os.makedirs(new_tag_path)

    tagging_instruct = prompt_lib["V2"]["tagging_instruction_2"]
    api_key = yaml.safe_load(open(os.path.join(current_dir,"../key.yaml")))["api_key"]

    for collection in [target_collections]:
        unvalid_items = post_format_refine_and_find_unvalid(collection, source_tag_path, new_tag_path)
        if len(unvalid_items) != 0:
            re_tag_unvalid_items_save(tagging_instruct, api_key, constants.source_image_path, collection, unvalid_items,
                                      source_tag_path)
