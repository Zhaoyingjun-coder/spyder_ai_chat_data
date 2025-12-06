
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd


def qianwen_send_p(driver, text):
    wait = WebDriverWait(driver, 10)
    handles = driver.window_handles  # 获取所有窗口句柄列表
    driver.switch_to.window(handles[-1])
    textarea = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//textarea[@placeholder="向千问提问"]')
        )
    )
    print("获取对话框")
    textarea.click()
    textarea.send_keys(text + '\n')
    print("已发送问题")


def collect_companys(driver,text):
    def collect_company(driver):
        # 1. 定位所有class=container-PvPoAn的元素
        container_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "content-wXxT0D")
            )
        )

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
            td_text = tr.find_element(By.XPATH, ".//td[2]").text.strip()
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
    # return prev_res,cmps
    df=pd.DataFrame()
    df["问题"] = [text]
    df["公司名称"] = [prev_res]
    return df

def init_chrome_driver():
    # 打开浏览器
    chrome_options = Options()
    chromedriver_path = r"D:\installoffice\tools\Web_driver\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service,options=chrome_options)
    driver.set_page_load_timeout(10)

    handles = driver.window_handles  # 获取所有窗口句柄列表
    driver.switch_to.window(handles[-1])  # 切换到最新打开的窗口

    #qianwen
    url='https://www.qianwen.com/'
    driver.get(url)
    time.sleep(3)


    time.sleep(15)  #等待手动登录
    handles = driver.window_handles  # 获取所有窗口句柄列表
    driver.switch_to.window(handles[-1])
    return driver

def countdown_with_display(seconds):
    for i in range(1, seconds + 1):
        # 使用 \r 回车符回到行首，覆盖之前的内容
        print(f"----- {i} 秒------", end='\r')
        time.sleep(1)
    # 循环结束后打印一个换行，避免下一行内容覆盖最后一次输出
    print()
