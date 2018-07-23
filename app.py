# FR - AIDE Crochet permet d'utiliser des applications asynchrones Twisted dans un contexte synchrone.
# EN - HELP With crochet, we can use asynchrones Twisted app in synchrone context/

import crochet
import json
import os
crochet.setup()

from flask import Flask, render_template, request, jsonify
from scrapy.crawler import CrawlerRunner
from scrapper import WebSpider

app = Flask(__name__)

# FR - HELP On defini les parametres de notre Crawler, notamment le nombre de pages Max a crawl.
# EN - HELP Define settings of our crawler, number of max crawl page for example

crawl_runner = CrawlerRunner({
    'CLOSESPIDER_ITEMCOUNT': 2
})

# FR - HELP Variable de stockage des resultats
# EN - HELP We stock the result of our research in :param storage

storage = {}

# FR - HELP Variable de stockage des taches terminées
# EN - HELP We stock completed tasks in :param scrappers_done

scrappers_done = {}


@app.route('/process', methods=['POST'])
def process():
    """
    FR - HELP Cette fonction est appelée lors de la soumission du formulaire de crawling.
    Elle fait appel au scrapper avec les parametres du formulaire.
    EN - HELP This function is called when we click on submit form (on the website). process() calls Scrapp with
    parameter of the send form

    """
    target_website = request.form.get('website')
    print('Scrapping website : %s' % target_website)
    global storage
    scrape_reactor(target_website, storage)
    return jsonify({'processing': target_website})


def process_done(target_website):
    """
    FR - HELP Callback !
    Cette fonction est appellée quand le scrapping d'un site est terminé.

    EN - HELP Callback, we called this function when the scrapping is down
    """

    print('Scrapping done : %s' % target_website)

    # FR - HELP Un tableau indique que le crawling du site est terminé.
    # EN - HELP This array give us a notification when the crawling are down

    scrappers_done[target_website] = True


@crochet.run_in_reactor
def scrape_reactor(target_website, storage):
    """
    FR - HELP Lance le WebSpider.
    :param target_website: Le site à crawler.
    :param storage: Les resultats du crawler seront stockées dans cette variable.

    EN - HELP Run the WebSpider
    :param target_website : target Website to crawl
    :param storage: the result of the crawler

    """
    scrapper = crawl_runner.crawl(WebSpider,
                                  target=target_website,
                                  storage=storage)

    #  Lorsque le crawler sera terminé, la fonction process_done sera appellée.
    scrapper.addCallback(lambda null: process_done(target_website))


@app.route('/results', methods=['POST'])
def results():
    """
    FR - HELP Permet d'obtenir les resultats du crawler.
    Si le crawler n'est pas terminé, alors le lien du site n'est pas disponible dans scrapper_done.
    Si le scrapper est terminé, alors on retourne l'intégralité des resultats renvoyés dans la variable storage.

    EN - HELP Get the crawler result
    If the crawler isn't finished the process, then the website link isn't give in scrapper_done
    If the scrapper is down, then, we give the results in the storage var
    """

    website = request.form.get('website')
    if website not in scrappers_done:
        return jsonify({'result': 'PROCESSING'})
    else:
        #print(storage)
        return jsonify({'result': 'DONE', 'data': storage[website]})


@app.route('/')
def index():
    return render_template('home.html')


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['FLASK_DEBUG'] = True
    app.run(debug=True)


@app.route('/savefile', methods=['POST'])
def savefile():
    jsonarray = request.json
    with open('./static/last-research.json', 'w') as outfile:
        json.dump(jsonarray, outfile)
    with open('./static/all-research.json', 'a') as outfile:
        json.dump(jsonarray, outfile)
    return render_template('home.html')


@app.route('/deletefiles', methods=['GET'])
def deletefiles():
    try:
        os.remove('./static/all-research.json')
        os.remove('./static/last-research.json')
        return jsonify({'result':'true'})
    except ValueError:
        print('Erreur to delete file')
