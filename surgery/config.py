import requests


class Googler():
    
    def __init__(self):
        s = requests.session()
        s.get('http://www.google.com/ncr')
        s.cookies['CONSENT'] = 'YES+ES.en-GB+20150906-13-0'
        self.session = s
    
    def __call__(self):
        return self

googler = Googler()
