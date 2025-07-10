import click

@click.group('network')
def network_group():
    """Manage and view Ethereum networks."""
    pass

@network_group.command('list')
def list_networks():
    """Show available networks."""
    click.echo("Listing available networks...")
    # Placeholder: Implement actual network listing logic
    click.echo("- mainnet")
    click.echo("- goerli")
    click.echo("- sepolia")

@network_group.command('use')
@click.argument('network_name', type=str)
def use_network(network_name):
    """Switch active network (mainnet, goerli, sepolia, etc.)."""
    click.echo(f"Switching active network to: {network_name}")
    # Placeholder: Implement network switching logic

@network_group.command('add')
@click.argument('name', type=str)
@click.option('--rpc', 'rpc_url', required=True, type=str, help="RPC URL of the custom network.")
def add_network(name, rpc_url):
    """Add a custom network."""
    click.echo(f"Adding custom network '{name}' with RPC URL: {rpc_url}")
    # Placeholder: Implement custom network addition logic

@network_group.command('remove')
@click.argument('name', type=str)
def remove_network(name):
    """Remove a network."""
    click.echo(f"Removing network: {name}")
    # Placeholder: Implement network removal logic

@network_group.command('info')
def network_info():
    """Show current network info (chain ID, gas price, peers)."""
    click.echo("Displaying current network information...")
    # Placeholder: Implement logic to fetch and display network info
    click.echo("Chain ID: 1 (Example Mainnet)")
    click.echo("Current Gas Price: 50 Gwei")
    click.echo("Connected Peers: 10")

if __name__ == '__main__':
    # This allows testing the command group independently, if necessary
    # For example: python network_commands.py list
    network_group()

# Added Price Command
import requests

@network_group.command('price')
@click.option('--coin', default='ethereum', help='The coin ID to fetch the price for (e.g., ethereum, bitcoin).')
@click.option('--currency', default='usd', help='The currency to display the price in (e.g., usd, eur, gbp).')
def get_price(coin, currency):
    """Fetch the current price of a cryptocurrency from CoinGecko."""
    api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies={currency}"
    click.echo(f"Fetching price for {coin} in {currency.upper()}...")
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if coin in data and currency in data[coin]:
            price = data[coin][currency]
            click.echo(f"Current price of {coin.capitalize()}: {price} {currency.upper()}")
        else:
            click.echo(f"Could not find price data for {coin} in {currency.upper()}.", err=True)
            if coin not in data:
                click.echo(f"Coin ID '{coin}' might be invalid or not supported by CoinGecko's simple API.", err=True)
            elif currency not in data.get(coin, {}):
                 click.echo(f"Currency '{currency}' might be invalid or not supported for {coin}.", err=True)

    except requests.exceptions.RequestException as e:
        click.echo(f"HTTP Request Error fetching price: {e}", err=True)
    except Exception as e:
        click.echo(f"An error occurred: {e}", err=True)
