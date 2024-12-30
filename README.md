# Dataset  
https://drive.google.com/drive/folders/1bwsHmLsF9DWIZo18SjKejmW45YOJuwpJ?usp=sharing  
## Compulsory
1. unzip **wgsn_report_data** to directory **./description_generation**
2. unzip **data** to directory **./**, containing all catwalk images and statistical results.
## Optional
unzip **gen_report** to directory **./**, containing all generated report by Gemini and GPT.
# RUN Introduction
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
# File Description
1. **page.py**: The backend service, also containing the Gradio page.
2. **model.py**: Main functions for report generation.
3. **metrics.py**: Calculating fashion metrics and plot charts for generation.
4. 