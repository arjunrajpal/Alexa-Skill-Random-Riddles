from flask import Flask
from flask_ask import Ask, statement, question, session
from bs4 import BeautifulSoup
from unidecode import unidecode
import requests
import random

app = Flask(__name__)
ask = Ask(app, '/get-riddles')


@app.route('/')
def hello_world():
    return "Ready"


@app.route('/get-riddles')
def get_random_riddles():
    url = "https://riddles.fyi/hard-riddles/"

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) '
                         'Chrome/23.0.1271.64 Safari/537.11'}

    req = requests.get(url, headers=hdr, verify=True)

    riddles = req.text

    soup = BeautifulSoup(riddles, 'html.parser')

    riddles = soup.find_all('article')

    results = []

    for i in range(len(riddles)):

        question = unidecode(riddles[i].find('h2', attrs={'class', 'entry-title'}).find('a').text).replace("\"", "")
        answer = unidecode(riddles[i].find('div', attrs={'class', 'su-spoiler-content su-clearfix'}).text).replace("\"", "")

        result = {'question': question, 'answer': answer}
        results.append(result)

    return results


@ask.launch
def launched():
    session.attributes['count'] = 0
    return question("Hi, would you like an interesting riddle ?")


@ask.intent('YES')
def yes():
    riddles = get_random_riddles()

    session.attributes['count'] += 1

    if session.attributes['count'] == 1:
        random.shuffle(riddles)
        return question('<speak>' + riddles[0]['question'] + ' ' + '<break time="1.5s" />' + '<emphasis level="strong">' +
                        riddles[0]['answer'] + '</emphasis>' + '<break time="1s" />' + ' Do you want another one ?' + '</speak>')
    else:
        return statement('<speak>' + riddles[5]['question'] + ' ' + '<break time="1.5s" />' + '<emphasis level="strong">' +
                        riddles[5]['answer'] + '</emphasis>' + '</speak>')


@ask.intent('NO')
def no():
    return statement('Thank you for using Random Riddles. Have a nice day !')


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement('Thank you for using Random Riddles. Have a nice day !')


@ask.intent('AMAZON.HelpIntent')
def help():
    return question('This skill asks you a Random Riddle. Reply with a Yes to get a riddle or No to exit the skill. '
                    'Would you like to start?')


@ask.intent('AMAZON.StopIntent')
def stop():
    return statement('Thank you for using Random Riddles. Have a nice day !')


@ask.intent('AMAZON.FallbackIntent')
def fallback():
    return question("Sorry didn't quite get it, please speak again !")


if __name__ == '__main__':
    app.run(debug=True, port=5000)