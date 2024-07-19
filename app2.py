from DrissionPage import ChromiumPage, ChromiumOptions

email = "sami.belhadj@oddo-bhf.com"  # replace with dynamic value if needed
password = "7cB3MP.6y9.Z?c?"  # replace with dynamic value if needed

try:
    # options = ChromiumOptions().set_headless(False)
    driver= ChromiumPage()
    print("ok")
    driver.get("https://app.pluralsight.com/id")
    driver.find_element_by_id("Username").send_keys(email)
    driver.find_element_by_id("Password").send_keys(password)
    driver.find_element_by_id("login").click()
    cookies = driver.get_cookies()
    cookie_value = None
    for cookie in cookies:
        if cookie['name'] == "Identity.Session":
            cookie_value = cookie['value']
            break
    driver.quit()
    print(cookie_value)


except Exception as e:
    print(e)
