import pdb, json, os

import yaml

import constants

current_dir = os.path.dirname(os.path.abspath(__file__))


def find_collections(base, collection_req=None):
    collection_list = []
    for root, ds, fs in os.walk(base):
        if collection_req is None:
            return ds
        for d in ds:
            if collection_req in d:
                collection_list.append(d)
        return collection_list


def find_category_aspects(cate_att_tags, category):
    att_tags = cate_att_tags[category]
    aspects = att_tags.keys()
    return list(aspects)


def summary_words(target_collections, cate_att_tag_file):
    cate_att_tag_counts = {}
    for collection in target_collections:

        file = open(
            current_dir + "/1_outfit_tagging_res_garment_level_refined/" + "tag_res_%s.txt" % collection).readlines()

        for line in file:
            line = line.lstrip("<").rstrip(">. ")
            if line.startswith("Category") or line.startswith("category"):
                tag_str = line.rstrip("\n")
                tg_list = tag_str.split("; ")
                cate = tg_list[0].split(": ")[-1]
                if cate not in cate_att_tag_counts:
                    cate_att_tag_counts[cate] = {}
                for tg in tg_list[1:]:
                    try:
                        tg_key, tg_value = tg.split(": ")
                    except Exception:
                        continue
                    tg_value = tg_value.rstrip(".; ")
                    if tg_key not in cate_att_tag_counts[cate]:
                        cate_att_tag_counts[cate][tg_key] = {}
                    if "," in tg_value:
                        ele_list = tg_value.split(", ")
                        for ele in ele_list:
                            if ele not in cate_att_tag_counts[cate][tg_key]:
                                cate_att_tag_counts[cate][tg_key][ele] = 0
                            cate_att_tag_counts[cate][tg_key][ele] += 1
                    else:
                        if tg_value not in cate_att_tag_counts[cate][tg_key]:
                            cate_att_tag_counts[cate][tg_key][tg_value] = 0
                        cate_att_tag_counts[cate][tg_key][tg_value] += 1

    json.dump(cate_att_tag_counts, open(cate_att_tag_file, "w"))
    return cate_att_tag_counts


def find_non_group_words(corpus, word_groups):
    group_list = []
    non_grouped_words = []
    grouped_words = []

    if type(word_groups) is dict:
        for group, words in word_groups.items():
            group_list.append(group)
            for word in words:
                if word not in grouped_words and word in corpus:
                    grouped_words.append(word)
    else:
        for line in word_groups:
            try:
                a = eval("{" + line + "}")
            except Exception:
                continue
            try:
                group_list.append(list(a.keys())[0])
            except Exception:
                continue
            for word in list(a.values())[0]:
                if word in corpus and word not in grouped_words:
                    grouped_words.append(word)

    for word in corpus:
        if word not in grouped_words:
            non_grouped_words.append(word)
    return group_list, grouped_words, non_grouped_words


def combine_word_groups(new_word_groups, word_groups):
    if type(word_groups) is dict:
        updated_word_groups = word_groups
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

    for line in new_word_groups.split("\n"):
        try:
            a = eval("{" + line + "}")
        except Exception:
            continue
        try:
            group = list(a.keys())[0]
        except Exception:
            continue
        group_words = list(a.values())[0]
        if len(group_words) == 0:
            group_words.append(group)
        if group in updated_word_groups:
            updated_word_groups[group] += group_words
        else:
            updated_word_groups[group] = group_words

    return updated_word_groups


def trans_word_group(word_groups):
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


def group_words(all_tags, category, attribute, collections_path):
    print("starting grouping tags of %s %s for %s" % (category, attribute, collections_path.split("/")[-2]))
    from openai import OpenAI
    api_key = yaml.safe_load(open(os.path.join(current_dir, "../key.yaml")))["api_key"]
    corpus = list(all_tags[category][attribute].keys())
    group_tag_file = collections_path + "%s_%s.txt" % (category, attribute)

    if os.path.exists(group_tag_file):
        preliminary_word_groups = open(group_tag_file).readlines()

    else:
        client = OpenAI(api_key=api_key, base_url=constants.gpt_base_url)
        ## completions 1: grouping corpus >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        message_1 = [{"role": "system", "content": "You are an assistant to help group tagging corpus."},
                     {"role": "user",
                      "content": "can you group the corpus describing %s for %s. You are required to group similar words together and output a dictionary that map each word to the group." % (
                          attribute, category)},
                     {"role": "user", "content": "the corpus contains words as follows"},
                     {"role": "user", "content": ";".join(corpus)},
                     {"role": "user",
                      "content": "Make sure only words with almost the same meaning be grouped, NOT those describing same aspect at a large scale."},
                     {"role": "user",
                      "content": "Here is an example: 'draped': ['draped', 'draping', 'draped front', 'draped neckline', 'draped panel', 'draped shoulders', 'draped overlay', 'draped look']"},
                     {"role": "user",
                      "content": "Only output the word groups as a dictionary, DO NOT output other descriptive or explanatory text!!"}
                     ]

        completion_1 = client.chat.completions.create(
            model=constants.GPT_MODEL,
            messages=message_1
        )

        out_f = open(group_tag_file, "a")
        out_f.write(completion_1.choices[0].message.content)
        out_f.close()
        preliminary_word_groups = completion_1.choices[0].message.content.split("\n")
    group_list, grouped_words, non_grouped_words = find_non_group_words(corpus, preliminary_word_groups)
    word_groups = preliminary_word_groups
    group_cnt = 1
    print("grouping round: %d  group no.: %d  ttl tag words: %d  grouped words: %d  non-grouped words: %d" % (
        group_cnt, len(group_list), len(corpus), len(grouped_words), len(non_grouped_words)))

    while len(non_grouped_words) > 2:
        group_cnt += 1
        client = OpenAI(api_key=api_key, base_url=constants.gpt_base_url)
        ## completions 2: grouping corpus >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        message_2 = [{"role": "system", "content": "You are an assistant to help group tagging corpus."},
                     {"role": "user",
                      "content": "can you group the corpus describing %s for %s. You are required to group similar words together and output a dictionary that map each word to the group." % (
                          attribute, category)},
                     {"role": "user", "content": "the corpus contains words as follows"},
                     {"role": "user", "content": ";".join(non_grouped_words)},
                     {"role": "user",
                      "content": "Make sure only words with almost the same meaning be grouped, NOT those describing same aspect at a large scale."},
                     {"role": "user", "content": "Candidate word groups include %s" % ";".join(group_list)},
                     {"role": "user",
                      "content": "Check whether each word can be grouped into an existing group. If not, you can create new groups"},
                     {"role": "user",
                      "content": "Here is an example of the word group: 'draped': ['draped', 'draping', 'draped front', 'draped neckline', 'draped panel', 'draped shoulders', 'draped overlay', 'draped look']."},
                     {"role": "user",
                      "content": "REMMENBER: Only output the word groups as a dictionary covering the given corpus. Make word GROUP to be the key and the containing words to be the values. DO NOT cover other words into the groups or output other descriptive or explanatory text!!"}
                     ]

        completion_2 = client.chat.completions.create(
            model=constants.GPT_MODEL,
            messages=message_2
        )

        new_word_groups = completion_2.choices[0].message.content
        updated_word_groups = combine_word_groups(new_word_groups, word_groups)  # dictionary
        group_list, grouped_words, non_grouped_words = find_non_group_words(corpus, updated_word_groups)
        word_groups = updated_word_groups
        print("grouping round: %d  group no.: %d  ttl tag words: %d  grouped words: %d  non-grouped words: %d" % (
            group_cnt, len(group_list), len(corpus), len(grouped_words), len(non_grouped_words)))

    if group_cnt < 2:
        word_groups = trans_word_group(word_groups)
    final_group_tag_file = collections_path + "%s_%s.dict" % (category, attribute)
    json.dump(word_groups, open(final_group_tag_file, "a"))


if __name__ == "__main__":

    # FUNCTIONS:
    # 1. applying GPT to group tagging words for specific attribute corresponding to specific category
    # 2. adopting multi-step word grouping strategy relying on GPT to generating word grouping dictionaries
    # INPUT:  "0_cate_att_tag_counts.json" of specific collection
    # OUTPUT: a list of dictionary saved in the path of "collection_data_path". Each dictionary contains the word group and corresponding grouped words with similar meanings for a specific aspect(attribute) for a category

    grouped_tag_path = os.path.join(current_dir, "1_outfit_tagging_res_garment_level_refined/grouped_tags/")
    if not os.path.exists(grouped_tag_path):
        os.makedirs(grouped_tag_path)

        # We conduct tag grouping for all years of data and then use the grouping results for generating specific year of collections
    if "all" in constants.collections_title:
        target_collections = find_collections(constants.source_image_path)
        grouping = 1
    else:
        target_collections = find_collections(constants.source_image_path, constants.collections_title)
        grouping = 0
    collection_data_path = grouped_tag_path + constants.collections_title + "/"
    if not os.path.exists(collection_data_path):
        os.makedirs(collection_data_path)

    cate_att_tag_file = collection_data_path + "0_cate_att_tag_counts.json"

    if os.path.exists(cate_att_tag_file):
        cate_words = json.load(open(cate_att_tag_file))
    else:
        cate_words = summary_words(target_collections, cate_att_tag_file)

    if grouping:
        target_categories = list(cate_words.keys())
        for target_category in target_categories:
            target_aspects = find_category_aspects(cate_words, target_category)
            for target_aspect in target_aspects:
                if os.path.exists(collection_data_path + "%s_%s.dict" % (target_category, target_aspect)):
                    continue
                group_words(cate_words, target_category, target_aspect, collection_data_path)  # detail
