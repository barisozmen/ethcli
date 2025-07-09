import click

# Note: 'click' automatically provides 'ethcli --help', 'ethcli <group> --help',
# and 'ethcli <group> <command> --help'.
# This 'help' group is primarily for custom extensions like 'examples'.

@click.group('help')
def help_group():
    """
    Provides extended help and examples for using ethcli.
    For standard help, use 'ethcli --help' or 'ethcli <command> --help'.
    """
    pass

@help_group.command('examples')
@click.option('--command', 'specific_command', type=str, help="Show examples for a specific command or group (e.g., 'wallet create', 'tx send').")
def show_examples(specific_command):
    """Print common usage examples for ethcli commands."""

    examples = {
        "general": [
            "# Show top-level help:",
            "ethcli --help",
            "# Show help for the 'wallet' command group:",
            "ethcli wallet --help",
            "# Show help for the 'wallet create' command:",
            "ethcli wallet create --help",
        ],
        "network": [
            "# List available networks:",
            "ethcli network list",
            "# Switch to the Goerli testnet:",
            "ethcli network use goerli",
            "# Add a custom network:",
            "ethcli network add my_local_node --rpc http://localhost:8545",
            "# Show info about the current network:",
            "ethcli network info",
        ],
        "wallet": [
            "# Create a new wallet with an alias:",
            "ethcli wallet create --name my_main_wallet",
            "# List all stored wallets:",
            "ethcli wallet list",
            "# Import a wallet using a private key (use quotes for safety):",
            'ethcli wallet import --private-key "0xYOUR_PRIVATE_KEY_HERE"',
            "# Export a wallet's address (private key hidden by default):",
            "ethcli wallet export my_main_wallet",
            "# Export a wallet and show its private key (USE WITH EXTREME CAUTION):",
            "ethcli wallet export my_main_wallet --show-private",
        ],
        "tx": [
            "# Send 0.5 ETH to an address (ensure active network and wallet are set):",
            "ethcli tx send --to 0xRecipientAddress... --value 0.5eth",
            "# Check the status of a transaction:",
            "ethcli tx status 0xTransactionHash...",
            "# Estimate gas for a transaction:",
            "ethcli tx gas-estimate --to 0xRecipientAddress... --value 0.1eth",
        ],
        "contract": [
            "# Deploy a smart contract (assuming MyContract.sol exists):",
            'ethcli contract deploy ./contracts/MyContract.sol --constructor-args \'123,"hello",0xSomeAddress\'',
            "# Call a read-only method on a deployed contract:",
            "ethcli contract call --address 0xContractAddress... --method 'balanceOf(address)' --args '0xAccountToQuery'",
            "# Send a transaction to a write method on a contract:",
            "ethcli contract send --address 0xContractAddress... --method 'transfer(address,uint256)' --args '0xRecipientAddress,1000000000000000000' --value 0.01eth",
            "# Get a contract's ABI:",
            "ethcli contract abi --address 0xContractAddress...",
        ],
        "account": [
            "# Check ETH balance of the active wallet:",
            "ethcli account balance",
            "# Check ETH balance of a specific address:",
            "ethcli account balance --address 0xSomeAddress...",
            "# Check balance of an ERC20 token for the active wallet:",
            "ethcli account balance --token 0xTokenContractAddress...",
            "# Get the nonce for the active wallet:",
            "ethcli account nonce",
            "# Resolve an ENS name to an address:",
            "ethcli account ens vitalik.eth",
        ],
        "nft": [
            "# Deploy an ERC-721 NFT contract (assuming MyNFT.sol for ERC721 exists):",
            'ethcli nft deploy721 ./contracts/MyNFT.sol --name "My Awesome NFT" --symbol "MANFT"',
            "# Mint an ERC-721 token:",
            "ethcli nft mint721 --to 0xRecipientAddress... --uri ipfs://YourMetadataHash --contract 0xNftContractAddress...",
            "# Get the owner of an ERC-721 token:",
            "ethcli nft owner721 --id 1 --contract 0xNftContractAddress...",
        ],
        "config": [
            "# Show all current configurations:",
            "ethcli config get",
            "# Set the default network to sepolia:",
            "ethcli config set default_network sepolia",
            "# Get the path to the config file:",
            "ethcli config path",
        ]
        # Add more examples for other groups as needed
    }

    if specific_command:
        # Try to find examples for the specific command/group
        # This is a simple match; could be more sophisticated (e.g. matching "tx" for "tx send")
        matched = False
        for key, ex_list in examples.items():
            if key == specific_command or specific_command.startswith(key):
                click.echo(f"\n--- Examples for '{key}' ---")
                for ex in ex_list:
                    click.echo(ex)
                matched = True
        if not matched:
            click.echo(f"No specific examples found for '{specific_command}'. Showing general examples.")
            if "general" in examples: # Check if general examples exist
                 for ex in examples["general"]:
                    click.echo(ex)
    else:
        click.echo("--- Common ethcli Usage Examples ---")
        click.echo("For detailed help on any command: ethcli <command_group> <sub_command> --help\n")
        for group_name, ex_list in examples.items():
            if group_name == "general": continue # Skip general if showing all
            click.echo(f"\n--- {group_name.capitalize()} Examples ---")
            for i, ex in enumerate(ex_list):
                click.echo(ex)
                if i >= 2 and len(ex_list) > 3: # Show first 3 for brevity when listing all
                    click.echo(f"(... and {len(ex_list) - 3} more for {group_name} ...)")
                    break

        click.echo("\n--- General Help Examples ---")
        if "general" in examples: # Check if general examples exist
            for ex in examples["general"]:
                click.echo(ex)

if __name__ == '__main__':
    # To test: python help_commands.py examples
    # python help_commands.py examples --command wallet
    help_group()
