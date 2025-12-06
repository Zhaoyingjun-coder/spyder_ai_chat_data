
import pandas as pd
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service

#初始化元宝驱动
def init_chrome_driver_yuanbao():
    chrome_options = Options()
    chromedriver_path = r"D:\installoffice\tools\Web_driver\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(10)

    handles = driver.window_handles  # 获取所有窗口句柄列表
    driver.switch_to.window(handles[-1])  # 切换到最新打开的窗口

    # 元宝
    url = 'https://yuanbao.tencent.com/chat/'
    driver.get(url)
    time.sleep(20)  # 等待手动登录
    return driver


# 登录
def login_chat(driver):
    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'登录')]"))
    )
    login_button.click()


#收集竞争对手信息
def collect_competitor(driver):

    def find_first_contains(text, lst):
        for index, element in enumerate(lst):
            if text in str(element):
                return index+1  # 找到第一个匹配项，返回索引
        return 0  # 无匹配项时返回-1

    target_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//div[@class='agent-chat__list__content']//div[@class='agent-chat__list__item__content']")
        )
    )
    last_element = target_elements[-1]
    # 第二步：取列表最后一个元素，再定位其下的目标子元素
    all_target_elements = last_element.find_elements(
        By.XPATH, ".//table[1]//tbody//tr//td[2]//*[@class='ybc-p']"
    )
    text_list = [i.text for i in all_target_elements]

    rank=find_first_contains('智推时代', text_list)
    res='、'.join(text_list)
    return res,rank

#点击参考资料
def yuanbao_click_reference(driver):
    try:
        all_source_elems = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "agent-chat__search-guid-tool__source")
            )
        )

        # 3. 筛选最后一个元素并点击
        if all_source_elems:  # 先判断列表非空，避免索引越界
            last_source_elem = all_source_elems[-1]  # 列表最后一个元素（Python索引-1）
            # 可选：等待元素可点击后再点击（更稳妥，避免元素存在但不可点）
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(last_source_elem)
            ).click()
            print("成功点击最后一个目标元素")
        else:
            print("未找到任何class=agent-chat__search-guid-tool__source的元素")
    except TimeoutException:
        print("超时：未找到目标元素")

#提取参考资料到DataFrame
def collect_url(driver,text):
    """
    提取指定元素的data-url和媒体名称，返回DataFrame
    :param driver: Selenium浏览器驱动对象
    :return: DataFrame（列：媒体平台、链接）
    """
    data_list = []

    try:
        # 1. 等待外层列表元素加载完成
        list_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "agent-dialogue-references__list")
            )
        )

        # 2. 定位列表下所有子级<li>标签
        li_elems = list_elem.find_elements(By.TAG_NAME, "li")

        if not li_elems:
            print("未找到任何<li>子标签")
            return pd.DataFrame(columns=["问题","媒体平台","竞争对手", "链接",'排名'])

        # 3. 遍历每个<li>，提取目标数据
        for li in li_elems[:10]:
            try:
                # 定位<li>下的.hyc-common-markdown__ref_card div（核心修正：data-url在这个div上）
                ref_card_elem = li.find_element(By.CLASS_NAME, "hyc-common-markdown__ref_card")
                # 提取data-url属性值（链接）
                url = ref_card_elem.get_attribute("data-url") or ""

                # 提取该div下的媒体名称（source_txt）
                source_elem = ref_card_elem.find_element(By.CLASS_NAME, "hyc-common-markdown__ref_card-foot__source_txt")
                media = source_elem.text.strip() or ""

                # 追加数据（过滤空值）
                if url or media:
                    data_list.append({"媒体平台": media, "链接": url})

            except NoSuchElementException:
                # 单个<li>下无ref_card或source_txt，跳过该<li>
                print("当前<li>标签下未找到ref_card或source_txt元素，跳过")
                continue

    except TimeoutException:
        print("超时：未找到class=agent-dialogue-references__list的外层元素")

    # 转换为DataFrame并返回
    cmp,rank=collect_competitor(driver)
    df = pd.DataFrame(data_list, columns=["问题","媒体平台",'竞争对手', "链接",'排名'])
    df["问题"] = text
    df["竞争对手"] = cmp
    df["排名"]=rank
    return df

# 倒计时显示函数
def countdown_with_display(seconds):
    for i in range(1, seconds + 1):
        # 使用 \r 回车符回到行首，覆盖之前的内容
        print(f"----- {i} 秒------", end='\r')
        time.sleep(1)
    # 循环结束后打印一个换行，避免下一行内容覆盖最后一次输出
    print()

def yuanbao_send_p(driver,text):
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.ql-editor.ql-blank'))
    )
    element.click()
    element.send_keys(text+'\n')
    print("-----------已发送问题！"+text+'-----------')


def check(driver, num):
    # 第一步：尝试等待元素加载（最多10秒），获取元素列表（仅用于判断数量）
    try:
        target_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='agent-chat__list__content']//div[@class='agent-chat__list__item__content']")
            )
        )
    except TimeoutException:
        # 超时则获取当前已有的元素（避免报错）
        target_elements = driver.find_elements(
            By.XPATH, "//div[@class='agent-chat__list__content']//div[@class='agent-chat__list__item__content']"
        )

    # 第二步：数量判断 + 等待逻辑（核心）
    if len(target_elements) != num:  # 数量不达标时等待10秒
        print(f"元素数量不达标（当前{len(target_elements)}个，目标{num}个），等待10秒后继续...")
        time.sleep(5)





