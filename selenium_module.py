
import time
from selenium import webdriver
import selenium.webdriver.chrome.options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# driver boot procedure
def boot(resolution):
    # manage notifications
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    res = "--window-size=" + resolution
    chrome_options.add_argument(res)
    chrome_options.add_argument('--headless')
    
    # driver itself
    dv = webdriver.Chrome(chrome_options = chrome_options, executable_path = r"./driver/chromedriver80.exe")
    return dv

# kill the driver
def killd(dv):
    dv.quit()

# get map from city
def map(dv, city, zoom):
    # get link
    dv.get("https://www.lightpollutionmap.info/#zoom=4&lat=5759860&lon=1619364&layers=B0TFFFFFFFFFFFFF")
    WebDriverWait(dv, 20).until(EC.visibility_of_all_elements_located)
    time.sleep(1)
    
    # close info popup
    close_poppup = dv.find_element_by_xpath("/html/body/div[4]/div[1]")
    close_poppup.click()
    time.sleep(1)
    
    # slide transparency to 100
    slider = dv.find_element_by_xpath("/html/body/div[1]/div[2]/ul/li[1]/ul/li/div/div[2]/div/span")
    for i in range(40):
        slider.send_keys(Keys.ARROW_RIGHT)
    time.sleep(0.5)
    
    # input the city
    input_field = dv.find_element_by_id("searchBox")
    for i in range(len(city)):
        time.sleep(0.1)
        input_field.send_keys(city[i])
    time.sleep(2)
    
    # go to city location
    input_field.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.5)
    input_field.send_keys(Keys.ENTER)
    time.sleep(5)
    
    # try closing the video ad by xpath
    try:
        close_ad = dv.find_element_by_xpath("/html/body/div[7]/img")
        close_ad.click()
    except:
        None
        
    # try closing the video ad by id
    try:
        close_ad = dv.find_element_by_id("vdo_ai_cross")
        close_ad.click()
    except:
        None
    time.sleep(1)
    
    # close the top right menu
    close_right_menu = dv.find_element_by_xpath("/html/body/div[1]/div[1]/div")
    close_right_menu.click()
    time.sleep(2)
    
    # zoom out
    for i in range(10 - zoom):
        zoom_out = dv.find_element_by_xpath("/html/body/div[1]/div[7]/div[2]/div[1]/button[2]")
        zoom_out.click()
        time.sleep(2)

    dv.save_screenshot('lpm.png')