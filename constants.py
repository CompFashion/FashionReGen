GENERATED = True  # use llm to generate description
RETRIEVAL = False  # use llm summarization and semantic alignment retrieval to get images
gpt_base_url = "https://api.uniapi.io"
model_selection = 'GPT'
category_specific = {'Dresses&Skirts': ['dresses', 'skirts'],
                     'Jackets&Coats&Outerwear': ['coats', 'jackets'],
                     'Topweights': ['blouses and woven tops', 'knits and jersey tops', 'sweaters'],
                     'Trousers&Shorts': ['trousers', 'shorts']}
# For those do not have corresponding data in conf, using relevant subcategory
section_gpt_conf = {'knits and jersey tops': 'blouses and woven tops'}
# attributes needed in yoy calculation to make bar charts
yoy_bar_attri = {'dresses': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'skirts': ['silhouette', 'detail'],
                 'blouses and woven tops': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'knits and jersey tops': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'sweaters': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'trousers': ['silhouette', 'detail', 'print and pattern'],
                 'shorts': ['silhouette', 'detail'],
                 'jackets': ['silhouette', 'detail', 'neckline', 'sleeve'],
                 'coats': ['silhouette', 'detail', 'neckline', 'sleeve']}
share_pie_attri = {"skirts": "length", "coats": "length"}
years = ['2019', '2020', '2021', '2022', '2023']
all_brands = ['chanel', 'christian-dior', 'givenchy', 'louis-vuitton', 'saint-laurent', 'valentino']
season_abb = {"springsummer": "S/S"}
