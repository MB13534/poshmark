import selenium, time, numpy, winsound, pdb, credentials, pickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


def rt(d): 
    times = numpy.random.random() + d
    return times


def debugger(): 
    #tests for the pop up captcha
    try:                
        captcha_pat = "/html/body/div[1]/div/div/div[2]/div[1]/h5" 
        captcha_fail = driver.find_element_by_xpath(captcha_pat)
        if captcha_fail.text == "Oh the HUMAN-ity. Check the box if you're a real person.":            
            for i in range(10): winsound.Beep(440, 500)                
            pdb.set_trace()
    except:
        pass

    #tests for the embedded captcha
    try:          
        if driver.find_element_by_xpath('/html/body/main/div/div/div[2]/form/div[3]/div') != []:
            for i in range(10): winsound.Beep(440, 500)                
            pdb.set_trace()        
    except:
        pass
    
    
def log_in(): 
    print('[*] Loading the Firefox web browser and directing it to the Poshmark log in page. ')
    driver.get('https://poshmark.com/login')
    driver.implicitly_wait(0)
    
    poshmark_username = credentials.poshmark_username
    poshmark_password = credentials.poshmark_password
    
    print(f'[*] Logging into Poshmark account, {poshmark_username}.')

    username = driver.find_element_by_name("login_form[username_email]")
    username.send_keys(poshmark_username)
    time.sleep(rt(1))

    password = driver.find_element_by_name("login_form[password]")
    password.send_keys(poshmark_password)
    time.sleep(rt(1))

    password.send_keys(Keys.RETURN)
    time.sleep(rt(2))
    
    debugger()
    
    print('[*] What name would you like to search for?')
    search = input()
    driver.get(f'https://poshmark.com/search?query={search}&type=people&src=dir')
    time.sleep(rt(2))
    
    
def scroll_page(delay=3):
    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    print("[*] Scrolling through followers. This will take a moment...")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(rt(delay))

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:

            break

        last_height = new_height

        
def follows_in_past_24():
    #opens saved file
    with open ('posh_save_followers.pkl', 'rb') as f: 
        try:
            time_list = pickle.load(f)
        except EOFError:
            time_list = []

    #updates list to only include timestamps that were made within 24h
    time_list = [t for t in time_list if round(time.time()) - t < 86400] 

    #overwrites save file with the updated list
    with open('posh_save_followers.pkl', 'wb') as f: 
        pickle.dump(time_list, f)

    return(time_list)        


def get_closet_follow_icons():
    #this is for people that already follow you
    #build_follow_icons = driver.find_elements_by_css_selector('html body div#app main div#content.content--desktop div.view div.col-l19.col-x18 div.follow-list__container.closet__follow-list.card.card--medium.form-card div.follow__action.follow-list__item button.al--right.btn.follow__btn.follow__action__button.btn--primary')
    
    #this is for searching for people
    build_follow_icons = driver.find_elements_by_css_selector('html body div#app main div#content.content--desktop div.view div.search-people.al--center.ta--c div.follow-list__container.card.card--medium div.follow__action.follow-list__item button.al--right.btn.follow__btn.follow__action__button.btn--primary')

    return build_follow_icons


def clicks_follow_user(follow_icon, d=.1):
    driver.execute_script("arguments[0].click();", follow_icon); time.sleep(rt(d))
    #follow_icon.click()
    #time.sleep(rt(d))
    
    
def follow(time_list):
    current_cycle_count=0
    print(f'[*] Preparing to follow x{len(follow_icons)} users')

    for icon in reversed(follow_icons): #go from bottom to top
        debugger()
        try:
            clicks_follow_user(icon)
            
            current_cycle_count+=1
            print(f'\t{current_cycle_count} users have been followed.')  

            #24 hour counter
            with open('posh_save_followers.pkl', 'wb') as f: 
                time_list.append(round(time.time()))
                pickle.dump(time_list, f)
                if len(time_list) >= 10000:
                    print(f"x{len(time_list)} users have been followed in the past 24 hours. Let's take a break!")
                    break       
        except:
            print('\t**[error]** A follow was missed.')
    
    
def deploy():
    debugger()
    print(f'[*] Starting on: {time.asctime( time.localtime(time.time()) )}')
    time_list = follows_in_past_24()
    print(f'[*] x{len(time_list)} users have been followed in the past 24 hours')
    starttime = time.time()

    follow(time_list)

    print(f'Finishing on: {time.asctime( time.localtime(time.time()) )}')
    print(f'[*] This cycle took {round((time.time() - starttime) / 60)} minutes.')

if __name__=="__main__":

    driver = webdriver.Firefox()
    log_in()
    #scroll_page()
    input("\n*****Return any key when you are ready to start!*****")
    follow_icons = get_closet_follow_icons()
    deploy()