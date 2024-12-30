import base64


def get_one_data(wgsn_data, conf, sub_cate):
    for k, v in wgsn_data.items():
        if conf["name"] in k:
            for data in v:
                if data["overview"] != conf["overview"] and data["title"] == sub_cate:
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
        sub_c = exa_data[0]["title"]
        if season_year in exa and sub_c == sub_cate:
            continue
        valid_example_list.append(exa_data[0]["slots"][0])
    return valid_example_list
