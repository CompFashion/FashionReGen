# Framework
![framework.png](framework.png)
Yujuan Ding, Yunshan Ma, Wenqi Fan, Yige Yao, Tat-Seng Chua, and Qing Li. 2024. FashionReGen: LLM-Empowered Fashion Report Generation. In Companion Proceedings of the ACM Web Conference 2024 (WWW '24). Association for Computing Machinery, New York, NY, USA, 991–994. https://doi.org/10.1145/3589335.3651232
# Dataset  
https://drive.google.com/drive/folders/1bwsHmLsF9DWIZo18SjKejmW45YOJuwpJ?usp=sharing  
## Compulsory
1. unzip **wgsn_report_data** to directory **./description_generation**
2. unzip **data** to directory **./**, containing all catwalk images and statistical results.
## Optional
unzip **gen_report** to directory **./**, containing all generated report by Gemini and GPT.
# Report Generation
1. Prepare catwalk images(Optional)
2. Edit constants.py.
3. Create **key.yaml** for api_key.
4. Run main.py for generation.
# File Description
## Main File
1. [page.py](page.py) provides the backend service and also contains the Gradio page.
2. [constants.py](constants.py) contains all the settings. **Edit this file to customize for different needs before running.**
3. [main.py](main.py) is the program for report generation from beginning, including customized catwalk images tagging and report generation.
## Tagging
1. [1_0_tag.py](tagging%2F1_0_tag.py)  generates the original GPT-tagged content.
2. [1_1_tag_format_refining.py](tagging%2F1_1_tag_format_refining.py) refines the GPT-tagged content.
3. [1_2_tag_word_grouping.py](tagging%2F1_2_tag_word_grouping.py) groups the tagging corpus.
4. [1_3_0_collection_tags_update.py](tagging%2F1_3_0_collection_tags_update.py) and [1_3_tag_dict_updating.py](tagging%2F1_3_tag_dict_updating.py) update tags with group dictionary.
5. [1_4_0_summarize_collection_tags.py](tagging%2F1_4_0_summarize_collection_tags.py) and [1_4_get_category_tags.py](tagging%2F1_4_get_category_tags.py) get statistical results for different categories' attributes.
6. [1_5_category_counting.py](tagging%2F1_5_category_counting.py) calculates the category distribution.
## Description generation
1. [overview_analysis_gen.py](description_generation%2Foverview_analysis_gen.py) provides helper functions for textual overview analysis generation, e.g., example retrieval.
2. [section_analysis_gen.py](description_generation%2Fsection_analysis_gen.py) provides helper functions for textual section analysis generation.
3. [llm_description.py](llm_description.py) includes functions for **textual analysis generation with LLM**.
## Other
1. [model.py](model.py) contains the main functions for report generation.
2. [metrics.py](metrics.py) calculates fashion metrics and plots charts for generation.
3. [prompt.py](prompt.py) includes prompts for textual analysis generation.
4. [existed_report.py](existed_report.py) is used for save and load already generated report.
# RUN UI System(Optional)
1. Run **page.py** for backend service.
2. The frontend package is https://drive.google.com/file/d/1QziQvacgCic13x1fPEKvBjnq1BScjDv6/view?usp=drive_link. Install nginx for frontend service, the nginx.conf file should contain the following code.
Then you can visit the webpage by http://localhost/fashionregen.
```
   server {
        listen 9001;
        server_name localhost;
	location /api/ {
            proxy_pass http://localhost:7860/;
        }
        location / {
            root   # replace this content with your frontend project directory
            index  index.html;
            try_files $uri $uri/ /index.html;
	    
   add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
    add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization'; 
    if ($request_method = 'OPTIONS') {
        return 204;
    }
      	
	} 
        }

    server {
        listen 80;
        server_name localhost;
        root # replace this content with your frontend project directory
	location /fashionregen {
         proxy_pass http://localhost:9001/;
         add_header Access-Control-Allow-Origin *;
   	 add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
   	 add_header Access-Control-Allow-Headers 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization';
 
    	if ($request_method = 'OPTIONS') {
        	return 204;
	    }
	}
    }
```
