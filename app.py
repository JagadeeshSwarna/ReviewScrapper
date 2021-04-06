# from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS,cross_origin
# import requests
# from bs4 import BeautifulSoup as bs
# from urllib.request import urlopen as uReq
# import re
# app = Flask(__name__)
#
# @app.route('/',methods=['GET'])  # route to display the home page
# @cross_origin()
# def homePage():
#     return render_template("index.html")
#
# @app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
# @cross_origin()
# def index():
#     if request.method == 'POST':
#         try:
#             searchString = request.form['content'].replace(" ","")
#             flipkart_url = "https://www.flipkart.com/search?q=" + searchString
#             uClient = uReq(flipkart_url)
#             flipkartPage = uClient.read()
#             uClient.close()
#             flipkart_html = bs(flipkartPage, "html.parser")
#             bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
#             del bigboxes[0:3]
#             box = bigboxes[0]
#             productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
#             prodRes = requests.get(productLink)
#             prodRes.encoding='utf-8'
#             prod_html = bs(prodRes.text, "html.parser")
#             print(prod_html)
#             commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
#
#             filename = searchString + ".csv"
#             fw = open(filename, "w")
#             headers = "Product, Customer Name, Rating, Heading, Comment \n"
#             fw.write(headers)
#             reviews = []
#             for commentbox in commentboxes:
#                 try:
#                     #name.encode(encoding='utf-8')
#                     name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
#
#                 except:
#                     name = 'No Name'
#
#                 try:
#                     #rating.encode(encoding='utf-8')
#                     rating = commentbox.div.div.div.div.text
#
#
#                 except:
#                     rating = 'No Rating'
#
#                 try:
#                     #commentHead.encode(encoding='utf-8')
#                     commentHead = commentbox.div.div.div.p.text
#
#                 except:
#                     commentHead = 'No Comment Heading'
#                 try:
#                     comtag = commentbox.div.div.find_all('div', {'class': ''})
#                     #custComment.encode(encoding='utf-8')
#                     custComment = comtag[0].div.text
#                 except Exception as e:
#                     print("Exception while creating dictionary: ",e)
#
#                 mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
#                           "Comment": custComment}
#                 reviews.append(mydict)
#             return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
#         except Exception as e:
#             print('The Exception message is: ',e)
#             return 'something is wrong'
#     # return render_template('results.html')
#
#     else:
#         return render_template('index.html')
#
# if __name__ == "__main__":
#     #app.run(host='127.0.0.1', port=8001, debug=True)
# 	app.run(debug=True)
#
#
#
#
# # doing necessary imports

from flask import Flask, render_template, request
from flask_cors import CORS,cross_origin
import requests
import re
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)  # initialising the flask app with the name 'app'

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","") # obtaining the search string entered in the form
        try:
            dbConn = pymongo.MongoClient("mongodb+srv://Jaga:12345@clusterjagadeesh.f6iyx.mongodb.net/test")  # opening a connection to Mongo
            db = dbConn['crawlerDB'] # connecting to the database called crawlerDB
            reviews = db[searchString].find({}) # searching the collection with the name same as the keyword
            if reviews.count() > 0: # if there is a collection with searched keyword and it has records in it
                return render_template('results.html',reviews=reviews) # show the results to user
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString # preparing the URL to search the product on flipkart
                uClient = uReq(flipkart_url) # requesting the webpage from the internet
                flipkartPage = uClient.read() # reading the webpage
                uClient.close() # closing the connection to the web server
                flipkart_html = bs(flipkartPage, "html.parser") # parsing the webpage as HTML
                bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"}) # seacrhing for appropriate tag to redirect to the product link
                del bigboxes[0:3] # the first 3 members of the list do not contain relevant information, hence deleting them.
                box = bigboxes[0] #  taking the first iteration (for demo)
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] # extracting the actual product link
                prodRes = requests.get(productLink) # getting the product page from server
                prod_html = bs(prodRes.text, "html.parser") # parsing the product page as HTML
                nextbox = prod_html.find_all('div', {'class': "col JOpGWq"}) # finding the HTML section containing the customer comments
                nexturl1 = nextbox.find_all('a', href=True)
                nexturl1 = str(nexturl1[-1])
                number_of_revs =int((re.findall(r'All (.+?) reviews',nexturl1))[0])
                if number_of_revs>9900:
                    number_of_revs = 9900
                subStr = re.findall(r'<a href=(.+?)>', nexturl1)
                nexturl = "https://www.flipkart.com" + subStr[0][1:-1]
                prodRes = requests.get(nexturl)
                prod_html = bs(prodRes.text, "html.parser")
                page = 1
                table = db[searchString] # creating a collection with the same name as search string. Tables and Collections are analogous.
                #filename = searchString+".csv" #  filename to save the details
                #fw = open(filename, "w") # creating a local file to save the details
                #headers = "Product, Customer Name, Rating, Heading, Comment \n" # providing the heading of the columns
                #fw.write(headers) # writing first the headers to file
                reviews = [] # initializing an empty list for reviews
                while number_of_revs > 0:
                    page += 1
                    prod_html = bs(prodRes.text, "html.parser")
                    commentboxes = prod_html.find_all('div', {
                        'class': "_27M-vq"})  # finding the HTML section containing the customer comments
                    count = 0
                    if page == 1000:
                        break
                    number_of_revs -= 10
                #  iterating over the comment section to get the details of customer and their comments
                    for commentbox in commentboxes:
                        try:
                            name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                        except:
                            name = 'No Name'

                        try:
                            rating = commentbox.div.div.div.div.text

                        except:
                            rating = 'No Rating'

                        try:
                            commentHead = commentbox.div.div.div.p.text
                        except:
                            commentHead = 'No Comment Heading'
                        try:
                            comtag = commentbox.div.div.find_all('div', {'class': ''})
                            custComment = comtag[0].div.text
                        except:
                            custComment = 'No Customer Comment'
                        #fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
                        mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                                  "Comment": custComment} # saving that detail to a dictionary
                        x = table.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection
                        reviews.append(mydict) #  appending the comments to the review list
                    if nexturl.find('&page=') == -1:
                        nexturl += '&page=' + str(page)
                    else:
                        loc_of_pg_equal = nexturl.rfind('=')
                        nexturl = nexturl[:loc_of_pg_equal + 1] + str(page)

                    prodRes = requests.get(nexturl)
                return render_template('results.html', reviews=reviews) # showing the review to the user
        except:
            return 'something is wrong'
            #return render_template('results.html')
    else:
        return render_template('index.html')
if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)