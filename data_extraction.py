from duckduckgo_search import DDGS
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from tqdm import tqdm
import pandas as pd
import os


def link_extractor():
    with DDGS(timeout=60) as ddgs:
        results = [r for r in ddgs.text("Canoo", max_results=1000)]
        print("Link Extraction Done")

    urls = [url['href'] for url in results]
    return urls


def data_extractor(urls):
    all_data = {}

    options = webdriver.ChromeOptions()
    options.add_argument("--test-type")
    options.add_argument("--disable-default-apps")
    options.add_argument("--ignore-certificate-errors");
    options.add_argument("--incognito");
    options.add_argument("--page-load-strategy='eager'")
    options.add_argument("--unhandled-prompt-behavior='dismiss'")

    for url in tqdm(urls):
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
        except Exception as e:
            print(e)
        time.sleep(3)
        try:
            data = driver.find_element(By.TAG_NAME, "body").text
        except Exception as e:
            print(e)
        all_data[url] = data
        driver.quit()

    return all_data


def replace(x):
    return x.replace("\n", " ")

def create_preprocess_save_dataframe(all_data):
    df = pd.DataFrame(list(all_data.items()), index=None, columns=['url', 'data'])

    df['data'] = df['data'].apply(replace)

    df = df[~df['data'].str.contains('404 This')]

    df = df[df['data']!='']

    df.to_csv('data.csv', index=None)
    return df


def data_to_txt(df):
    path = 'data'
    if not os.path.exists(path):
        os.makedirs(path)

    for i in range(len(df)):
        with open(f"./data/{i}.txt", 'w', encoding="utf-8") as f:
            f.write(df['data'][i])


if __name__=='__main__':
    urls = link_extractor()
    all_data = data_extractor(urls)
    df = create_preprocess_save_dataframe(all_data)
    data_to_txt(df)