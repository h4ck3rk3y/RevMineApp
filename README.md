# RevMine

Make that buying decision.

## Components

#Core
- Core *RevMine* contains the server side code.
- There are different scrapers for Flipkart, Snapdeal and Amazon.in
- The script nlp_dep.py gathers insights out of the reviews.
- api.py runs on `flask`.

#Extension
- js/ images/ css/ contain assets for the extension
- popup.html, popup.js and bg.js are the main parts of the extension

#Installation

- `$ git clone https://github.com/Zephrys/RevMineApp`
- `$ cd Core`
- Ensure that you have mongodb installed and running.
- Install all the required packages by `$ pip install -r requirements.txt`
- Install twsitd `$ pip install twisted`
- `$ twistd -n web --wsgi api.app --port 8080`

Your backend is now running. Now load up the extension.

- `git clone https://github.com/Zephrys/RevMineExtension`
- Load it up in chrome browser
- Go to product of choice
- Profit??
