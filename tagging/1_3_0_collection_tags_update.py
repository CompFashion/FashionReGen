import os, json
import pdb
import constants

current_dir = os.path.dirname(os.path.abspath(__file__))

def find_collections(base):
    collection_list = []
    for root, ds, fs in os.walk(base):
        for d in fs:
            # if "original.txt" in d and "tag_res" in d:
            if "tag_res" in d:
                collection_list.append(d)
        return collection_list

    
def get_tag_group_map(group_tag_file):
    tag_group_map = {}
    for group, tag_list in group_tag_file.items():
        for tag in tag_list:
            tag_group_map[tag] = group
    return tag_group_map


def trans_word_group(word_groups):
    if len(word_groups) == 1:
        if "\\" in word_groups[0]:
            updated_word_groups = eval("".join(word_groups[0].split("\\")))
            new_updated_word_groups = {}
            for key, values in updated_word_groups.items():
                
                new_key = key.strip(", ")
                new_value_list = []
                for v in values:
                    new_value_list.append(v.strip(", "))
                new_updated_word_groups[new_key] = new_value_list
        updated_word_groups = new_updated_word_groups          
    else:   
        updated_word_groups = {}
        for line in word_groups:
            try:
                a = eval("{" + line + "}")
            except Exception:
                continue
            group = list(a.keys())[0]
            group_words = list(a.values())[0]
            updated_word_groups[group] = group_words
    return updated_word_groups

        
def get_one_tag_groups(group_data_path, target_category, target_aspect):
    try:
        group_tag_file = json.load(open(group_data_path + "%s_%s.dict"%(target_category, target_aspect), "r"))
    except Exception:
        try:
            group_tag_file = open(group_data_path + "%s_%s.dict"%(target_category, target_aspect), "r").readlines()
        except Exception:
            group_tag_file = None
    if type(group_tag_file) is list:
#         if target_category == "dresses" and target_aspect == "length":
#             pdb.set_trace()
        try:
            group_tag_file = trans_word_group(group_tag_file)
        except Exception:
            group_tag_file = None
    if group_tag_file is not None:
        tag_group_map = get_tag_group_map(group_tag_file)
    else:
        tag_group_map = None
        
    return tag_group_map


def get_all_tag_group(group_data_path):
    def get_all_dict(path):
        collection_list = []
        for root, ds, fs in os.walk(path):
            for d in fs:
                if "dict" in d:
                    collection_list.append(d)
        return collection_list
    
    all_tag_group = {}
    all_cate_aspect_list = get_all_dict(group_data_path)

    for all_cate_aspect in all_cate_aspect_list:
        cate, aspect = all_cate_aspect.split(".")[0].split("_")
        tag_troup_map = get_one_tag_groups(group_data_path, cate, aspect)
        if cate not in all_tag_group:
            all_tag_group[cate] = {}
        all_tag_group[cate][aspect] = tag_troup_map
    return all_tag_group
                      
def update_one_data(tag_group_dict, tag_str):
    new_tg_list = []
    tg_list = tag_str.split("; ")
    valid_cnt = 0
    nonvalid_cnt = 0
    for tg in tg_list:
        tg_key, tg_value = tg.split(": ")
        if tg_key == "category":
            cate = tg_value
            tag_group_maps = tag_group_dict[cate]
        else:
            tag_group_map = tag_group_maps[tg_key]
            if "," in tg_value:
                ele_list = tg_value.split(", ")
                new_ele_list = []
                for ele in ele_list:
                    try:
                        new_ele = tag_group_map[ele]
                        valid_cnt += 1
                    except Exception:
                        new_ele = ele
                        nonvalid_cnt += 1
                    if new_ele not in new_ele_list:
                        new_ele_list.append(new_ele)
                tg_value = ", ".join(new_ele_list)
            else:
                try:
                    tg_value = tag_group_map[tg_value]
                    valid_cnt += 1
                except Exception:
                    tg_value = tg_value
                    nonvalid_cnt += 1
        tg_str = tg_key + ": " + tg_value
        new_tg_list.append(tg_str)
    new_tag_str = "; ".join(new_tg_list) + "\n"
#     print("valid %d, nonvalid %d"%(valid_cnt, nonvalid_cnt))
    return new_tag_str
    
def update_collection_tags(target_collection, source_tag_path, new_tag_path, tag_group_dict):
    new_tag_dict = {}
    new_tag_dict[target_collection] = {}
    ori_tags = open(source_tag_path + target_collection).readlines()
    
    for line in ori_tags:
        if line.startswith("item"):
            item = line.rstrip("\n").split(":")[-1]
            new_tag_dict[target_collection][item] = {}
            att_str = ""
        elif line.startswith("category"):
            new_tag = update_one_data(tag_group_dict, line)
            att_str += new_tag
            new_tag_dict[target_collection][item] = att_str
        
        
    save_file = new_tag_path + target_collection
    f = open(save_file, "a")
    unvalid_items = []
    for i, tg in new_tag_dict[target_collection].items():
        f.write("item:%s\n"%i)
        if tg != {}:
            f.write(tg)
    f.close()
                      
        

if __name__ == "__main__":    
    source_tag_path = os.path.join(current_dir, "1_outfit_tagging_res_garment_level_refined/")
    new_tag_path = os.path.join(current_dir, "1_outfit_tagging_res_garment_level_grouped/")
    group_path = os.path.join(current_dir, "../data/grouped_tags/2019_2023_ss_all/")
    if not os.path.exists(new_tag_path):
        os.makedirs(new_tag_path)
    cate_aspect_tag_group = get_all_tag_group(group_path)
    target_collections = find_collections(source_tag_path)
    for collection in target_collections:
        update_collection_tags(collection, source_tag_path, new_tag_path, cate_aspect_tag_group)    
