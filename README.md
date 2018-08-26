# BlanQ 
- [**Get the BlanQ android app from the PlayStore**](https://play.google.com/store/apps/details?id=com.shrikanthravi.blanq)
- View demo [here](https://drive.google.com/open?id=1Zaln9xPbPbJPNeXAJbFaHapuSZ47PQkB). 
  - Quiz on Topic : Chennai -> Architecture
  - Quiz on PDF : Document about History of Android 
  - Quiz on Text : Introduction to [Battle of Plassey](https://en.wikipedia.org/wiki/Battle_of_Plassey) from Wikipedia
 - [Bonus demo](https://drive.google.com/open?id=1sooMJv8jrPLpddTcyz-su91ygJAxSc5x) : Quiz on Game of Thrones
## Using NLP to generate Multiple-Choice Questions from any document
- Statistically determines best entities to blank
- Generate semantically similar options based on context and corpus
- Better than subjective questions
    MC questions tests student's understanding of concepts and can exhibit broad ranges of difficulty,
    probe different cognitive processes and, therefore, test different levels of under- standing.

# Problem
Quiz creation currently requires
- Manual effort,
- Making  the process difficult to adapt and scale. 

## Features 
### Generate quiz
- From any document
- On any topic in any genre (Educational or Recreational)
- From any paragraph

## Scope
- Competitive Exams 
- Quiz Games
- Test knowledge on any topic or book
- Helps students learn without any adult supervision

# Incentivizing kids to learn
- Requires RaspberryPi controlling power of TV
- Kids can click on "Submit" after each quiz
  - Score is sent to a Flask Server (PiServer.py) running on Pi
  - If `score > 70`, an hour of TV (viewing time) is added to timeout
  
Note : Quality of questions generated from PDFs depends on PDF and text parsed from PDF.
