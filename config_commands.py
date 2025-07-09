import click
import json
import os

# Define a default path for the configuration file
# In a real app, use click.get_app_dir for platform-agnostic config location
APP_NAME = "ethcli"
CONFIG_DIR = click.get_app_dir(APP_NAME, force_posix=True) # Using force_posix for consistency in examples
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Default configuration settings
DEFAULT_CONFIG = {
    "default_network": "mainnet",
    "default_wallet_alias": None,
    "default_gas_limit": 2000000, # General purpose limit
    "default_rpc_urls": {
        "mainnet": "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID", # User should replace this
        "goerli": "https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID",
        "sepolia": "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID",
    },
    "custom_networks": {}, # Stores user-added networks: name -> {rpc_url, chain_id (optional)}
    "etherscan_api_key": None,
}

def load_config():
    """Loads configuration from the JSON file."""
    if not os.path.exists(CONFIG_FILE):
        # If config doesn't exist, create it with defaults
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        click.echo(f"Warning: Could not load config file at {CONFIG_FILE}. Using defaults. Error: {e}", err=True)
        return DEFAULT_CONFIG.copy() # Return a copy to avoid modifying the global default

def save_config(config_data):
    """Saves configuration to the JSON file."""
    try:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)
    except IOError as e:
        click.echo(f"Error: Could not save config file to {CONFIG_FILE}. Error: {e}", err=True)


@click.group('config')
def config_group():
    """Manage global settings and preferences for ethcli."""
    pass

@config_group.command('set')
@click.argument('key', type=str)
@click.argument('value', type=str)
def set_config_value(key, value):
    """
    Set a configuration value. Use dot notation for nested keys (e.g., default_rpc_urls.mainnet).

    Examples:

    ethcli config set default_network goerli

    ethcli config set default_gas_limit 300000

    ethcli config set default_rpc_urls.mainnet https://your-mainnet-rpc.com

    ethcli config set etherscan_api_key YOUR_API_KEY
    """
    config = load_config()

    # Handle nested keys
    keys = key.split('.')
    current_level = config

    for i, k_part in enumerate(keys[:-1]):
        if k_part not in current_level or not isinstance(current_level[k_part], dict):
            # If path doesn't exist or is not a dict, create it or inform user
            # For simplicity, we'll assume valid paths based on DEFAULT_CONFIG structure for now
            # A more robust version would create nested dicts if they don't exist
            click.echo(f"Error: Key path '{'.'.join(keys[:i+1])}' is not a valid dictionary in config.", err=True)
            click.echo(f"You might need to set up the parent structure first or the key is invalid.")
            return
        current_level = current_level[k_part]

    final_key = keys[-1]

    # Attempt to cast value to a more appropriate type if possible
    # This is a simple heuristic; a more complex system might use a schema
    parsed_value = value
    if value.lower() == "true":
        parsed_value = True
    elif value.lower() == "false":
        parsed_value = False
    elif value.lower() == "none" or value.lower() == "null":
        parsed_value = None
    else:
        try:
            parsed_value = int(value)
        except ValueError:
            try:
                parsed_value = float(value)
            except ValueError:
                pass # Keep as string

    current_level[final_key] = parsed_value
    save_config(config)
    click.echo(f"Configuration updated: {key} = {parsed_value}")
    click.echo(f"Config file location: {CONFIG_FILE}")

@config_group.command('get')
@click.argument('key', type=str, required=False)
def get_config_value(key):
    """
    Get a configuration value. Use dot notation for nested keys.
    If no key is provided, shows the entire configuration.
    """
    config = load_config()
    if not key:
        click.echo("Current configuration:")
        click.echo(json.dumps(config, indent=2))
        click.echo(f"\nConfig file location: {CONFIG_FILE}")
        return

    keys = key.split('.')
    current_level = config
    try:
        for k_part in keys:
            current_level = current_level[k_part]
        click.echo(f"{key} = {json.dumps(current_level, indent=2)}")
    except KeyError:
        click.echo(f"Error: Key '{key}' not found in configuration.", err=True)
    except TypeError: # Could happen if trying to access sub-key of a non-dict
        click.echo(f"Error: Cannot access sub-key of '{key}'. It might not be a dictionary.", err=True)


@config_group.command('reset')
@click.confirmation_option(prompt="Are you sure you want to reset all settings to their defaults?")
def reset_config():
    """Reset all settings to their default values."""
    save_config(DEFAULT_CONFIG)
    click.echo("Configuration has been reset to defaults.")
    click.echo(json.dumps(DEFAULT_CONFIG, indent=2))
    click.echo(f"\nConfig file location: {CONFIG_FILE}")

@config_group.command('path')
def config_path():
    """Show the path to the configuration file."""
    click.echo(f"Configuration file is located at: {CONFIG_FILE}")

if __name__ == '__main__':
    # For testing:
    # Ensure the config directory and file are managed cleanly for tests
    # For example, by using a temporary directory
    # click.echo(f"Config file would be: {CONFIG_FILE}")
    # config_group()
    pass
