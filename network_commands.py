from web3 import Web3
from datetime import datetime

def get_web3_instance(node_url):
    """Initializes and returns a Web3 instance connected to the given node URL."""
    # This is duplicated from account_commands.py, consider refactoring to a shared utils module later
    return Web3(Web3.HTTPProvider(node_url))

def get_latest_block(args, node_url, default_address=None): # default_address is not used but kept for consistency
    """Fetches and displays information about the latest mined block."""
    try:
        w3 = get_web3_instance(node_url)
        if not w3.is_connected():
            print(f"Error: Could not connect to Ethereum node at {node_url}")
            return

        latest_block = w3.eth.get_block('latest')
        print("Latest Block Information:")
        print(f"  Number: {latest_block.number}")
        print(f"  Timestamp: {datetime.fromtimestamp(latest_block.timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  Miner: {latest_block.miner}")
        print(f"  Gas Used: {latest_block.gasUsed}")
        print(f"  Gas Limit: {latest_block.gasLimit}")
        print(f"  Hash: {latest_block.hash.hex()}")
        print(f"  Parent Hash: {latest_block.parentHash.hex()}")
        print(f"  Transactions: {len(latest_block.transactions)}")
    except Exception as e:
        print(f"Error fetching latest block data: {e}")

def get_gas_price(args, node_url, default_address=None): # default_address is not used but kept for consistency
    """Fetches and displays the current gas price."""
    try:
        w3 = get_web3_instance(node_url)
        if not w3.is_connected():
            print(f"Error: Could not connect to Ethereum node at {node_url}")
            return

        gas_price_wei = w3.eth.gas_price
        gas_price_gwei = w3.from_wei(gas_price_wei, 'gwei')
        print(f"Current Gas Price: {gas_price_gwei} Gwei ({gas_price_wei} Wei)")
    except Exception as e:
        print(f"Error fetching gas price: {e}")

def register_network_commands(subparsers):
    """Registers network-related subcommands to the main parser."""
    network_parser = subparsers.add_parser("network", help="Commands for Ethereum network information")
    network_subparsers = network_parser.add_subparsers(title="network_commands", dest="network_command", required=True)

    # Get latest block command
    latest_block_parser = network_subparsers.add_parser("latest_block", help="Get information about the latest block.")
    latest_block_parser.set_defaults(func=get_latest_block)

    # Get gas price command
    gas_price_parser = network_subparsers.add_parser("gas_price", help="Get the current gas price.")
    gas_price_parser.set_defaults(func=get_gas_price)
