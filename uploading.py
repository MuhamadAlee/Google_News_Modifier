import time
import pyautogui
import parameters as para
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pynput.keyboard import Key, Controller


class Upload:

    def __init__(self):
        self.driver = webdriver.Chrome("./driver/chromedriver")
        self.driver.get('https://www.nftnewz.net/wp-admin')
        self.driver.maximize_window()
        self.keyboard = Controller()


    def login(self):
        try:
            #setting login credential
            self.driver.find_element_by_id('wp-submit').click()
            time.sleep(5)
            username = self.driver.find_element_by_id("user_login")
            username.send_keys(para.username)
            password = self.driver.find_element_by_id("user_pass")
            password.send_keys(para.password)

            #login
            self.driver.find_element_by_id("wp-submit").click()
            time.sleep(5)

        except:
            self.driver.close()
    def create_blog(self,my_tittle,my_para,my_img,mycat):
        
        try:

            flag=True
            # select posts class from menus
            menus = self.driver.find_elements_by_css_selector("div[class='wp-menu-name']")
            menus[1].click()
            time.sleep(2)

            # make a new post  
            menus = self.driver.find_elements_by_css_selector("ul[class='wp-submenu wp-submenu-wrap']")[0].find_elements_by_css_selector('li')
            menus[-1].click()
            time.sleep(2)



            #moving to down position
            self.driver.execute_script("scroll(0, 500);")
            time.sleep(2)

            #select category

            cat=""
            if mycat=="nft":
                cat="in-category-11"
            elif mycat=="metaverse":
                cat="in-category-12"
            else:
                cat="in-category-13"
                            
            category_div = self.driver.find_element_by_css_selector("div[id='category-all']")
            self.driver.execute_script("arguments[0].scrollTop = (0,300)", category_div)
            category = self.driver.find_element_by_id(cat).click()
            time.sleep(2)

           
            


            #uploading image
            self.driver.find_element_by_id("set-post-thumbnail").click()
            time.sleep(2)
            self.driver.find_element_by_id("menu-item-upload").click()
            time.sleep(2)
            self.driver.find_element_by_id("__wp-uploader-id-1").click()
            time.sleep(2)
            # pyautogui.press("esc")
            self.keyboard.press(Key.esc)
            self.keyboard.release(Key.esc)

            
            image = '/home/ali/Documents/BlogGenerationAutomation/images/'+my_img
            input_file = "//input[starts-with(@id,'html5_')]"
            self.driver.find_element_by_xpath(input_file).send_keys(image)

            time.sleep(10)
            self.driver.find_elements_by_css_selector('button[class="button media-button button-primary button-large media-button-select"]')[0].click()
            time.sleep(2)


            #again moving to top
            self.driver.execute_script("scroll(0, 0);")
            time.sleep(2)

             # place title here
            top_title = self.driver.find_element_by_id("title")
            top_title.send_keys(my_tittle)

            #place paragraph here
            self.driver.switch_to.frame(self.driver.find_element_by_id("content_ifr"))
            para_body = self.driver.find_element_by_id("tinymce")
            para_body.send_keys(my_para)

            #back to main content 
            self.driver.switch_to.default_content()

            #again moving to top
            self.driver.execute_script("scroll(0, 0);")
            time.sleep(2)
            #finally publish Blog here
            # self.driver.find_element_by_css_selector("input[id='publish']").click()
            self.driver.find_element_by_css_selector("input[id='save-post']").click()
            
            time.sleep(5)
            self.driver.close()
        except Exception as e:
            print(e)
            self.driver.close()
            flag=False
        

        return flag





    
    
