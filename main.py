import subprocess
from datetime import datetime
from src.graph.render_snapshot import render_snapshot
from src.proxy.proxy import Proxy
from src.report.report import generate_report, list_requests
from tabulate import tabulate
import sys
import os

from src.snapshot.snapshot import parse_har_to_snapshot, compare_snapshots


def print_help():
    """
    Displays the help message for the application.
    """
    print("""
    Usage: command [parameters]
    
    Available commands:
      crawl <crawler> <name> <url> <proxy_port> : Start CrawlJax or BlackWidow for the given url and save the result as <name>.har
      proxy <name> <url> : Start the proxy without a Crawler for manual crawling 
      list : List the snapshot files
      compare <snap1> <snap2> <report_filename> : Compare two snapshots and generate a report
      show <snap> <report_filename> : Lists the requests in a snapshot to terminal or to filename if provided
      help : Show this help
    """)


if len(sys.argv) == 1:
    print_help()
    sys.exit()

action = sys.argv[1]

snapshot_directory = './har_exports'

if action == "crawl":
    crawler = sys.argv[2]
    name = sys.argv[3]
    url = sys.argv[4]
    proxy_port = 8080
    if len(sys.argv)  == 6:
        proxy_port = sys.argv[5]

    print(f"proxy port: {proxy_port}")
    if "CrawlJax" == sys.argv[2]:
        crawl_cmd = f"java -jar crawler/CrawlJax/target/CrawlJax-1.0-SNAPSHOT-jar-with-dependencies.jar {url} {proxy_port}"
    elif "BlackWidow" == sys.argv[2]:
        crawl_cmd = f"cd crawler/BlackWidow && python3 crawl.py --url {url} --proxy 127.0.0.1:{proxy_port}"
    else:
        print("Invalid crawler specified. Use CrawlJax or BlackWidow")
        sys.exit()
    proxy = Proxy(os.path.join(snapshot_directory, name + '.har'), proxy_port)
    domain_f = open(os.path.join(snapshot_directory, name + '.domain.txt'), 'w')
    domain_f.write(url)

    subprocess.run(crawl_cmd, shell=True)
    proxy.stop()
elif action == "list":
    snapshot_files = [f for f in os.listdir(snapshot_directory) if os.path.isfile(os.path.join(snapshot_directory, f))]
    table_data = []
    for snapshot_file in snapshot_files:
        if '.har' in snapshot_file:
            snapshot_name = snapshot_file.rstrip('.har')
            file_date = os.path.getmtime(os.path.join(snapshot_directory, snapshot_file))
            table_data.append([snapshot_name, datetime.fromtimestamp(file_date).strftime("%Y-%m-%d %H:%M:%S")])
    print(tabulate(table_data, headers=('Snapshot name', 'Created at')))
elif action == "proxy":
    name = sys.argv[2]
    url = sys.argv[3]
    proxy = Proxy(os.path.join(snapshot_directory, name + '.har'))
    domain_f = open(os.path.join(snapshot_directory, name + '.domain.txt'), 'w')
    domain_f.write(url)
    input("Press Enter to stop proxy after crawling...")
    proxy.stop()

elif action == "compare":
    snap1_name = sys.argv[2]
    snap2_name = sys.argv[3]
    compare_name = f'{snap1_name}-{snap2_name}'
    report_filename = f'reports/report_{compare_name}.txt'
    if 4 in sys.argv:
        report_filename = sys.argv[4]
    snap1 = parse_har_to_snapshot(snap1_name, snapshot_directory)
    snap2 = parse_har_to_snapshot(snap2_name, snapshot_directory)
    compare_snapshots(snap1, snap2, compare_name)
    render_snapshot(snap1, snap2, compare_name)
    generate_report(snap1, snap2, report_filename)

elif action == "show":
    snap1_name = sys.argv[2]
    report_filename = ''
    if len(sys.argv) == 4:
        report_filename = sys.argv[3]
    snap1 = parse_har_to_snapshot(snap1_name, snapshot_directory)
    render_snapshot(snap1)
    print(list_requests(snap1, report_filename))

elif action == "help":
    print_help()

else:
    print("command not found")
    print_help()
