#!/usr/bin/env python3
import argparse
import getpass
import sys
import logging

from infosecAPI import learners


def main():
    example = "Usage: %(prog)s -k key.txt -f Scheduled_CSV.csv -p 'http:http://proxy:8080, https:http://proxy:8080'"
    options = argparse.ArgumentParser(epilog=example)
    options.add_argument('-d', '--debug', help='Print debug messages', action='store_true')
    options.add_argument('-q', '--quiet', help="Don't print status messages", action='store_true')
    options.add_argument('-H', '--host', help='Base URL for the api. e.g. https://securityiq.infosecinstitute.com/api/v2/', default="https://securityiq.infosecinstitute.com/api/v2/")
    options.add_argument('-k', '--passfile', help='File containing your api key (Default is to prompt)', required=True)
    options.add_argument('-f', '--user_file', help="CSV file containing AD users", required=True)
    options.add_argument('-p', '--proxies', help='Proxy server address in the form of "http=http://proxy:8080, https=http://proxy:8080"')
    args = options.parse_args()
    
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    if args.quiet:
        log_level = logging.WARNING
    
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(asctime)s: %(filename)s: %(funcName)s: %(lineno)d: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=[
            logging.FileHandler('infosecAPI.log'),
            logging.StreamHandler()]
        )
    
    if args.passfile:
        with open(args.passfile) as f:
            api_key = f.readline().strip()
    else:
        api_key = getpass.getpass()
    
    base_url = args.host
    user_file = args.user_file
    # check for proxies
    if args.proxies:
        logging.debug("proxies: %s" % args.proxies)
        proxies = {}
        proxy_list = args.proxies.split(',')
        for proxy in proxy_list:
            proxy_parts = proxy.split('=')
            if len(proxy_parts) == 2:
                proxies[proxy_parts[0]] = proxy_parts[1]
            else:
                logging.error("Invalid proxy specification.")
                sys.exit("Error: Invalid proxy specification.")
    else:
        proxies = None
    
    sync_job = learners.LearnerQuery(base_url=base_url, api_key=api_key, user_file=user_file, proxies=proxies)
    
    sync_job.sync_ad_with_learners()


if __name__ == '__main__':
    sys.exit(main())
