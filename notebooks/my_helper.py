import cv2
import matplotlib.pyplot as plt
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from lxml import etree
import re

def view_image(window_name,img,destroy=False):
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.imshow(window_name,img)
    if destroy:
        cv2.waitKey()
        cv2.destroyAllWindows()
        
def plot_img(img,rgb=True,figsize=(4,3)):
    plt.figure(figsize=figsize)
    if rgb:
        plt.imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    else:
        plt.imshow(img)
    plt.axis("off")
    

def download_image(url,filename):
    res = requests.get(url,stream=True)
    if res.status_code == 200:
        path = "../images/"+ filename+".jpg"
        print(f"[INFO] downloading image and saving to {path}")
        with open(path,"wb") as f:
            for chunk in res.iter_content(chunk_size=1024):
                f.write(chunk)
    else:
        print(f"[INFO] Failed download image")
        
def download_folder_github(url,save_path):
    base_url = "https://github.com"
    base_path = Path(save_path)
    base_path.mkdir(parents=True,exist_ok=True)
    res = requests.get(url)
    soup = BeautifulSoup(res.content,"html.parser")
    dom = etree.HTML(str(soup))
    elements = dom.xpath('//*[@id="repo-content-pjax-container"]/div/div/div[4]/div[3]/div/*/*[@role="rowheader"]//*[@href]')
    for ele in elements[1:]:
        blob_url = ele.attrib["href"]
        filename = ele.text
        raw_url = base_url + re.sub("blob","raw",blob_url)
        file_path = base_path/filename
        if file_path.is_file():
            print(f'File already exists skipping download file {filename}')
            continue
        file_res = requests.get(raw_url,stream=True)
        if file_res.status_code == 200:
            print(f'Downloading file {filename}')
            with open(file_path,"wb") as f:
                for chunk in file_res.iter_content(chunk_size=1024):
                    f.write(chunk)
        else:
            print(f'Error getting the content from url {raw_url}')