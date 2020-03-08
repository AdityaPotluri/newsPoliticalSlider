
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from pprint import pprint
from newsapi import NewsApiClient


txt="newsbias.txt"
newsapi = NewsApiClient(api_key='probably should not post this online?')

#uses the NewsApiClient to, given a list of sources, produce a JSON list of all articles available
def get_news(source_list):
    top_headlines = newsapi.get_everything(
                                          domains=(",").join(source_list),
                                          language='en',
                                          )

    return top_headlines['articles'][:8]
    

#rescales the score so that instead of -100 to 100 they go from 0 to 100
def zeroToHundred(scores):
    score=int(scores.split(",")[1])
    if(score<0):
        return 50-((-score)/2)
    return 50+score/2

#generates a dictionary of news to their respective scores and returns it
def newsToScore(txt_file):
    txt_file=open(txt_file,"r")
    news_bias=txt_file.readlines()
    news=[news.split(",")[0] for news in news_bias]
    bias=[zeroToHundred(scores) for scores in news_bias]
    return dict(zip(news,bias))

newsScore=newsToScore(txt)

#given the bias entered by the user the function will return the news sources within 
# 10 points of that bias if not enough sources are found it will return within a broader range
def create_source_list(bias,newsToScore=newsScore):
    specificSources=[key for key in newsToScore.keys() if bias-15<newsToScore[key]<bias+15]
    broaderSources=[key for key in newsToScore.keys() if bias-30<newsToScore[key]<bias+20]
    if(len(specificSources)>2):
        return specificSources
    else:
        return broaderSources



app = Flask(__name__)


@app.route('/',methods=['GET','POST'])
def mainPage():
    if(request.method=="POST"):
        value=100-int((request.form['range_slider']))
        news=get_news(create_source_list(value))
        
        return render_template('MainPage.html',value=value)
    else:
        return render_template('MainPage.html')
    

if __name__ == '__main__':
    app.run()
