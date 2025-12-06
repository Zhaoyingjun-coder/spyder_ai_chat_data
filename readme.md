### 手册

```python
# 根据文本内容定位元素并点击示例
login_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'登录')]"))
)
login_button.click()
```
