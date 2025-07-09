import click
import requests # For Etherscan API
from web3 import Web3
from ethcli import config # Import the config module

# Function to save configuration to ethcli/config.py
def save_config_to_file(eth_address, node_api_key, etherscan_api_key):
    # Construct the path to config.py within the ethcli package
    # This assumes ethcli/config.py is the correct path relative to the project root
    # For a more robust way, especially if commands can be run from anywhere,
    # consider using appdirs or storing config in a user's home directory.
    config_path = "ethcli/config.py"

    lines = []
    if eth_address is not None:
        lines.append(f"ETH_ADDRESS = '{eth_address}'\n")
    else: # Preserve existing if not provided
        lines.append(f"ETH_ADDRESS = {repr(config.ETH_ADDRESS)}\n")

    if node_api_key is not None:
        lines.append(f"NODE_API_KEY = '{node_api_key}'\n")
    else: # Preserve existing
        lines.append(f"NODE_API_KEY = {repr(config.NODE_API_KEY)}\n")

    if etherscan_api_key is not None:
        lines.append(f"ETHERSCAN_API_KEY = '{etherscan_api_key}'\n")
    else: # Preserve existing
        lines.append(f"ETHERSCAN_API_KEY = {repr(config.ETHERSCAN_API_KEY)}\n")

    with open(config_path, "w") as f:
        f.writelines(lines)

    # Reload config to make it available immediately
    import importlib
    importlib.reload(config)

def get_active_wallet_address():
    if not config.ETH_ADDRESS:
        click.echo("Ethereum address not configured. Please run 'account set --address YOUR_ADDRESS'.", err=True)
        return None
    return config.ETH_ADDRESS

def get_web3_provider():
    """Initializes and returns a Web3 provider instance."""
    if not config.NODE_API_KEY:
        click.echo("Node API key not configured. Please run 'account set --nodekey YOUR_NODE_API_KEY'.", err=True)
        return None
    # Assuming Infura, adjust if provider URL structure is different
    provider_url = f"https://mainnet.infura.io/v3/{config.NODE_API_KEY}"
    return Web3(Web3.HTTPProvider(provider_url))

@click.group('account')
def account_group():
    """Manage account settings and view information."""
    pass

@account_group.command('set')
@click.option('--address', 'eth_address', type=str, help='Your Ethereum public address.', default=None)
@click.option('--nodekey', 'node_api_key', type=str, help='API key for your Ethereum node provider (e.g., Infura, Alchemy).', default=None)
@click.option('--scankey', 'etherscan_api_key', type=str, help='API key for Etherscan.', default=None)
def set_config(eth_address, node_api_key, etherscan_api_key):
    """Set and save your Ethereum address, Node API key, and Etherscan API key."""
    if eth_address is None and node_api_key is None and etherscan_api_key is None:
        click.echo("No options provided. Use --address, --nodekey, or --scankey to set values.")
        click.echo(f"Current ETH Address: {config.ETH_ADDRESS or 'Not set'}")
        click.echo(f"Current Node API Key: {'Set' if config.NODE_API_KEY else 'Not set'}")
        click.echo(f"Current Etherscan API Key: {'Set' if config.ETHERSCAN_API_KEY else 'Not set'}")
        return

    if eth_address and not Web3.is_address(eth_address):
        click.echo("Invalid Ethereum address format.", err=True)
        return

    try:
        save_config_to_file(eth_address, node_api_key, etherscan_api_key)
        click.echo("Configuration saved successfully to ethcli/config.py.")
        if eth_address:
            click.echo(f"ETH Address set to: {config.ETH_ADDRESS}")
        if node_api_key:
            click.echo(f"Node API Key has been set.")
        if etherscan_api_key:
            click.echo(f"Etherscan API Key has been set.")

    except Exception as e:
        click.echo(f"Error saving configuration: {e}", err=True)


@account_group.command('balance')
@click.option('--address', 'target_address_override', type=str, help="Address to check balance for (defaults to configured address).")
@click.option('--token', 'token_contract_address', type=str, help="ERC-20 token contract address (optional).")
@click.option('--block', 'block_identifier', type=str, help="Block number or tag (e.g., 'latest', 'pending', or a number) (optional).")
def get_balance(target_address_override, token_contract_address, block_identifier):
    """Show ETH or token balance for an address."""
    address_to_check = target_address_override or get_active_wallet_address()
    if not address_to_check:
        return

    block_info = f" at block {block_identifier}" if block_identifier else " (latest)"

    w3 = get_web3_provider()
    if not w3:
        return

    if token_contract_address:
        click.echo(f"Fetching ERC-20 token balance for token {token_contract_address} at address {address_to_check}{block_info}...")
        # Placeholder: Implement ERC-20 token balance fetching
        # 1. Need ABI for ERC-20 (balanceOf function).
        # 2. Call balanceOf(address_to_check) on the token_contract_address.
        # 3. Format the result (considering token decimals).
        click.echo(f"Token Balance (Token: {token_contract_address}): 123.45 TKN (Example - Not Implemented)")
    else:
        click.echo(f"Fetching ETH balance for address: {address_to_check}{block_info}...")
        try:
            checksum_address = Web3.to_checksum_address(address_to_check)
            if block_identifier:
                eth_balance = w3.eth.get_balance(checksum_address, block_identifier=block_identifier)
            else:
                eth_balance = w3.eth.get_balance(checksum_address)
            balance_in_ether = Web3.from_wei(eth_balance, 'ether')
            click.echo(f"ETH Balance: {balance_in_ether} ETH")
        except Exception as e:
            click.echo(f"Error fetching ETH balance: {e}", err=True)

@account_group.command('nonce')
@click.option('--address', 'target_address_override', type=str, help="Address to check nonce for (defaults to configured address).")
@click.option('--block', 'block_identifier', type=str, default='pending', help="Block number or tag (e.g., 'latest', 'pending') (defaults to 'pending').")
def get_nonce(target_address_override, block_identifier):
    """Show current nonce for an address."""
    address_to_check = target_address_override or get_active_wallet_address()
    if not address_to_check:
        return

    w3 = get_web3_provider()
    if not w3:
        return

    click.echo(f"Fetching nonce for address: {address_to_check} at block: {block_identifier}...")
    try:
        checksum_address = Web3.to_checksum_address(address_to_check)
        nonce = w3.eth.get_transaction_count(checksum_address, block_identifier=block_identifier)
        click.echo(f"Nonce: {nonce}")
    except Exception as e:
        click.echo(f"Error fetching nonce: {e}", err=True)

@account_group.command('transactions')
@click.option('--address', 'target_address_override', type=str, help="Address to fetch transactions for (defaults to configured address).")
@click.option('--limit', type=int, default=10, help="Number of transactions to display.")
@click.option('--sort', type=click.Choice(['asc', 'desc']), default='desc', help="Sort order (ascending or descending).")
def get_transactions(target_address_override, limit, sort):
    """Fetch and display recent transactions for an address using Etherscan."""
    eth_address = target_address_override or get_active_wallet_address()
    if not eth_address:
        return

    if not config.ETHERSCAN_API_KEY:
        click.echo("Etherscan API key not configured. Please run 'account set --scankey YOUR_ETHERSCAN_API_KEY'.", err=True)
        return

    etherscan_api_url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": eth_address,
        "startblock": 0,
        "endblock": 99999999, # Or 'latest' if API supports
        "page": 1,
        "offset": limit,
        "sort": sort,
        "apikey": config.ETHERSCAN_API_KEY,
    }

    click.echo(f"Fetching last {limit} transactions for {eth_address} (sort: {sort})...")
    try:
        response = requests.get(etherscan_api_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if data["status"] == "1":
            if not data["result"]:
                click.echo("No transactions found.")
                return
            for tx in data["result"]:
                value_eth = Web3.from_wei(int(tx['value']), 'ether')
                direction = "OUT" if tx['from'].lower() == eth_address.lower() else "IN"
                click.echo(
                    f"  {direction} Hash: {tx['hash']}\n"
                    f"    Block: {tx['blockNumber']}, Timestamp: {tx['timeStamp']} ({click.style(tx['confirmations'], fg='green')} confs)\n"
                    f"    From: {tx['from']}\n"
                    f"    To: {tx['to']}\n"
                    f"    Value: {value_eth} ETH\n"
                    f"    Gas Used: {tx['gasUsed']}, Gas Price: {Web3.from_wei(int(tx['gasPrice']), 'gwei')} Gwei\n"
                    f"    Is Error: {'Yes' if tx['isError'] == '1' else 'No'}"
                )
        elif data["status"] == "0" and data["message"] == "No transactions found":
            click.echo("No transactions found for this address.")
        else:
            click.echo(f"Error from Etherscan API: {data.get('message', 'Unknown error')} {data.get('result', '')}", err=True)
    except requests.exceptions.RequestException as e:
        click.echo(f"HTTP Request Error: {e}", err=True)
    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)

@account_group.command('tokens')
@click.option('--address', 'target_address', type=str, help="Address to list tokens for (defaults to active wallet).")
# Could add --min-balance to filter small balances
def list_tokens(target_address):
    """List ERC-20 tokens held by an address."""
    address_to_check = target_address or get_active_wallet_address()
    click.echo(f"Listing ERC-20 tokens for address: {address_to_check}...")
    # Placeholder: Implement token listing. This is complex and might involve:
    # 1. Querying a token list service (e.g., Uniswap's list, CoinGecko).
    # 2. Or, scanning transaction history for 'Transfer' events to this address.
    # 3. Or, using a service like Etherscan API or Covalent/Alchemy/Infura token APIs.
    click.echo("  Token: DAI (0x6B175474E89094C44Da98b954EedeAC495271d0F), Balance: 100.0")
    click.echo("  Token: USDC (0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48), Balance: 50.5")
    click.echo("(Placeholder - requires external data source or indexing)")

@account_group.command('ens')
@click.argument('name_or_address', type=str)
def resolve_ens(name_or_address):
    """Resolve ENS name to address, or perform reverse lookup for an address."""
    if name_or_address.startswith('0x'):
        click.echo(f"Performing reverse ENS lookup for address: {name_or_address}...")
        # Placeholder: Implement ENS reverse lookup (web3.ens.name(address))
        click.echo(f"ENS Name: vitalik.eth (Example)")
    elif '.eth' in name_or_address:
        click.echo(f"Resolving ENS name: {name_or_address}...")
        # Placeholder: Implement ENS name resolution (web3.ens.address(name))
        click.echo(f"Address: 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 (Example for vitalik.eth)")
    else:
        click.echo("Invalid input. Please provide an ENS name (e.g., 'vitalik.eth') or an Ethereum address (e.g., '0x...').", err=True)

if __name__ == '__main__':
    account_group()
