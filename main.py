
import cchardet
import re
import json
from bs4 import BeautifulSoup
from requests_html import HTMLSession

"""
requests_html : permet d'effectuer une requête avec JS 
cchardet :      augmente la vitesse de reconnaissance de l'encodage (source : doc bs4)
lxml :          parser en C, plus rapide que le parser par défaut de bs4
"""


# SEINE-SAINT-DENIS
# n = 629 (24 juillet 2022)
# 2 avocats n'ont pas de mail renseigné
# execute en 51 secondes

class SeineSaintDenis:

    def __init__(self):
        self.start_url = 'https://www.avocats-bobigny.com/index.php?option=com_comprofiler&Itemid=1468'
        self.session = HTMLSession()
        self.json_file = './ssd_mail.json'
        self.mail_dict = {}
        self.total_mails = 0
        self.webmail = ['gmail', 'yahoo', 'icloud']
        self.fai = ['orange', 'wanadoo', 'laposte', 'aol', 'neuf', 'sfr', 'cegetel']
        self.fournisseur_mail = ['protonmail', 'avocat-conseil']

    def crawl(self):
        for i in range(0, 640, 20):
            mail_regex = '(?:.*)@(.*)(?:\.)(?:.*)'
            r = self.session.get(self.start_url+'&limitstart={}'.format(i))
            r.html.render()  # Obligatoire pour activer le JS
            soup = BeautifulSoup(r.html.raw_html, 'lxml')
            trs = soup.tbody.find_all('tr', 'cbUserListRow')
            for tr in trs:
                self.total_mails += 1
                try:
                    email_dom = re.findall(mail_regex, tr.find('span', 'cbMailRepl').a.text)[0]
                    self.populate_dict(self.res_clean(email_dom))
                except AttributeError:
                    pass
        self.json_dumper()

    def populate_dict(self, mail):
        if mail not in self.mail_dict:
            self.mail_dict[mail] = 1
        else:
            self.mail_dict[mail] += 1

    def res_clean(self, email):
        if email == 'ymail':
            return 'yahoo'
        elif email == 'hotmail' or email == 'live' or email == 'outlook':
            return 'microsoft'
        elif email in self.webmail or email in self.fai or email in self.fournisseur_mail:
            return email
        else:
            return 'solo'

    def json_dumper(self):
        data = self.mail_dict
        a = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
        print(a)
        with open(self.json_file, 'w') as jsonfile:
            json.dump(a, jsonfile)
