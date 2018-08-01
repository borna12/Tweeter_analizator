from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import os
import sys
import csv
import tweepy
import matplotlib.pyplot as plt
from collections import Counter
from aylienapiclient import textapi


## Twitter credentials
consumer_key = "BmNiYupIhKuHdzbkCx1VMdtvr"
consumer_secret = "WH1RGba0ediS0rpNHkynTZjXNvwBFaLW7IJwiAxkH3hE02zSw4"
access_token = "1023580625083805696-f7q17RjvvLi25uRxkbQ3PYl4pJthgI"
access_token_secret = "lDi4SYquIcPJ0K0ILlA8GtdulG6EpXhNRthKWx3hpUfTL"

## AYLIEN credentials
application_id = "586cb424"
application_key = "04fce1273ed7e09571631f4b38401bfc"

## set up an instance of Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

## set up an instance of the AYLIEN Text API
client = textapi.Client(application_id, application_key)



def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def dohvati():
    query = unesi_rijec.get()
    if len(query)==0:
        oznaka_trazenja.config(text="ne možete tražiti prazni pojam")
        return
    number = "61"
    results = api.search(
    lang="en",
    q=query + " -rt",
    count=number,
    result_type="recent"
    )
    print("--- Gathered Tweets \n")
    oznaka.grid(row=4,column=1,padx=10,pady=10,columnspan=1)
    oznaka2.grid(row=4,column=2,padx=10,pady=10,columnspan=1)
    oznaka3.grid(row=5,column=1,padx=10,pady=10,columnspan=2)

    tree.heading('#0', text='Tweet')
    tree.column('#0', width=710)
    
    tree.heading('#1', text='Mišljenje', anchor='w')
    tree.column('#1',width=70)

    tree.grid(row=3, column=0, columnspan=6,padx=5,pady=5,  sticky=W+E)
    ##skroler
    scrollbar.grid(sticky=N+S+E, row = 3, column = 0,columnspan=6)
    tree.config(yscrollcommand=scrollbar.set) 
    scrollbar.config(command=tree.yview)
    root.geometry("800x400")
    center(root)
## open a csv file to store the Tweets and their sentiment 
    file_name = 'Sentiment_Analysis_of_{}_Tweets_About_{}.csv'.format(number, query)

    with open("tablica.csv", 'w', newline='') as csvfile:
        csv_writer = csv.DictWriter(
            f=csvfile,
            fieldnames=["Tweet", "Sentiment"]
        )
        csv_writer.writeheader()

        print("--- Opened a CSV file to store the results of your sentiment analysis... \n")

        ## tidy up the Tweets and send each to the AYLIEN Text API
        for c, result in enumerate(results, start=1):
            tweet = result.text
            tidy_tweet = tweet.strip().encode('ascii', 'ignore')

            if len(tweet) == 0:
                print('Empty Tweet')
                continue

            response = client.Sentiment({'text': tidy_tweet})
            csv_writer.writerow({
                'Tweet': response['text'],
                'Sentiment': response['polarity']
            })
            if (response['polarity']=="positive"):
                sentiment="pozitivno"
            elif (response['polarity']=="negative"):
                sentiment="negativno"
            else:
                sentiment="neutralno"
            tree.insert('', 'end', text=response['text'],values=sentiment)
            print("Analyzed Tweet {}".format(c))

        ## count the data in the Sentiment column of the CSV file 
    with open("tablica.csv", 'r') as data:
        counter = Counter()
        for row in csv.DictReader(data):
            counter[row['Sentiment']] += 1

        positive = counter['positive']
        negative = counter['negative']
        neutral = counter['neutral']

    ## declare the variables for the pie chart, using the Counter variables for "sizes"
    oznaka.config(text="Broj pozitivnih mišljenja: "+ str(positive))
    oznaka2.config(text="Broj negativnih mišljenja: "+ str(negative))
    oznaka3.config(text="Broj neutralnih mišljenja: "+ str(neutral))
    colors = ['green', 'red', 'grey']
    sizes = [positive, negative, neutral]
    labels = 'pozitivno', 'negativno', 'neutralno'

    ## use matplotlib to plot the chart
    plt.pie(
    sizes,
    shadow=True,
    colors=colors,
    labels=labels,
    startangle=90,
    autopct="%1.1f%%"
    )
    plt.axis('equal')
    plt.title("Mišljenje {} novih tweetova koje sadrže {}".format(number, query))
    plt.savefig('slika.png')
    plt.show()
    oznaka_trazenja.config(text="pretraživanje završeno")


root = Tk()

unesi_rijec=ttk.Entry(root,text="...")
unesi_rijec.grid(row=1,column=1,padx=10,pady=10, columnspan=1)

pretrazi=ttk.Button(root,text="pretraži pojam", command=dohvati)
pretrazi.grid(row=1,column=2, padx=10,pady=10, columnspan=1)


oznaka=Label(root,text="Br. pozitivnih mišljenja: ")

oznaka2=Label(root,text="Br. negativnih mišljenja: ")
oznaka3=Label(root,text="Br. neutralnih mišljenja: ")
tree = ttk.Treeview(root,columns=("Tweet"), selectmode="extended")
scrollbar = Scrollbar(root,orient="vertical")
oznaka_trazenja=ttk.Label(root,text="pretraživanje može potrajati")
oznaka_trazenja.grid(row=2, columnspan=2, column=1)

center(root)
root.title("Analizator")
root.iconbitmap(r"favicon.ico")
root.resizable(False, False)
root.mainloop()