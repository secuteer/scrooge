# scrooge
_Detection of Changes in the Functionality of Web Applications_

## Installation
### Install requirements.txt for Python 3 
```
pip install -r ./requirements.txt
```
### Install Proxy
The [mitmproxy](https://mitmproxy.org/) is used as the proxy server.
Installation on Mac OS using Homebrew:
```
brew install mitmproxy
```
Installation for other systems: https://docs.mitmproxy.org/stable/overview-installation/

### Install Webcrawler "CrawlJax"
An installed JDK and Maven are required.
```
cd crawler/CrawlJax
mvn clean
mvn install
mvn compile
mvn assembly:single
```

The .jar file `./crawler/CrawlJax/target/CrawlJax-1.0-SNAPSHOT-jar-with-dependencies.jar` will be created.
If the file path changes on your system, you need to adjust the path in `main.py`.

### Install Webcrawler "Black Widow"
Clone the [BlackWidow](https://github.com/SecuringWeb/BlackWidow) repository into `./crawler/BlackWidow`.
`./crawler/BlackWidow/crawl.py` needs to be adjusted as follows:

```
parser.add_argument("--proxy", help="Proxy URL") # Add argument for proxy server URL
...
proxy_server_url = args.proxy
chrome_options.add_argument(f'--proxy-server={proxy_server_url}')
```
This allows the proxy server to be specified via the URL argument.

If you install BlackWidow in a different path, you need to adjust this in `./main.py`.
#### Notes on BlackWidow
* For BlackWidow, Selenium version 4.2.0 must be installed. If you have a newer version installed, you need to downgrade it.



## CLI-Tool
If all the installation steps have been completed, you can now run the tool. Try it out with:
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


## Tools
### Start Proxy Manually
```
mitmdump --set hardump=./har_exports/dump.har
```
Starts on *:8080

### Start Crawler Manually
#### BlackWidow
```
cd crawler/BlackWidow && python3 crawl.py --url {url}
```

#### CrawlJax
```
java -jar crawler/CrawlJax/target/CrawlJax-1.0-SNAPSHOT-jar-with-dependencies.jar {url} {proxy_port}
```





