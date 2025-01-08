# FashionReGen
## Overview
This repository contains the code for the [FashionReGen paper](https://arxiv.org/abs/2403.06660), which proposes an LLM-empowered approach to fashion report generation. It provides a framework for **Catwalk Understanding**, **Collective Organization and Analysis**, and **Fashion Report Generation**, as illustrated in the figure below.

![framework.png](framework.png)

## Getting Started
### Key Steps for Report Generation
1. Prepare **catwalk images**. You can either use your own images or download the example data from Google Drive (see the Dataset section below for details, Dataset Optional 1).
2. Edit the [constants.py](constants.py) file according to the provided instructions.
3. Fill in your personal **OpenAI API key** in [key.yaml](key.yaml). Note that the OpenAI API format may change over time, so please update the request format accordingly if any changes occur.
4. Modify the **year, season, brand and category** in [main.py](main.py) to match the specifics of your catwalk images.
5. Run [main.py](main.py) to execute the entire pipeline.

It will use the following codes and their functions are listed below:
### Settings
[constants.py](constants.py) contains all the settings. **Edit this file to customize for your specific needs before running.**
### Tagging
All python files in **tagging/** handle the tagging process. This includes:
* GPT tagging for the catwalk images.
* Data processing steps, including refining, grouping, and formatting the tagging results.
* Final outputs are **statistical results** for both category distribution and category attribute distribution.
### Fashion Metric Calculation
[metrics.py](metrics.py) calculates fashion metrics and plots charts for generation.
### Report Helper
1. [model.py](model.py) contains the different parts of content generation functions.
2. [existed_report.py](existed_report.py) is used for save and load already generated report.
### Description Generation
All python files in **description_generation/** folder, along with [llm_description.py](llm_description.py) are responsible for generating textual analyses using LLM for both overview and section-level analysis. This includes retrieving examples as specified in the prompt.
[prompt.py](prompt.py) contains predefined prompts, which include task descriptions and instructions for the analysis generation.


## Dataset  
https://drive.google.com/drive/folders/1bwsHmLsF9DWIZo18SjKejmW45YOJuwpJ?usp=sharing  
### Compulsory
unzip **wgsn_report_data** to directory **./description_generation**
### Optional
1. unzip **data** to directory **./**, containing all catwalk images and statistical results. **You can use catwalk images here as target images**.
2. unzip **gen_report** to directory **./**, containing all generated report by Gemini and GPT.
## Citing FashionReGen
If you find this repository useful, please cite our paper:
```
@inproceedings{FashionReGen,
  author       = {Yujuan Ding and
                  Yunshan Ma and
                  Wenqi Fan and
                  Yige Yao and
                  Tat{-}Seng Chua and
                  Qing Li},
  title        = {FashionReGen: LLM-Empowered Fashion Report Generation},
  booktitle    = {{WWW} (Companion Volume)},
  pages        = {991--994},
  publisher    = {{ACM}},
  year         = {2024}
}
```

## RUN UI System(Optional)
1. Run **page.py** for backend service。
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
