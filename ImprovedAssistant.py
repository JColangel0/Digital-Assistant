# PERSONAL ASSISTANT AI V.4.0

import pyttsx3
import speech_recognition as sr
import datetime
import time
import pyjokes
import wikipedia
import smtplib
import requests
from bs4 import BeautifulSoup
import webbrowser
import wolframalpha

dt = datetime.datetime.now()
engine = pyttsx3.init()

f = open("docs/Presets.txt", "r")
content = f.readlines()

voices = engine.getProperty('voices')
engine.setProperty("rate", float(content[0]))
engine.setProperty('voice', voices[0].id)

title = str(content[1])
title.replace("\n", "")
timeoutVal = content[2]
phraseLimitVal = content[3]
voiceIncRate = content[4]

tellDailyNews = True
if content[5] == dt.strftime("%B %d, %Y"):
    tellDailyNews = False

f.close()


def speak(audio):
    print(audio)
    engine.say(audio)
    engine.runAndWait()


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                print("Listening")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(
                    source, float(timeoutVal), float(phraseLimitVal))
                Query = r.recognize_google(audio, language='en-us')
                print(Query)
                break
            except Exception as e:
                print(e)
                speak("Say that again "+title)
        return Query.lower()


def sendEmail():
    gmail_user = 'assistantsam10@gmail.com'
    gmail_password = 'Grades#123'
    sent_from = "S.A.M."

    speak("Who would you like to email "+title+"?")
    f = open("contacts.txt", "r")
    to = takeCommand()
    data = f.read()
    contact = ""
    if to.upper() in data:
        contact = data[len(to)+2:data.index("..")]
        to = contact

    speak("What would you like to say "+title+"?")
    body = takeCommand()

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, body)
        smtp_server.sendmail()
        smtp_server.close()
        speak("Email sent successfully!")
    except Exception as ex:
        speak("Something went wrong…"+ex)


def greeting():
    now = datetime.datetime.now()
    ch = now.strftime("%H")
    if dt.strftime("%p") == "AM":
        speak("Good Morning "+title)
    elif '12' in ch or '13' in ch or '14' in ch or '15' in ch or '16' in ch:
        speak("Good Afternoon "+title)
    else:
        speak("Good Evening "+title)


def diagnostic():
    f = open("Presets.txt", "r")
    content = f.readlines()
    speak("Voice rate: " + content[0])
    speak("Pause Threshold: "+content[2])
    speak("Phrase Limit: "+content[3])
    speak("Voice Increment Value: "+content[4])
    f.close()


def changeTitle():
    global title
    speak("What would you like your new title to be?")
    newTitle = takeCommand()
    title = newTitle


def saveChanges():
    f = open("docs/Presets.txt", "w")
    f.write(str(engine.getProperty("rate"))+"\n")
    f.write(title)
    f.write("\n"+str(timeoutVal))
    f.write(str(phraseLimitVal))
    f.write(str(voiceIncRate))
    f.close()


def dictateMode():
    speak("What would you like the document name to be?")
    docName = takeCommand()
    f = open("docs/"+docName+".txt", "w")
    speak("Beginning dictation")
    f.write(takeCommand())
    f.close


def editFile(fName):
    if fName == None:
        speak("Which file am I editing "+title+"?")
        fName = takeCommand()
        if fName == "database":
            f = open("docs/database.txt", "a")
            f.write(takeCommand())
            f.write("..\n")
            f.close()
        else:
            try:
                f = open("docs/"+fName+".txt", "a")
                f.write(takeCommand())
                f.write(" ")
                f.close()
            except:
                speak("No such file could be found "+title)
    else:
        if fName == "database":
            f = open("docs/database.txt", "a")
            data = takeCommand()
            keyword = data[:data.index("?")]
            keyword = keyword.upper()
            finalData = keyword+data[data.index("?"):]
            f.write(finalData)
            f.write("..\n")
            f.close()
        else:
            try:
                f = open("docs/"+fName+".txt", "a")
                f.write(takeCommand())
                f.write(" ")
                f.close()
            except:
                speak("No such file could be found "+title)


def readFile(file):
    try:
        if file == None:
            speak("Which file am I reading "+title+"?")
            fileName = takeCommand()
            f = open("docs/"+fileName+".txt", "r")
            speak(f.read())
            f.close()
        else:
            f = open("docs/"+file+".txt", "r")
            speak(f.read())
            f.close()
    except:
        speak("No such file could be found "+title)


def monitor_web():
    f = open("docs/web_monitor.txt", "r")
    data = f.readlines()
    counter = 0
    while counter < len(data):
        scrapeSite(data[counter].replace("\n", ""),
                   data[counter+1].replace("\n", ""), 10)
        counter += 2


def scrapeSite(url, element, limit):
    speak("Top results from "+url+"\n")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    page = soup.find_all(element)
    counter = 1
    for x in list(dict.fromkeys(page)):
        if counter <= limit:
            speak(x.text.strip())
            counter += 1
    speak("\n")


def search(string):
    finalVal = ""
    values = [True, True, True]
    unwanted = ["search", "for", "on", "about", "information",
                "tell", "me", "everything", "what", "you", "know"]
    words = string.split()
    searchVal = ""
    for x in words:
        if x not in unwanted:
            searchVal += x+" "
    searchVal = searchVal[:-1]
    try:
        f = open("docs/"+searchVal+".txt", "r")
        f.close()
    except:
        values[0] = False
    df = open("docs/database.txt", "r")
    baseData = df.read()
    if searchVal.upper() not in baseData:
        values[1] = False
    try:
        wikiData = wikipedia.summary(searchVal, 2)
    except:
        values[2] = False
    if values[0]:
        finalVal += "I found a file named "+searchVal+"\n"
    if values[1]:
        start = baseData.index(searchVal.upper())
        stop = baseData[start:].index("..")+start
        finalVal += "From my database: " + baseData[start:stop]+"\n"
    if values[2]:
        finalVal += "From Wikipedia: "+wikiData
    speak(finalVal)


def listenMode():
    global tellDailyNews
    now = datetime.datetime.now()
    ch = now.strftime('%H:%M')
    speak("Entering sleep mode "+title)
    while True:
        try:
            time.sleep(60)
            if ch == '23:59':
                tellDailyNews = True
        except KeyboardInterrupt:
            break
    takeCommand()


def updateDatabase():
    speak("Which section are we updating "+title+"?")
    section = takeCommand().upper()
    print(section)
    f = open("docs/database.txt", "r")
    data = f.read()
    if section in data:
        start = data.index(data[data.index(section)+len(section)+2:])
        speak("What would you like to add, "+title+"?")
        newSec = data[start:data[start:].index("..")+start]+" | "+takeCommand()
        fn = open("docs/database.txt", "w")
        fn.write(data.replace(
            data[start:data[start:].index("..")+start], newSec))
        fn.close()
    else:
        speak("I could not find that section " +
              title+". Would you like to add it?")
        answer = takeCommand()
        if "yes" in answer:
            editFile("database")
    f.close()


def getNews(stopIndex, url, openOption):
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = soup.find('body').find_all('h3')
    unwanted = ['BBC World News TV', 'BBC World Service Radio',
                'News daily newsletter', 'Mobile app', 'Get in touch']
    counter = 1

    for x in list(dict.fromkeys(headlines)):
        if x.text.strip() not in unwanted and counter <= stopIndex:
            speak(x.text.strip())
            counter += 1

    if openOption == True:
        speak("Would you like to read these articles?")
        answer = takeCommand()
        if "yes" in answer:
            if "tech" in answer or "technology" in answer:
                webbrowser.open("https://www.bbc.com/news/technology")
            elif "science" in answer:
                webbrowser.open(
                    "https://www.bbc.com/news/science_and_environment")
            else:
                webbrowser.open('https://www.bbc.com/news')


def getWeather():
    response = requests.get(
        "https://weather.com/weather/today/l/1df7354798a71c2a87c94fad701382c964decc25e1250e3ec34e7739d42b41e7")
    soup = BeautifulSoup(response.text, 'html.parser')
    rawTime = soup.find(
        "span", {"class": "CurrentConditions--timestamp--23dfw"})
    rawTemp = soup.find(
        "span", {"class": "CurrentConditions--tempValue--3a50n"})
    rawConditions = soup.find(
        "div", {"class": "CurrentConditions--phraseValue--2Z18W"})
    rawForecast = soup.find(
        "div", {"class": "CurrentConditions--precipValue--3nxCj"})
    for x in list(dict.fromkeys(rawTime)):
        time = x.text.strip()
    for x in list(dict.fromkeys(rawTemp)):
        temp = x.text.strip()
    for x in list(dict.fromkeys(rawConditions)):
        conditions = x.text.strip()
    try:
        for x in list(dict.fromkeys(rawForecast)):
            forecast = " There is a "+x.text.strip()
    except:
        forecast = ""
    speak(
        time+", the weather is " + conditions +
        " and it is "+temp+"." + forecast
    )


def dailyGreeting():
    d = datetime.datetime.now()
    greeting()
    speak("Today is "+d.strftime("%B %d, %Y") +
          "."+" It is "+d.strftime("%X")+" "+d.strftime("%p"))
    getWeather()
    speak("Today's top headlines are: ")
    getNews(3, 'https://www.bbc.com/news', False)
    speak("Top headlines in technology today are: ")
    getNews(3, "https://www.bbc.com/news/technology", False)
    speak("Top headlines in science today are: ")
    getNews(3, "https://www.bbc.com/news/science_and_environment", False)
    speak("Have a great day, "+title)
    f = open("docs/Presets.txt", "r+")
    data = f.readlines()
    data[5] = d.strftime("%B %d, %Y")
    stringdata = ""
    for x in data:
        stringdata += x
    f.write(stringdata)
    f.close()


def question(string):
    if "what" in string:
        question = string[string.index("what"):]
    elif "who" in string:
        question = string[string.index("who"):]
    else:
        speak("Your question could not be answered")
    app_id = "5AJ3J5-8XHYG8KQVL"
    client = wolframalpha.Client(app_id)
    response = client.query(question)
    speak(next(response.results).text)


def process(input):
    if "thank" in input:
        speak("You're quite welcome "+title +
              ", I do everything I can to please you")
    elif "hello" in input:
        speak("Hello "+title)
    elif "date" in input or "time" in input:
        speak(dt.strftime("%c"))
    elif "diagnostic" in input:
        diagnostic()
    elif "change" in input and "title" in input:
        changeTitle()
    elif "say" in input and "something" in input:
        speak("Are we testing audio output "+title +
              ", or do you just love the sound of my voice?")
    elif "dictation" in input:
        dictateMode()
    elif "edit" in input and "file" in input:
        editFile(None)
    elif "read" in input:
        readFile(None)
    elif "search" in input or ("tell" in input and "about" in input) or "about" in input:
        search(input)
    elif "mode" in input:
        if "sleep" in input:
            listenMode()
        elif "problem" in input:
            spoken = ""
            while True:
                spoken += takeCommand()
                spoken += " "
                if "end session" in spoken:
                    break
    elif "tell" in input and "joke" in input:
        speak(pyjokes.get_joke(language='en'))
    elif "add" in input and "database" in input:
        editFile("database")
    elif "email" in input:
        sendEmail()
    elif "update" in input and "database" in input:
        updateDatabase()
    elif "capabilities" in input:
        speak(
            "I am capable of many things "+title +
            ". I can send emails, run diagnostics, perform dictations, read or edit files, or search for or in files. " +
            "I can also search the web, my own databases, and enter sleep mode or problem mode. Would you like to hear my keywords?"
        )
    elif "news" in input:
        getNews(5, 'https://www.bbc.com/news', True)
    elif "weather" in input:
        getWeather()
    elif "question" in input:
        question(input)
    elif "monitor" in input and "update" in input:
        monitor_web()


if __name__ == "__main__":
    if tellDailyNews == True:
        dailyGreeting()
        tellDailyNews = False
    else:
        greeting()

    while True:
        query = takeCommand()
        if "good night" in query or "goodnight" in query or "shutdown" in query or "shut down" in query:
            saveChanges()
            exit()
        else:
            process(query)
