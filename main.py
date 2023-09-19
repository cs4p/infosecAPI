#!/usr/bin/env python3
import argparse
import getpass
import sys
import logging
from learners import sync_ad_with_learners


def main():
    example = "Usage: %(prog)s -p key.txt -f Scheduled_CSV.csv"
    options = argparse.ArgumentParser(epilog=example)
    options.add_argument('-d', '--debug', help='Print debug messages', action='store_true')
    options.add_argument('-q', '--quiet', help="Don't print status messages", action='store_true')
    options.add_argument('-H', '--host', help='Base URL for the api. e.g. https://securityiq.infosecinstitute.com/api/v2/', default="https://securityiq.infosecinstitute.com/api/v2/")
    options.add_argument('-p', '--passfile', help='File containing your api key (Default is to prompt)', required=True)
    options.add_argument('-f', '--user_file', help="CSV file containing AD users", required=True)
    args = options.parse_args()
    
    if args.passfile:
        with open(args.passfile) as f:
            api_key = f.readline().strip()
    else:
        api_key = getpass.getpass()
        
    base_url = args.host
    user_file = args.user_file
    
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    if args.quiet:
        log_level = logging.WARNING
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(asctime)s: %(filename)s: %(funcName)s: %(lineno)d: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=[
            logging.FileHandler('infosecAPI.log'),
            logging.StreamHandler()]
        )
    sync_ad_with_learners(base_url, api_key, user_file)


if __name__ == '__main__':
    sys.exit(main())