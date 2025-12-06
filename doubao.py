import pandas as pd
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def collect_companys(driver):
    def collect_company(driver):
        # 1. 定位所有class=container-PvPoAn的元素
        container_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "container-PvPoAn")
            )
        )
        if not container_elements:
            return ''

        # 2. 取最后一个container元素
        last_container = container_elements[-1]

        # 3. 提取目标td文本
        td_text_list = []

        # 定位最后一个container下第一个table的所有tr（相对XPath）
        tr_list = WebDriverWait(last_container, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//table[1]//tbody//tr"))
        )
        # 遍历所有tr，提取第一个td的文本
        for tr in tr_list:
            td_text = tr.find_element(By.XPATH, ".//td[1]").text.strip()
            td_text_list.append(td_text)

        res = "、".join(td_text_list)

        return res,td_text_list

    prev_res=''
    while True:
        curr_res,cmps = collect_company(driver)  # 执行获取文本
        time.sleep(1)
        if curr_res == prev_res:  # 相邻两次结果相同则终止
            break
        prev_res = curr_res
    return prev_res,cmps



def get_elements_doubao(driver):
    """
    提取所有 data-testid="search-text-item" 元素下的 href 和 footer-title-M1Yzgt 文本
    """
    links = []
    footer_texts = []
    
    # 定位所有 data-testid="search-text-item" 的元素
    # search_items = driver.find_elements(By.CSS_SELECTOR, '[data-testid="search-text-item"]')

    wait = WebDriverWait(driver, 10)

    # 等待元素出现，找到后返回
    search_items = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '[data-testid="search-text-item"]')
        )
    )

    for item in search_items:
        try:
            # 1. 提取 <a> 标签的 href 属性
            a_tag = item.find_element(By.CSS_SELECTOR, 'a.search-lIUYwC')
            href = a_tag.get_attribute('href')
            if href:
                links.append(href.strip())

            # 2. 提取 class="footer-title-M1Yzgt" 的文本
            footer_element = item.find_element(By.CSS_SELECTOR, '.footer-title-M1Yzgt')
            footer_text = footer_element.text.strip()
            if footer_text:
                footer_texts.append(footer_text)
            else:
                footer_texts.append(None)  # 兜底
                
        except Exception as e:
            # 某个子元素找不到时的容错处理
            print(f"处理单个搜索项时出错: {str(e)}")
            continue  # 跳过当前项，继续处理下一个
    
    return links, footer_texts

#点击登录按钮
def login_doubao(driver):
    xpth='//*[@id="chat-route-layout"]/div/main/div/div[1]/div[2]/button/span' 
    target_element = driver.find_element(By.XPATH, xpth)
    target_element.click()

#发送问题
def doubao_send_p(driver,text):
    wait = WebDriverWait(driver, 20)

    #点击对话框并发送问题
    element = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//textarea[@data-testid='chat_input_input']")
            )
        )
    if element:  
        element[0].click()
        element[0].send_keys(text+'\n')

#点击参考资料
def doubao_click_reference(driver):
    wait = WebDriverWait(driver, 20)
    
    # 获取参考资料的网址以及平台
    # time.sleep(20)
    share_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'分享')]"))
        )
    elements = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//*[contains(text(),'篇资料')]")
                )
            )
    if elements:
        try:
            # 点击最后一个匹配的元素
            time.sleep(1)
            elements[-1].click()
        except Exception as e:
            print('点击元素时出错')
    else:
        print("未找到包含'篇资料'的按钮")

    print("成功点击最后一个包含'篇资料'的按钮")


def doubao_collect_data(driver,text):

    def find_index(lst, str_):
        for index, item in enumerate(lst):
            # 确保item是字符串类型，避免非字符串元素导致AttributeError
            if isinstance(item, str) and str_ in item:
                return index + 1
        return 0

    print("开始收集数据")
    # time.sleep(2)
    DATA=pd.DataFrame([],columns=['问题','网址','竞争对手','来源','排名'])
    # 点击最后一个匹配的元素
    # time.sleep(2)
    links,footer_texts=get_elements_doubao(driver)
    cmp_str,cmp=collect_companys(driver)
    rank=find_index(cmp,"智推")
    cmp=cmp_str
    print(links)
    print(footer_texts)
    print(cmp)
    print(rank)

    for i in range(len(links)):
        #new_row = {'问题':text,'来源': where[i],'网址':web[i]}
        DATA.loc[len(DATA)] = [text, links[i], footer_texts[i], cmp,rank]

    return DATA

def countdown_with_display(seconds):
    for i in range(1, seconds + 1):
        # 使用 \r 回车符回到行首，覆盖之前的内容
        print(f"----- {i} 秒------", end='\r')
        time.sleep(1)
    # 循环结束后打印一个换行，避免下一行内容覆盖最后一次输出
    print()


def init_chrome_driver_yuanbao():
    chrome_options = Options()
    chromedriver_path = r"D:\installoffice\tools\Web_driver\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(10)

    handles = driver.window_handles  # 获取所有窗口句柄列表
    driver.switch_to.window(handles[-1])  # 切换到最新打开的窗口

    # 豆包
    url = 'https://www.doubao.com/chat/'
    driver.get(url)
    time.sleep(2)
    # login_doubao(driver)
    time.sleep(20)  # 等待手动登录
    return driver

def check(driver,num):
    container_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "container-PvPoAn")
        )
    )
    if len(container_elements) != num:
        time.sleep(5)