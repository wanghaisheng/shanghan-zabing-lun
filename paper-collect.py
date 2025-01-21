# https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baiduadv&wd=%E5%9B%BD%E4%BA%A7ct%20site%3Amp.weixin.qq.com&oq=%E5%9B%BD%E4%BA%A7ct%20site%3Amp.weixin.qq.com&rsv_pq=e88db4ce00cd887e&rsv_t=256b4D2yo2fBNTqKe7E3IhSD4s4sO14u68eLuvCndtsP00QR1%2Br2andmZKJ69F0&rqlang=cn&rsv_enter=1&rsv_dl=tb&gpc=stf%3D1736852798%2C1737457598%7Cstftype%3D1&tfflag=1&si=mp.weixin.qq.com&ct=2097152
# https://weixin.sogou.com/weixin?query=%E5%9B%BD%E4%BA%A7ct&_sug_type_=&sut=4315&lkt=1%2C1737143307246%2C1737143307246&s_from=input&_sug_=y&type=2&sst0=1737143307348&page=10&ie=utf8&w=01019900&dr=1
#搜狗不登录显示10条 总共1000条  放弃

import pandas as pd
import json
import time
import argparse
import os
import urllib.parse
from getbrowser import setup_chrome  # Import your setup_chrome

browser = setup_chrome()


def getlinks(k, timeframe='7days', position='all', site=None,perpageresult='50',format=None):
    urls = []
    baseurl = 'https://www.baidu.com/gaoji/advanced.html'
    # search_url = f"https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baiduadv&wd={urllib.parse.quote(k)}%20site%3A{site}&oq={urllib.parse.quote(k)}%20site%3A{site}&rsv_pq=e88db4ce00cd887e&rsv_t=256b4D2yo2fBNTqKe7E3IhSD4s4sO14u68eLuvCndtsP00QR1%2Br2andmZKJ69F0&rqlang=cn&rsv_enter=1&rsv_dl=tb&gpc=stf%3D1736852798%2C1737457598%7Cstftype%3D1&tfflag=1&si={site}&ct=2097152"
    # input
    tab = browser.new_tab()
    tab.get(baseurl)
    #输入关键词
    print('输入关键词')
    
    tab.eles('t:table')[0].ele('t:tbody').children()[1].clear().input(k)
    setting=tab.eles('t:table')[1].ele('t:tbody').children()
    # 每页结果数量
    print('设置每页数量')
    
    select=setting[0].ele('t:select')
    option = select('t:option')
    if perpageresult not in ["10","20","50"]:
        perpageresult="50"
    select.select.by_value(perpageresult)
    #最近几天的结果
    print('设置时间')
    
    select=setting[1].ele('t:select')
    option = select('t:option')
    if timeframe not in ['0days',"1days","7days","30days",'360days']:
        timeframe="0days"
        
    select.select.by_value(timeframe.replace('days','').strip())
    #文档格式	pdf word
    select=setting[3].ele('t:select')
    option = select('t:option')
    if format is None :
        pass
        
    else:
        if format not in ['all',"pdf","doc","xls",'ppt','rtf']:
            format="all"
        select.select.by_value(format)

    #关键词出现位置
    checkbox=setting[4].eles('t:input')
    if position not in ['all',"title","url"]:
        position="all"
    if position=='all':
        checkbox[0].click()
    if position=='title':
        checkbox[1].click()
    if position=='url':
        checkbox[2].click()
    # 网站内查询
    print('输入搜索的目标网站')
    
    if site:
        setting[-1].ele('t:input').input(site)
    

    
    tab=tab.ele('@value=百度一下').click.for_new_tab()
    print('提交结果 ',tab.url)
    all_items = []
    page_num = 1
    while True:
        time.sleep(3)
        try:
            uls = tab.eles('.result.c-container.xpath-log.new-pmd')
            for index, e in enumerate(uls):
                try:
                    link = e.ele("t:h3").ele("t:a").link
                    title = e.ele("t:h3").ele("t:a").text
                    dese = e.ele('.c-title.t.t.tts-title').next(2)
                    date = dese.ele('.c-color-gray2').text
                    des = dese.ele('.content-right_1THTn').text
                    item = {
                        "keyword": k,
                        "url": link,
                        "title": title,
                        "date": date,
                        "des": des,
                        "page_num": page_num
                    }
                    all_items.append(item)

                except Exception as ee:
                    print(f'Error parsing link{ee}')
        except Exception as ee:
            print(f"Error parsing page:{page_num} {ee}")

        try:
            next_page = tab.ele('text:下一页 >')
            next_page.click()
            page_num += 1
        except:
            break

    tab.close()
    return all_items

def save_data(data, output_format, filename, result_folder='result', keyword=''):
    os.makedirs(result_folder, exist_ok=True)

    if keyword:
        filename = f"{keyword}_{filename}"

    full_filename = os.path.join(result_folder, filename)

    if output_format == 'csv':
        df = pd.DataFrame(data)
        df.to_csv(full_filename, index=False, encoding='utf_8_sig')
        print(f"Data saved to {full_filename} (CSV format)")
    elif output_format == 'json':
        with open(full_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {full_filename} (JSON format)")
    else:
        print("Invalid output format. Supported formats are 'csv' and 'json'.")


def load_historical_links(filename='archive.csv', result_folder='result', keyword=''):
    if keyword:
        filename = f"{keyword}_{filename}"
    full_filename = os.path.join(result_folder, filename)
    try:
        df = pd.read_csv(full_filename)
        return set(df['url'].tolist())
    except FileNotFoundError:
        return set()
    except pd.errors.EmptyDataError:
        return set()
    except Exception as e:
        print(f"Error loading historical links: {e}")
        return set()


def save_historical_links(new_links, filename='archive.csv', result_folder='result', keyword=''):
    if keyword:
        filename = f"{keyword}_{filename}"
    full_filename = os.path.join(result_folder, filename)
    os.mkdirs(result_folder,exist)
    try:
        existing_links = load_historical_links(filename, result_folder, keyword)

        new_df = pd.DataFrame(new_links)

        if existing_links:

            existing_df = pd.read_csv(full_filename)

            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            updated_df = new_df

        updated_df.drop_duplicates(subset=['url'], inplace=True)
        updated_df.to_csv(full_filename, index=False, encoding='utf_8_sig')

    except Exception as e:
        print(f"Error saving historical links: {e}")

    if not os.path.exists(full_filename):
        pd.DataFrame({'url': []}).to_csv(full_filename, index=False, encoding='utf_8_sig')


# Main execution
if __name__ == "__main__":
    # Get configuration from environment variables
    output_format = os.getenv('OUTPUT_FORMAT', 'csv').lower()  # Default: csv
    output_filename = os.getenv('OUTPUT_FILENAME', 'data')  # Default: data
    result_folder = os.getenv('RESULT_FOLDER', 'result')  # Default: result

    site = os.getenv('domain', 'wap.cnki.net')  # Default:
    keywords = os.getenv('keywords', '伤寒杂病')  # Default:

    if ',' in keywords:
        keywords = keywords.split(',')
    else:
        keywords = [keywords]

    # You can still override with command-line arguments if needed
    parser = argparse.ArgumentParser(description="Scrape data from sxlib.org.cn and save it as CSV or JSON.")
    parser.add_argument("-f", "--format", choices=['csv', 'json'],
                        help="Override OUTPUT_FORMAT environment variable")
    parser.add_argument("-o", "--output",
                        help="Override OUTPUT_FILENAME environment variable")
    parser.add_argument("-r", "--result-folder",
                        help="Override RESULT_FOLDER environment variable")
    args = parser.parse_args()

    if args.format:
        output_format = args.format
    if args.output:
        output_filename = args.output
    if args.result_folder:
        result_folder = args.result_folder

    for k in keywords:
        all_links = getlinks(k,site=site)
        print(f"Found {len(all_links)} links for keyword: {k}")

        historical_links = load_historical_links(result_folder=result_folder, keyword=k)
        new_links = [item for item in all_links if item['url'] not in historical_links]
        print(f"Found {len(new_links)} new links for keyword: {k}")

        if len(all_links)>0:
            save_historical_links(historical_links.extends(all_links), result_folder=result_folder, keyword=k)
        if len(new_links)>0:
            save_historical_links(new_links,filename='latest.csv', result_folder=result_folder, keyword=k)

    browser.quit()
