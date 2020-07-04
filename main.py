import requests
import config as cfg

def switcher():
    choice = cfg.get_setting(path, 'Authentication', 'default')

    if choice == "":
        print ("Press 1  - to login as user, 2 - to login via fb, 3 - to login via google")
        choice = input("Choose: ")
        cfg.update_setting(path, 'Authentication', 'default', choice)
    if choice == "1":
        print("Login using email/pass")
        return auth()
    if choice == "2":
        print("Login using auth via fb")
        return auth_fb()
    if choice == "3":
        print("Login using auth via google")
        return auth_google()
    else:
        print("Not correct option. Try again...")
        switcher()

def auth():
    login = cfg.get_setting(path, 'Authentication', 'Login')
    if login == "":
        login = input("Enter username:")
        cfg.update_setting(path, 'Authentication', 'Login', login)
    password = cfg.get_setting(path, 'Authentication', 'Password')
    if password == "":
        password = input("Enter password:")
        cfg.update_setting(path, 'Authentication', 'Password',password)
    cred = {
        "username": login,
        "password": password,
        "remember": "true"
    }
    with requests.Session() as s:
        p = s.post(url + "/account/login", data=cred)
        r = s.get(url + "/account/login")
        if p.status_code == 204:
            print("Success. Session created...")
            # print(p.json()['message'])
            wlcm_msg = "Hi! " + str(r.json()['firstName']) + " " + str(r.json()['lastName'])
            print(wlcm_msg)
            return s
        else:
            print(p.status_code)
            if p.status_code == 400:
                print("Username/password incorrect. Try again")
            print(p.json()['message'])
            login = cfg.update_setting(path, 'Authentication', 'Login', "")
            password = cfg.update_setting(path, 'Authentication', 'Password', "")
            auth()

def auth_fb():
    token = cfg.get_setting(path, 'Facebook', 'Token')
    if token == "":
        token = input("Enter Facebook token:")
        cfg.update_setting(path, 'Facebook', 'Token', token)
    cred = {
      "token": token
    }
    with requests.Session() as s:
        r = s.get(url + '/login/facebook/token', params=cred)
        if r.status_code == 200:
            print("Success. Session created...")
            return s
        else:
            print(r.json()['message'])
            cfg.update_setting(path, 'Facebook', 'Token', '')
            auth_fb()

def auth_google():
    token = cfg.get_setting(path, 'Google', 'Token')
    if token == "":
        token = input("Enter Google token:")
        cfg.update_setting(path, 'Google', 'Token', token)
    cred = {
      "token": token
    }
    with requests.Session() as s:
        r = s.get(url + '/login/google', params = cred)

def cityId(cityName):
    resp = s.get(url + '/autocomplete/city', params={"term": cityName})
    if cityName == "":
        return 0
    for city in resp.json():
       return city['id']

def get_resume():
    resume = s.get(url + "/resume")
    return resume.json()

def apply(resume, vac, clientID):
    param = {
        "profCv": True,
        "hasCQ": True,
        "cvId": resume,
        "clientId": clientID,
        "vacancyId": vac,
        "addAlert": True
}
    send = s.post(url + "/vacancy/apply", data=param)

    print("ID: " + str(vac) + " Result: " +  str(send.json()['success']))

def clientID():
    return s.get(url + "/account/login").json()['uid']

def choose_resume_id():
    print("Choose one from the list:")
    list = { }
    for res in get_resume():
        print("ID: " + str(res['id']) + "   NAME: " + str(res['name']))
        list[res['id']] = res['name']
    print (list)
    resume_id = input("Paste resume ID: ")
    cfg.update_setting(path, 'Resume', 'id', resume_id)
    cfg.update_setting(path, 'Resume', 'name', list[int(resume_id)])
    return resume_id

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

def search(cityName, keyWords):
    pg = 0
    ids = []
    data = {
        "page": pg,
        "count": "20",
        "cityId": cityId(cityName),
        "keywords": keyWords
    }
    srch = s.get(url + "/vacancy/search",  params=data)
    print("Find total: " + str(srch.json()['total']))
    pgs = int(srch.json()['total'] / 20)
    for pg in range(0, pgs + 1):
        data['page'] = pg
        srch = s.get(url + "/vacancy/search", params=data)
        for vac in srch.json()['documents']:
            if vac['id'] not in get_ids(ids_path):
                ids.append(vac['id'])
        printProgressBar(pg, pgs, prefix='Progress:', suffix='Complete', length=50)
    return ids

def get_ids (path):
    ids = []
    with open(path, "r") as f:
        for id in f:
            ids.append(int(id.rstrip()))
    return ids

def save_ids(path, ids):
    with open(path, "w") as f:
        for id in ids:
            f.write(str(id) + "\n")

url = "https://api.rabota.ua"
path = "settings.ini"
ids_path = "saved_ids.txt"


s = switcher()
clientID = clientID()
print("Your client id:" + str(clientID))

resume_name = cfg.get_setting(path, 'Resume', 'name')
resume_id = cfg.get_setting(path, 'Resume', 'id')
if resume_id == "":
    choose_resume_id()
else:
    choice = input("Do you want to use ID: " + resume_id + " Name: " + resume_name + " (YES/no) ? ")
    if choice == "no":
        choose_resume_id()

cityName = cfg.get_setting(path, 'Resume', 'city')
if cityName == "":
    cityName = input("City name (leave blank for all cities): ")
    cfg.update_setting(path, 'Resume', 'city', cityName)

keyWords = cfg.get_setting(path, 'Resume', 'key')
if keyWords == "":
    keyWords = input("Key words (leave blank to search all): ")
    cfg.update_setting(path, 'Resume', 'key', keyWords)

vac_ids = search(cityName, keyWords)
print("New vacancies count : " + str(len(vac_ids)))
save_ids(ids_path, vac_ids)
ready = input("Do you want to send ?(YES/no): ")
if ready == "no":
    print("Lol")
    quit()
for vac in vac_ids:
    apply(resume_id, vac, clientID)
    # printProgressBar(vac, vac_ids,  prefix='Progress:', suffix='Complete', length=50)
