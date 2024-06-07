# scrooge
_Detektion von Änderungen im Funktionsumfang von Web-Applikationen_

## Installation
### requirements.txt installieren für Python 3 
```
pip install -r ./requirements.txt
```
### Proxy installieren
Als Proxy Server wird [mitmproxy](https://mitmproxy.org/) verwendet.
Installation auf Mac OS mit Homebrew:
```
brew install mitmproxy
```
Installation für andere Systeme: https://docs.mitmproxy.org/stable/overview-installation/

### Webcrawler "CrawlJax" installieren
Es wird eine installiertes JDK und Maven vorausgesetzt.
```
cd crawler/CrawlJax
mvn clean
mvn install
mvn compile
mvn assembly:single
```
Es wird die .jar-Datei `./crawler/CrawlJax/target/CrawlJax-1.0-SNAPSHOT-jar-with-dependencies.jar` erstellt.
Sollte sich der Dateipfad auf deinem System ändern, so musst du den Pfad in `main.py` anpassen.

### Webcrawler "Black Widow" installieren
Klone das Repository [BlackWidow](https://github.com/SecuringWeb/BlackWidow) in `./crawler/BlackWidow`.
`./crawler/BlackWidow/crawl.y` muss folgendermassen angepasst werden:

```
parser.add_argument("--proxy", help="Proxy URL") # Argument für Proxy-Server URL hinzufügen
...
proxy_server_url = args.proxy
chrome_options.add_argument(f'--proxy-server={proxy_server_url}')
```
Dadurch kann das der Proxy-Server mittels URL-Argument mitangegeben werden. 

Solltest du BlackWidow in einem anderern Pfad installieren, so musst du dies in `./main.py` anpassen.
#### Hinweise zu BlackWidow
* Für BlackWidow muss die Selenium-Version 4.2.0 installiert sein. Solltest du eine neuere Version installiert haben, so musst du diese downgraden.



## CLI-Tool
Wenn alle schritte bei Installation durchgeführt wurden, kann nun das Tool ausgeführt werden. Probiere es besten gleich mal aus mit:
```
python main.py help
```
```
Usage: command [parameters]
 
Available commands:
    crawl <crawler> <name> <url> <proxy_port> : Start CrawlJax or BlackWidow for the given url and save the result as <name>.har
    proxy <name> <url> : Start the proxy without a Crawler for manual crawling 
    list : List the snapshot files
    compare <snap1> <snap2> <report_filename> : Compare two snapshots and generate a report
    show <snap> <report_filename> : Lists the requests in a snapshot to terminal or to filename if provided
    help : Show this help
```


## Werkzeuge
### Proxy manuell starten
```
mitmdump -s ./proxy/proxy.py --set hardump=./har_exports/dump.har
```
Startet auf *:8080
### Crawler manuell starten
#### BlackWidow
```
cd crawler/BlackWidow && python3 crawl.py --url {url}
```

#### CrawlJax
```
java -jar crawler/CrawlJax/target/CrawlJax-1.0-SNAPSHOT-jar-with-dependencies.jar {url} {proxy_port}
```





