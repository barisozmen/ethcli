from web3 import Web3
from decimal import Decimal

def get_web3_instance(node_url):
    """Initializes and returns a Web3 instance connected to the given node URL."""
    return Web3(Web3.HTTPProvider(node_url))

def wei_to_ether(wei_balance):
    """Converts a balance from Wei to Ether."""
    return Decimal(wei_balance) / Decimal(10**18)

def get_balance(args, node_url, default_address):
    """Fetches and displays the ETH balance of an Ethereum address."""
    address = args.address if hasattr(args, 'address') and args.address else default_address
    if not address:
        print("Error: No address specified or cached. Use 'set_address' or provide an address.")
        return

    try:
        w3 = get_web3_instance(node_url)
        if not w3.is_connected():
            print(f"Error: Could not connect to Ethereum node at {node_url}")
            return

        checksum_address = Web3.to_checksum_address(address)
        balance_wei = w3.eth.get_balance(checksum_address)
        balance_eth = wei_to_ether(balance_wei)
        print(f"Balance for {checksum_address}: {balance_eth:.18f} ETH")
    except Exception as e:
        print(f"Error fetching balance for {address}: {e}")

def get_transaction_count(args, node_url, default_address):
    """Fetches and displays the transaction count (nonce) of an Ethereum address."""
    address = args.address if hasattr(args, 'address') and args.address else default_address
    if not address:
        print("Error: No address specified or cached. Use 'set_address' or provide an address.")
        return

    try:
        w3 = get_web3_instance(node_url)
        if not w3.is_connected():
            print(f"Error: Could not connect to Ethereum node at {node_url}")
            return

        checksum_address = Web3.to_checksum_address(address)
        nonce = w3.eth.get_transaction_count(checksum_address)
        print(f"Transaction count for {checksum_address}: {nonce}")
    except Exception as e:
        print(f"Error fetching transaction count for {address}: {e}")

def register_account_commands(subparsers):
    """Registers account-related subcommands to the main parser."""
    account_parser = subparsers.add_parser("account", help="Commands for Ethereum accounts")
    account_subparsers = account_parser.add_subparsers(title="account_commands", dest="account_command", required=True)

    # Get balance command
    balance_parser = account_subparsers.add_parser("balance", help="Get ETH balance for an address.")
    balance_parser.add_argument("address", nargs="?", help="Ethereum address (e.g., 0x...). Uses cached address if not provided.")
    balance_parser.set_defaults(func=get_balance)

    # Get transaction count command
    tx_count_parser = account_subparsers.add_parser("tx_count", help="Get transaction count (nonce) for an address.")
    tx_count_parser.add_argument("address", nargs="?", help="Ethereum address (e.g., 0x...). Uses cached address if not provided.")
    tx_count_parser.set_defaults(func=get_transaction_count)
