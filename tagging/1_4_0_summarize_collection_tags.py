import json, os
import nltk
import pdb

import constants

current_dir = os.path.dirname(os.path.abspath(__file__))


# fix the capitalization and plural of words
# ignore those irrelevant categories
def find_collections(base):
    collection_list = []
    for root, ds, fs in os.walk(base):
        for d in ds:
            if "original" in d:
                collection_list.append(d)
        return collection_list


def count_category_attribute(target_collection, tag_file_path):
    file = open(tag_file_path + "tag_res_%s.txt" % target_collection).readlines()
    outfit_dict = {}
    for line in file:
        if "item" in line:
            item = line.rstrip("\n").split(":")[-1]
            outfit_dict[item] = {}
        if "category" in line:
            cate = line.split(";")[0].split(": ")[-1]

            attribute_list = line.rstrip("\n").split("; ")[1:]
            outfit_dict[item][cate] = attribute_list
    return outfit_dict


#### set the target collection before running ####
# source_image_path = "0_source_data/2019_2023_ss/"
# target_collections = find_collections(source_image_path)
tag_file_path = os.path.join(current_dir, "1_outfit_tagging_res_garment_level_grouped/")

# count category and attribute numbers
for target_collection in [constants.collections_title]:
    output_path = os.path.join(current_dir, "2_collection_res_grouped/%s/" % target_collection)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    category_count = {}
    category_attribute_count = {}
    outfit_dict = count_category_attribute(target_collection, tag_file_path)
    for outfit, garments in outfit_dict.items():
        for cate, attribute_list in garments.items():
            if cate not in category_count:
                category_count[cate] = 0
                category_attribute_count[cate] = {}
            category_count[cate] += 1

            for att_str in attribute_list:
                att, element_str = att_str.split(": ")
                elements = element_str.split(", ")
                if att not in category_attribute_count[cate]:
                    category_attribute_count[cate][att] = {}
                for element in elements:
                    if element not in category_attribute_count[cate][att]:
                        category_attribute_count[cate][att][element] = 0
                    category_attribute_count[cate][att][element] += 1

    f1 = open(output_path + "category_attribute_count.json", "w")
    json.dump(category_attribute_count, f1)
    f2 = open(output_path + "category_count.json", "w")
    json.dump(category_count, f2)
