import base64


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
        report_name = one["pdf_paths"]
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
