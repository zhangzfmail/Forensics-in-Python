##############################################################
#                     Bitcoin Address Lookup                 #
#       Blockchain Browser: https://blockchain.info/         #
# Blockchain API: https://blockchain.info/api/blockchain_api #
##############################################################
import argparse
import json
import logging
import urllib2
import time_converter
import sys
import os

def main():
    #Define system argument
    parser = argparse.ArgumentParser(description='Bitcoin Address Lookup',
                                     epilog='Developed in Python ')
    parser.add_argument('BTCADDRESS', help='Bitcoin Address')
    parser.add_argument('-L', help='Specify log directory')
    args = parser.parse_args()

    address = args.BTCADDRESS

    #Set up Log
    if args.L:
        if not os.path.exists(args.L):
            os.makedirs(args.L)
        log_path = os.path.join(args.L, 'btc_address_lookup.log')
    else:
        log_path = 'btc_address_lookup.log'
    logging.basicConfig(filename=log_path, level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)s | %(message)s', filemode='w')
    logging.info('Starting Bitcoin Address Lookup')
    logging.debug('System Platform: ' + sys.platform)
    logging.debug('System Version: ' + sys.version)
    logging.info('Initiated program for Bitcoin address: %s' % (address))
    logging.info('Obtaining JSON structured data from blockchain.info')

    print '*'*40
    print 'Bitcoin Address Lookup'
    print '*'*40

    #Load account and print information
    raw_account = getAddress(address)
    account = json.loads(raw_account.read())
    printTransactions(account)


def getAddress(address):
    #Open the blockchain browser page and return the content
    url = 'https://blockchain.info/address/'+address+'?format=json'
    try:
        return urllib2.urlopen(url)
    except urllib2.URLError, e:
        logging.error('URL Error for %s' % (url))
        if hasattr(e, 'code') and hasattr(e, 'headers'):
            logging.debug('%s: %s' % (e.code, e.reason))
            logging.debug('%s' % (e.headers))
        print 'Received URL Error for Blockchain Browser: %s' % url
        logging.info('Program exiting...')
        sys.exit(1)


def printTransactions(account):
    logging.info('Printing account and transaction information')
    printHeader(account)
    print 'Bitcoin Account Transactions:'
    for i, tx in enumerate(account['txs']):
        print 'Transaction #%i' % (i)
        print 'Transaction Hash:', tx['hash']
        print 'Transaction Date: %s' % (time_converter.time_converter(tx['time']))
        for output in tx['out']:
            inputs = getInputs(tx)
            if len(inputs) > 1:
                print '%s --> %s (%.8f BTC)' % (' & '.join(inputs), output['addr'], output['value'] * 10**-8)
            elif len(inputs) == 1:
                print '%s --> %s (%.8f BTC)' % (''.join(inputs), output['addr'], output['value'] * 10**-8)
            else:
                logging.warn('Detected no input for transaction with hash: %s' % (tx['hash']))
                print 'Detected no input for transaction.'

        print '*'*40


def printHeader(account):
    print 'Address:', account['address']
    print 'Current Balance: %.8f BTC' % (account['final_balance'] * 10**-8)
    print 'Total Sent: %.8f BTC' % (account['total_sent'] * 10**-8)
    print 'Total Received: %.8f BTC' % (account['total_received'] * 10**-8)
    print 'Number of Transactions:', account['n_tx']
    print '*'*40


def getInputs(tx):
    inputs = []
    for input_addr in tx['inputs']:
            inputs.append(input_addr['prev_out']['addr'])
    return inputs

if __name__ == '__main__':
    main()
