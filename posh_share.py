import selenium, time, numpy, winsound, pdb, credentials, pickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


#random number generator. adds 0<2 seconds to d(delay between clicks)
def rt(d): 
    times = float(sum(numpy.random.random(2))) + d
    return times


#checks if there is a captcha
#essentially pauses script by entering debugger mode if so
#resolve captcha and then 'continue' out of captcha
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

  
#directs to poshmark url and enters user's credentials from credentials.py
#directs to closet and filters 'available items only'
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
    
    print('[*] Heading to closet and displaying only available listings. ')
    
    driver.get('https://poshmark.com/closet/taylorcarey3?availability=available&all_size=true&my_size=false')
    time.sleep(rt(2))
    

#scrolls to bottom of page to load all items
def scroll_page(delay=5):
    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    print("[*] Scrolling through all items in closet. This will take a moment...")

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
 


def shares_in_past_24():
    #opens saved file
    with open ('posh_save.pkl', 'rb') as f: 
        try:
            time_list = pickle.load(f)
        except EOFError:
            time_list = []

    #updates list to only include timestamps that were made within 24h
    time_list = [t for t in time_list if round(time.time()) - t < 86400] 

    #overwrites save file with the updated list
    with open('posh_save.pkl', 'wb') as f: 
        pickle.dump(time_list, f)

    return(time_list)   


#returns an element list of all of the share icons for each item
def get_closet_share_icons():
    item_pat = "//div[@class='d--fl ai--c social-action-bar__action social-action-bar__share']"
    items = driver.find_elements_by_xpath(item_pat)
    build_share_icons = [i.find_element_by_css_selector("html body div#app main div#content.content--desktop div.view div div.grid-page div section.main__column.col-l19.col-x16 div.m--t--1 div.tile.col-x12.col-l6.col-s8.p--2 div.card.card--small div.social-action-bar.tile__social-actions div.d--fl.ai--c.social-action-bar__action.social-action-bar__share i.icon.share-gray-large") for i in items]
    return build_share_icons


#clicks the 'share' button and clicks the prompted 'to my followers' button
def clicks_share_followers(share_icon, d=3.5):

    #First share click (button element location was returned from get_closet_share_icons()
    driver.execute_script("arguments[0].click();", share_icon); time.sleep(rt(d))

    #Second share click (determines button element location first)
    share_pat = "/html/body/div[1]/main/div[1]/div/div/div[2]/div[2]/div[1]/ul/li[1]/a/div/span"
    share_followers = driver.find_element_by_xpath(share_pat)
    driver.execute_script("arguments[0].click();", share_followers); time.sleep(rt(d))

  
#loops through each icon and clicks both share buttons by sending to get_share_followers one at a time
#checks for captcha before each iteration
#returns printed error if a listing was not found, or the scrip lags and misses one
def share(time_list): 
    current_cycle_count=0
    print(f'[*] Preparing to share x{len(share_icons)} items')

    for item in share_icons:
        debugger()
        try:
            clicks_share_followers(item)
            
            current_cycle_count+=1
            print(f'\t{current_cycle_count} items have been shared.')  

            #24 hour counter
            with open('posh_save.pkl', 'wb') as f: 
                time_list.append(round(time.time()))
                pickle.dump(time_list, f)
                 
        except:
            print('\t**[error]** A listing was missed.')


#the actual cycles of sharing. 
#starts a new cycle every two hours and sleeps inbetween    
def deploy():
    debugger()
    c=0
    while True:   
        c+=1
        print(f'\n\n**********Cycle #{c}:**********')        
        print(f'[*] Starting on: {time.asctime( time.localtime(time.time()) )}')
        time_list = shares_in_past_24()
        print(f'[*] x{len(time_list)} items have been shared in the past 24 hours')
        starttime = time.time()

        share(time_list)

        print(f'Finishing on: {time.asctime( time.localtime(time.time()) )}')
        print(f'[*] This cycle took {round((time.time() - starttime) / 60)} minutes.')

        #if the cycle got paused and took longer than 2 hours, it will sleep for 60 minutes
        if 7200-(time.time() - starttime) < 0:
            print(f'[*] Sharing will resume in 60 minutes.')
            time.sleep(3600)
        #a normal cycle sleeps the difference of two hours
        else:
            print(f'[*] Sharing will resume in {round((7200-(time.time() - starttime))/60)} minutes.')
            time.sleep(7200-(time.time() - starttime))
        

#below executes if program is run directly
if __name__=="__main__":

    #loads firefox
    driver = webdriver.Firefox()

    log_in()

    scroll_page()

    #this is unnecessary... 
    #requires a physical prompt to start after logging in and loading the full closet
    input("\n*****Press any key when you are ready to start!*****")

    share_icons = get_closet_share_icons()

    deploy()