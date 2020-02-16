import requests
import re
from pyquery import PyQuery

def log(text):
    print('[ LOG ] ', text)

class Jsos():

    def __init__(self, userIndex, userPassword):

        log('Initializing JSOS connector...')

        self.userIndex = userIndex
        self.userPassword = userPassword
        self.isLogged = False
        self.s = requests.session()
        self.cookie = None

        self.page = None    #recent HTML page

        self.jsosUrl = 'https://jsos.pwr.edu.pl/'

        self.pageList = dict()
        self.pageList['mainPage'] = ''
        self.pageList['loginAsStudent'] = 'index.php/site/loginAsStudent'
        self.pageList['logout'] = 'index.php/site/logout'
        self.pageList['messageIndex'] = 'index.php/student/wiadomosci'

    def GetPageUrl(self, page, varList = []):
        if page in self.pageList.keys():
            # add varibles
            # ? var1=value1 & var2=value2
            return self.jsosUrl + self.pageList[page]

        raise ValueError('Unknown page ' + page)

    def Go(self, page, varList = [], type = 'get'):

        if type == 'get':
            self.page = self.s.get(self.GetPageUrl(page))

        elif type == 'post':
            self.page = self.s.post(self.GetPageUrl(page), varList)
          
        else:
            raise ValueError('Unknown type of request: ' + type)

    def RenderPage(self):
        if self.page:
            print(self.page.content)
        return True

    def GetUrlParam(self, url):
        _, paramString = url.split('?')
        out = dict()
        for keyEqualValue in paramString.split('&'):
            key, value = keyEqualValue.split('=')
            out[key] = value

        return out

    def Login(self):

        log('Trying to login...')

        if self.isLogged: 
            log('User already logged in')
            return True
        
        req = dict()
        req['username'] = self.userIndex
        req['password'] = self.userPassword
        req['oauth_request_url'] = 'http://oauth.pwr.edu.pl/oauth/authenticate'
        req['oauth_consumer_key'] = self.oauth_consumer_key
        req['oauth_token'] = self.oauth_token
        req['oauth_locale'] = self.oauth_locale
        req['oauth_callback_url'] = 'https://jsos.pwr.edu.pl/index.php/site/loginAsStudent'
        req['oauth_symbol'] = 'EIS'

        formAction = 'https://oauth.pwr.edu.pl/oauth/'
        formAction += 'authenticate?0-1.IFormSubmitListener-authenticateForm'
        formAction += '&oauth_token=' + self.oauth_token
        formAction += '&oauth_consumer_key=' + self.oauth_consumer_key
        formAction += '&oauth_locale=' + self.oauth_locale

        self.page = self.s.post(formAction, req)

        if self.page.url == 'https://jsos.pwr.edu.pl/index.php/student/indeksDane':
            log('User logged successfully')
            return True

        else:
            log('Login failed')
            return False

    def SavePage(self):
        file = open("page.html", "wt")
        print(self.page.text)
        #file.write(self.page.text)
        file.close()

    def GetAmountOfUnreadMessage(self):

        pq = PyQuery(self.page.text)

        messageTag = pq('span.label.label-success.label-drop')

        return messageTag.text()

    def GetUnreadHeaders(self):
        out = []

        pq = PyQuery(self.page.text)
        unreadList = pq('tr.unread')

        text = unreadList.text().split('\n')

        for i in range(len(text) // 3):
            message = dict()
            message['from'] = text[i*3]
            message['title'] = text[(i*3+1)]
            message['sent'] = text[(i*3+2)]

            out.append(message)


        return out


    def GetMessageHeader(self, element):
        print(element)
        return 'X - X - X'

    def SetSessionToken(self, data):
        log('Fetching session ouath variables...')

        if not data: raise ValueError('Token data is invalid')

        self.oauth_token = data['oauth_token']
        self.oauth_consumer_key = data['oauth_consumer_key']
        self.oauth_locale = data['oauth_locale']

        log('Fetching completed')

        return True


jsos = Jsos('pwrxxxxxx', 'haslo')

jsos.Go('mainPage')
jsos.Go('loginAsStudent')
jsos.SetSessionToken(jsos.GetUrlParam(jsos.page.url))
if not jsos.Login():
    raise ValueError('Login failed')
#now we are in student/indeksDane

#go to message panel
jsos.Go('messageIndex')

unreadMessageList = jsos.GetUnreadHeaders()
for message in unreadMessageList:
    print(message['title'])

jsos.Go('logout')
