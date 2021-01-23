import os, pickle, time
os.getcwd

def shares_in_past_24():
    #opens saved file
    with open ('posh_save.pkl', 'rb') as f: 
        time_list = pickle.load(f)

    #updates list to only include timestamps that were made within 24h
    time_list = [t for t in time_list if round(time.time()) - t < 86400] 

    #overwrites save file with the updated list
    with open('posh_save.pkl', 'wb') as f: 
        pickle.dump(time_list, f)

    return(time_list) 

time_list = shares_in_past_24()
print(f'[*] x{len(time_list)} items have been shared in the past 24 hours')

with open('posh_save.pkl', 'wb') as f: 
    time_list.append(round(time.time()))
    pickle.dump(time_list, f)