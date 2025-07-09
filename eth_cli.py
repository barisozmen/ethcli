import argparse
import os
import sys

from account_commands import register_account_commands
from network_commands import register_network_commands

# Location to cache the Ethereum address
ADDRESS_CACHE_FILE = os.path.expanduser("~/.eth_cli_address")
NODE_URL_CACHE_FILE = os.path.expanduser("~/.eth_cli_node_url")

def set_address(args):
    """Saves the Ethereum address to the cache file."""
    with open(ADDRESS_CACHE_FILE, "w") as f:
        f.write(args.address)
    print(f"Ethereum address {args.address} saved.")

def get_cached_address():
    """Retrieves the cached Ethereum address."""
    if os.path.exists(ADDRESS_CACHE_FILE):
        with open(ADDRESS_CACHE_FILE, "r") as f:
            return f.read().strip()
    return None

def set_node_url(args):
    """Saves the Ethereum node URL to the cache file."""
    with open(NODE_URL_CACHE_FILE, "w") as f:
        f.write(args.url)
    print(f"Ethereum node URL {args.url} saved.")

def get_cached_node_url():
    """Retrieves the cached Ethereum node URL."""
    if os.path.exists(NODE_URL_CACHE_FILE):
        with open(NODE_URL_CACHE_FILE, "r") as f:
            return f.read().strip()
    return None

def main():
    parser = argparse.ArgumentParser(description="A CLI tool to interact with the Ethereum blockchain.")
    subparsers = parser.add_subparsers(title="commands", dest="command", required=True)

    # Top-level command for setting the address
    set_address_parser = subparsers.add_parser("set_address", help="Save your Ethereum address.")
    set_address_parser.add_argument("address", help="Your Ethereum address (e.g., 0x...)")
    set_address_parser.set_defaults(func=set_address)

    # Top-level command for setting the node URL
    set_node_url_parser = subparsers.add_parser("set_node_url", help="Save your Ethereum node URL (e.g., Infura/Alchemy HTTP endpoint).")
    set_node_url_parser.add_argument("url", help="Ethereum node URL")
    set_node_url_parser.set_defaults(func=set_node_url)

    # Register account commands
    register_account_commands(subparsers)

    # Register network commands
    register_network_commands(subparsers)

    # Add other command groups here if needed (e.g., transaction commands, block commands)

    if len(sys.argv) == 1:
        # If no command is given, check if address or node_url is set.
        # If not, prompt the user.
        # If an address is set, default to showing account balance or some summary.
        # For now, just print help.
        cached_address = get_cached_address()
        cached_node_url = get_cached_node_url()
        if not cached_address:
            print("No Ethereum address set. Use 'eth_cli set_address <YOUR_ADDRESS>' to set it.")
            parser.print_help(sys.stderr)
            sys.exit(1)
        if not cached_node_url:
            print("No Ethereum node URL set. Use 'eth_cli set_node_url <YOUR_NODE_URL>' to set it.")
            print("You can get a free one from services like Infura (infura.io) or Alchemy (alchemy.com).")
            parser.print_help(sys.stderr)
            sys.exit(1)
        # If both are set, could default to a specific command, e.g., get_balance
        # For now, if they are set but no command is given, also print help.
        parser.print_help(sys.stderr)
        sys.exit(1)


    args = parser.parse_args()

    # Execute the function associated with the chosen command
    # Some commands like set_address don't need node_url or address
    if hasattr(args, 'func'):
        if args.command in ["set_address", "set_node_url"]:
            args.func(args)
        else:
            # For other commands, ensure address and node_url are available
            address = get_cached_address()
            node_url = get_cached_node_url()

            if not address and not getattr(args, 'address', None):
                print("Error: Ethereum address not set. Use 'set_address' command or provide address as an argument.")
                sys.exit(1)
            if not node_url:
                print("Error: Ethereum node URL not set. Use 'set_node_url' command.")
                sys.exit(1)

            # Pass dependencies to the command function
            args.func(args, node_url, address if not getattr(args, 'address', None) else args.address)

if __name__ == "__main__":
    main()
