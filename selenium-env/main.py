from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path # this will get you the path variable
import time
import boto3
import os


client = boto3.client('s3')

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello Wolld"
    
@app.route("/seo-screenshots", methods=["GET","POST"])
def getSEOScreenshots():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("window-size=1920,1080")

    svc = webdriver.ChromeService(executable_path=binary_path)
    driver = webdriver.Chrome(service=svc,options=options)

    if request.method == "GET" or request.method == "POST":
        body = request.get_json()
        fileName = body['fileName']
        url = body['url']
        
        if(body is not None):
            # http or http needs to be present. If not concat it with the url.
            if( "https" not in url):
                driver.get('https://' + url)
            else:
                driver.get(url)
            
            time.sleep(10)

            w = driver.execute_script('return document.body.parentNode.scrollWidth')
            h = driver.execute_script('return document.body.parentNode.scrollHeight')
            #set to new window size
            driver.set_window_size(w, h)

            title = driver.execute_script('return document.title;')
        
            metas = driver.execute_script("return document.getElementsByTagName('meta')")
            for i in range(len(metas)):
                metaDesc = driver.execute_script("return document.getElementsByTagName('meta')"+str([i])+".name")
                if metaDesc == "description":
                    metaDesc = driver.execute_script("return document.getElementsByTagName('meta')"+str([i])+".content")
                    break
                else:
                    metaDesc = "Not Found"


            driver.save_screenshot("/home/ubuntu/python-web-screenshots/screenshots/"+ str(fileName) + ".png")
            file = open("/home/ubuntu/python-web-screenshots/screenshots/" + str(fileName) + ".png","rb")
            driver.quit()
            client.upload_fileobj(file,'seo-screenshots',fileName,{'ACL':'public-read'})


            url = "https://seo-screenshots.s3.amazonaws.com/" + str(fileName)
            seoData = {
                'title': title,
                'description': metaDesc,
                'screenshotURL': url,
            }
            
            return jsonify(seoData), 200
    elif(body is None):
        return "Bad Request. Request body has valid data.", 400
    else:
        return "Internal Server Error", 500
    
    request.close()

if __name__ == "__main__":
    app.run()