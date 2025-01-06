import json, os
import constants

current_dir = os.path.dirname(os.path.abspath(__file__))

grouped_tag_path = os.path.join(current_dir, "1_outfit_tagging_res_garment_level_refined/grouped_tags/")
# collections_title = "2023" # "2019_2023_ss_all"
collection_data_path = grouped_tag_path + constants.collections_title + "/"
all_tags = json.load(open(collection_data_path + "1_cate_att_tag_grouped_counts.json"))
if not os.path.exists(collection_data_path + "1_cate_tags/"):
    os.makedirs(collection_data_path + "1_cate_tags/")
    
for cate, tags in all_tags.items():
    json.dump(tags, open(collection_data_path + "1_cate_tags/%s.json"%cate, "w"))
    