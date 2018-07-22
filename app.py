# Crochet permet d'utiliser des applications asynchrones Twisted dans un contexte synchrone.

import crochet
crochet.setup()

from flask import Flask, render_template, request, jsonify
from scrapy.crawler import CrawlerRunner
from scrapper import WebSpider


app = Flask(__name__)

# On defini les parametres de notre Crawler, notamment le nombre de pages Max a crawl.
crawl_runner = CrawlerRunner({
    'CLOSESPIDER_ITEMCOUNT': 2
})

# Variable de stockage des resultats
storage = {}

# Variable de stockage des taches terminées
scrappers_done = {}


@app.route('/process', methods=['POST'])
def process():
    """
    Cette fonction est appelée lors de la soumission du formulaire de crawling.

    Elle fait appel au scrapper avec les parametres du formulaire.

    """
    target_website = request.form.get('website')
    print('Scrapping website : %s' % target_website)
    global storage
    scrape_reactor(target_website, storage)
    return jsonify({'processing': target_website})


def process_done(target_website):
    """
    Callback !

    Cette fonction est appellée quand le scrapping d'un site est terminé.
    """

    print('Scrapping done : %s' % target_website)

    #  Un tableau indique que le crawling du site est terminé.
    scrappers_done[target_website] = True


@crochet.run_in_reactor
def scrape_reactor(target_website, storage):
    """
    Lance le WebSpider.

    :param target_website: Le site à crawler.
    :param storage: Les resultats du crawler seront stockées dans cette variable.
    """
    scrapper = crawl_runner.crawl(WebSpider,
                                  target=target_website,
                                  storage=storage)

    #  Lorsque le crawler sera terminé, la fonction process_done sera appellée.
    scrapper.addCallback(lambda null: process_done(target_website))


@app.route('/results', methods=['POST'])
def results():
    """
    Permet d'obtenir les resultats du crawler.

    Si le crawler n'est pas terminé, alors le lien du site n'est pas disponible dans scrapper_done.
    Si le scrapper est terminé, alors on retourne l'intégralité des resultats renvoyés dans la variable storage.
    """

    website = request.form.get('website')
    if website not in scrappers_done:
        return jsonify({'result': 'PROCESSING'})
    else:
        print(storage)
        return jsonify({'result': 'DONE', 'data': storage[website]})


@app.route('/')
def index():
    return render_template('home.html')


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['FLASK_DEBUG'] = True
    app.run(debug=True)