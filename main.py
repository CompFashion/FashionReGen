import os
import subprocess
import shutil

import yaml

import constants
from model import get_content


def tagging_customized_images():
    dest_path = "data/all_brand_data_2019_2023"
    if os.path.exists(os.path.join(dest_path, constants.collections_title, "category_attribute_count.json")):
        return
    # modify all configuration in constants.py before tagging
    files = ["tagging/1_0_tag.py", "tagging/1_1_tag_format_refining.py", "tagging/1_2_tag_word_grouping.py",
             "tagging/1_3_0_collection_tags_update.py", "tagging/1_3_tag_dict_updating.py",
             "tagging/1_4_0_summarize_collection_tags.py", "tagging/1_4_get_category_tags.py",
             "tagging/1_5_category_counting.py"]

    for file in files:
        print(f"Executing {file}...")
        subprocess.run(["python", file])
        print(f"{file} finished！")

    path = f"tagging/2_collection_res_grouped/{constants.collections_title}"
    if not os.path.exists(path):
        print(f"Tagging file does not exist: {path}")
        return

    if os.path.exists(os.path.join(dest_path, constants.collections_title)):
        os.rmdir(os.path.join(dest_path, constants.collections_title))
    shutil.move(path, dest_path)
    dest_path2 = "data/refined_tag_files"
    if not os.path.exists(dest_path2):
        os.makedirs(dest_path2)
    shutil.move(f"tagging/1_outfit_tagging_res_garment_level_refined/tag_res_{constants.collections_title}.txt", dest_path2)


def generate_report(year, season, category, brand):
    api_key = yaml.safe_load(open("key.yaml"))["api_key"]
    data = get_content(year, season, category, brand, True, 'GPT', api_key)
    print(data)


if __name__ == "__main__":
    tagging_customized_images()
    # manually set the metadata of customized data or use the default data
    # ['Spring/Summer (S/S)', 'Autumn/Winter (A/W)']
    # ['Dresses&Skirts', 'Jackets&Coats&Outerwear', 'Topweights', 'Trousers&Shorts']
    # ['chanel', 'christian-dior', 'givenchy', 'louis-vuitton', 'saint-laurent', 'valentino']
    generate_report('2024', 'Spring/Summer (S/S)', 'Dresses&Skirts', ['valentino'])