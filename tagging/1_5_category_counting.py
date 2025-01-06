import json, os
import constants

current_dir = os.path.dirname(os.path.abspath(__file__))

def find_collections(base, collection_req = None):
    collection_list = []
    for root, ds, fs in os.walk(base):
        if collection_req is None:
            return ds
        for d in ds:
            if collection_req in d:
                collection_list.append(d)
        return collection_list 
    
def get_category_distribution(target_collections, save_path, collection_title):
    cate_count = {}
    for collection in target_collections: 
        file = open(save_path + "tag_res_%s.txt"%collection).readlines()
        for line in file:
            line = line.lstrip("<").rstrip(" .>")
            if line.startswith("Category") or line.startswith("category"):
                cate = line.split("; ")[0].split(": ")[-1]
                if cate not in cate_count:
                    cate_count[cate] = 0
                cate_count[cate] += 1

    json.dump(cate_count, open(save_path + "grouped_tags/%s/cate_count.json"%collection_title, "w"))
    
    
if __name__ == "__main__":
    save_path = os.path.join(current_dir, "1_outfit_tagging_res_garment_level_refined/")# or "1_outfit_tagging_res_garment_level/"
    target_collections = find_collections(constants.source_image_path, constants.collections_title)
    get_category_distribution(target_collections, save_path, constants.collections_title)