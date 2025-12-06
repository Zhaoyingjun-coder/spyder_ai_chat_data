
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


#点击登录按钮
def login_deepseek(driver):
    time.sleep(2)
    xpth='/html/body/main/div[1]/div[1]/div[3]/a' 
    target_element = driver.find_element(By.XPATH, xpth)
    target_element.click()

def deepseek_send_p(driver,text):
    wait = WebDriverWait(driver, 10)
    handles = driver.window_handles  # 获取所有窗口句柄列表
    driver.switch_to.window(handles[-1])
    textarea = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//textarea[@placeholder="给 DeepSeek 发送消息 "]')
        )
    )
    print("获取对话框")
    textarea.click()
    textarea.send_keys(text+'\n')
    print("已发送问题")
def deepseek_click_reference(driver):
    wait = WebDriverWait(driver, 10)
    try:
        # 使用XPath查找所有包含"已阅读"和"个网页"的元素
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH,
                "//*[contains(text(), '已阅读') and contains(text(), '个网页')]"))
        )
        if elements:
            # 获取最后一个匹配元素并点击
            last_element = elements[-1]
            last_element.click()
            print("成功点击最后一个阅读统计元素")
        else:
            print("未找到匹配的元素")

    except Exception as e:
        print(f"操作失败: {e}")


def get_elements_deepseek(driver):
    """
    提取所有 data-testid="search-text-item" 元素下的 href 和 footer-title-M1Yzgt 文本
    """
    links = []
    footer_texts = []
    
    container = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "dc433409")))

    # 获取所有a标签
    a_tags = container.find_elements(By.TAG_NAME, "a")

    for a_tag in a_tags:
        # 提取href属性
        href = a_tag.get_attribute("href")
        
        # 提取class="abc"的span标签文本
        try:
            span_text = a_tag.find_element(By.CLASS_NAME, "d2eca804").text.strip()
        except NoSuchElementException:
            span_text = ""  # 如果没有找到则为空
        
        if href:  # 只添加有href的结果
            links.append(href.strip())
            footer_texts.append(span_text if span_text else None)
    
    return links, footer_texts

def collect_companys(driver):
    def collect_company(driver):
        # 1. 定位所有class=container-PvPoAn的元素
        container_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "dad65929")
            )
        )
        if not container_elements:
            return ''

        container_elements=container_elements[0].find_elements(By.XPATH, "./*")

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



def deepseek_collect_data(driver,text):
    def find_index(lst, str_):
        for index, item in enumerate(lst):
            # 确保item是字符串类型，避免非字符串元素导致AttributeError
            if isinstance(item, str) and str_ in item:
                return index + 1
        return 0

    time.sleep(2)
    DATA=pd.DataFrame([],columns=['问题','来源','竞争对手','网址','排名'])
    # 点击最后一个匹配的元素
    time.sleep(2)
    links,footer_texts=get_elements_deepseek(driver)
    str_cmp,cmp_ls=collect_companys(driver)
    print(links)
    print(footer_texts)
    cmp=str_cmp
    print(cmp)

    time.sleep(1)

    rank = find_index(cmp_ls, "智推")

    for i in range(len(links)):
        #new_row = {'问题':text,'来源': where[i],'网址':web[i]}
        DATA.loc[len(DATA)] = [text,footer_texts[i],cmp,links[i],rank]
    return DATA


def cc(driver):
    xpath = '//*[@id="root"]/div/div/div[2]/div[3]/div[2]/div/div[1]/div[4]/div[1]'
    # 等待元素可点击并点击
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    element.click()  # 注意是 click() 不是 cleck()

def new_page_deepseek(driver):
    xpath = '//*[@id="root"]/div/div/div[2]/div[1]/div/div[2]'
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    print("建立对话")

def stop_deepseek(driver):
    xpath = '//*[@id="root"]/div/div/div[2]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div[2]/div/div[2]'
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    print("停止回答")

def init_chrome_driver():
    # 打开浏览器
    chrome_options = Options()
    chromedriver_path = r"D:\installoffice\tools\Web_driver\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service,options=chrome_options)
    driver.set_page_load_timeout(10)

    handles = driver.window_handles  # 获取所有窗口句柄列表
    driver.switch_to.window(handles[-1])  # 切换到最新打开的窗口

    #deepseek
    url='https://www.deepseek.com/'
    driver.get(url)
    time.sleep(3)
    #登录
    xpth='/html/body/main/div[1]/div[1]/div[3]/a'
    target_element = driver.find_element(By.XPATH, xpth)
    target_element.click()

    time.sleep(15)  #等待手动登录
    handles = driver.window_handles  # 获取所有窗口句柄列表
    driver.switch_to.window(handles[-1])
    return driver


def check(driver,num):
    container_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "dad65929")
        )
    )
    c=len(container_elements[0].find_elements(By.XPATH, "./*"))
    if c != num:
        time.sleep(5)


def countdown_with_display(seconds):
    for i in range(1, seconds + 1):
        # 使用 \r 回车符回到行首，覆盖之前的内容
        print(f"----- {i} 秒------", end='\r')
        time.sleep(1)
    # 循环结束后打印一个换行，避免下一行内容覆盖最后一次输出
    print()