import os
import subprocess
import json
import shutil
import pytest
import tempfile

# Helper function to run eth commands
def run_eth_command(command_args, input_data=None, env=None):
    """
    Runs the 'eth' CLI command with given arguments.

    Args:
        command_args (list): A list of strings representing the command and its arguments.
        input_data (str, optional): String data to pass to the command's stdin.
        env (dict, optional): Environment variables to set for the command.

    Returns:
        subprocess.CompletedProcess: The result object from subprocess.run.
    """
    process = ['eth'] + command_args
    print(f"Running command: {' '.join(process)}") # For debugging test runs

    # Ensure environment is based on current environment
    full_env = os.environ.copy()
    if env:
        full_env.update(env)

    result = subprocess.run(
        process,
        capture_output=True,
        text=True,
        input=input_data,
        env=full_env,
        # It's good practice to add a timeout, but for now, we'll omit it
        # unless specific tests hang.
        # timeout=30
    )
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    return result

# Fixture for managing the ethcli configuration directory
@pytest.fixture(scope="function") # "function" scope ensures a fresh config for each test
def isolated_config_dir():
    """
    Creates a temporary directory to act as the config home,
    isolating ethcli configuration for each test.
    It sets the HOME environment variable to this temporary directory,
    as click.get_app_dir typically relies on HOME for ~/.config.
    """
    original_home = os.environ.get("HOME")
    original_xdg_config_home = os.environ.get("XDG_CONFIG_HOME")

    with tempfile.TemporaryDirectory() as tmpdir:
        # click.get_app_dir(..., force_posix=True) will create a .config inside this tmpdir.
        # So, we set HOME to tmpdir.
        print(f"Using temporary HOME for config: {tmpdir}")
        os.environ["HOME"] = tmpdir
        # Unset XDG_CONFIG_HOME to ensure HOME is used by click.get_app_dir
        if "XDG_CONFIG_HOME" in os.environ:
            del os.environ["XDG_CONFIG_HOME"]

        # The actual config dir will be tmpdir + "/.config/ethcli"
        # due to force_posix=True and APP_NAME="ethcli"
        # We can pre-create it if needed, but ethcli should handle it.

        yield tmpdir # This is what the test will receive

        # Restore original environment variables
        if original_home is None:
            del os.environ["HOME"]
        else:
            os.environ["HOME"] = original_home

        if original_xdg_config_home is None:
            if "XDG_CONFIG_HOME" in os.environ: # Should not happen if we deleted it
                 del os.environ["XDG_CONFIG_HOME"]
        else:
            os.environ["XDG_CONFIG_HOME"] = original_xdg_config_home

# Basic test to ensure the CLI is callable
def test_eth_is_callable():
    """Test that the 'eth' command can be called."""
    result = run_eth_command(["--version"]) # Click usually adds --version
    # The setup.py doesn't specify a click version command, but click itself provides it.
    # If 'ethcli.cli:ethcli' is a click.Group, then 'eth --version' should work.
    # Let's check for basic help output if --version isn't automatically handled by base click.Group
    if "eth, version" not in result.stdout and result.returncode != 0 :
         # Fallback to check if main help works
         result = run_eth_command(["--help"])
         assert result.returncode == 0
         assert "Usage: eth [OPTIONS] COMMAND [ARGS]..." in result.stdout
    else:
        assert result.returncode == 0
        assert "eth, version" in result.stdout # or whatever click outputs for --version

    print("Test `test_eth_is_callable` passed.")

# Placeholder for future tests - helps confirm pytest setup
def test_placeholder():
    assert True
    print("Test `test_placeholder` passed.")

# --- Config Command Tests ---

def test_config_path(isolated_config_dir):
    """Test 'eth config path' command."""
    result = run_eth_command(["config", "path"])
    assert result.returncode == 0

    # Expected path is $HOME/.ethcli/config.json when force_posix=True and app_name is 'ethcli'
    # The isolated_config_dir fixture sets HOME to a temp directory.
    expected_path = os.path.join(isolated_config_dir, ".ethcli", "config.json")
    assert expected_path in result.stdout
    print(f"test_config_path: Verified path '{expected_path}' in output.")

def test_config_get_all_initial(isolated_config_dir):
    """Test 'eth config get' for initial default configuration."""
    result = run_eth_command(["config", "get"])
    assert result.returncode == 0

    try:
        config_data = json.loads(result.stdout.split("Current configuration:")[1].split("\nConfig file location:")[0].strip())
    except (json.JSONDecodeError, IndexError) as e:
        pytest.fail(f"Could not parse JSON output from 'eth config get': {e}\nOutput was:\n{result.stdout}")

    # These are defaults from ethcli/commands/config.py
    assert config_data["default_network"] == "mainnet"
    assert config_data["default_wallet_alias"] is None
    assert "default_rpc_urls" in config_data
    assert config_data["default_rpc_urls"]["mainnet"].startswith("https://mainnet.infura.io/v3/")
    print("test_config_get_all_initial: Verified initial default config output.")

def test_config_set_and_get_single(isolated_config_dir):
    """Test 'eth config set <key> <value>' and 'eth config get <key>'."""
    key, value = "default_network", "testnet_xyz"
    set_result = run_eth_command(["config", "set", key, value])
    assert set_result.returncode == 0
    assert f"Configuration updated: {key} = {value}" in set_result.stdout

    get_result = run_eth_command(["config", "get", key])
    assert get_result.returncode == 0
    assert f"{key} = \"{value}\"" in get_result.stdout # JSON output will quote strings

    # Verify in the actual config file
    config_file_path = os.path.join(isolated_config_dir, ".ethcli", "config.json")
    with open(config_file_path, 'r') as f:
        config_on_disk = json.load(f)
    assert config_on_disk[key] == value
    print(f"test_config_set_and_get_single: Verified set and get for '{key}'.")

def test_config_set_and_get_nested(isolated_config_dir):
    """Test setting and getting a nested configuration value."""
    key, value = "default_rpc_urls.goerli", "http://new-goerli-rpc.example.com"
    set_result = run_eth_command(["config", "set", key, value])
    assert set_result.returncode == 0
    assert f"Configuration updated: {key} = {value}" in set_result.stdout

    get_result = run_eth_command(["config", "get", key])
    assert get_result.returncode == 0
    assert f"{key} = \"{value}\"" in get_result.stdout

    # Verify in the actual config file
    config_file_path = os.path.join(isolated_config_dir, ".ethcli", "config.json")
    parent_key, child_key = key.split('.', 1)
    with open(config_file_path, 'r') as f:
        config_on_disk = json.load(f)
    assert config_on_disk[parent_key][child_key] == value
    print(f"test_config_set_and_get_nested: Verified set and get for nested key '{key}'.")

def test_config_get_non_existent_key(isolated_config_dir):
    """Test 'eth config get' for a non-existent key."""
    key = "this_key_does_not_exist_123"
    result = run_eth_command(["config", "get", key])
    # The command currently exits 0 even on error, but prints to stderr.
    # A more robust CLI might exit non-zero. For now, test stderr.
    assert result.returncode == 0
    assert f"Error: Key '{key}' not found in configuration." in result.stderr
    print("test_config_get_non_existent_key: Verified error for non-existent key in stderr.")

def test_config_reset(isolated_config_dir):
    """Test 'eth config reset' command."""
    # First, change some values
    run_eth_command(["config", "set", "default_network", "testnet_for_reset"])
    run_eth_command(["config", "set", "some_new_custom_key", "some_value"])

    # Run reset, piping 'y' for confirmation.
    # The click confirmation_option by default aborts if it doesn't get 'y'.
    reset_result = run_eth_command(["config", "reset"], input_data="y\n")
    assert reset_result.returncode == 0
    assert "Configuration has been reset to defaults." in reset_result.stdout

    # Verify config is back to defaults
    get_all_result = run_eth_command(["config", "get"])
    assert get_all_result.returncode == 0
    try:
        config_data = json.loads(get_all_result.stdout.split("Current configuration:")[1].split("\nConfig file location:")[0].strip())
    except (json.JSONDecodeError, IndexError) as e:
        pytest.fail(f"Could not parse JSON output after reset: {e}\nOutput was:\n{get_all_result.stdout}")

    assert config_data["default_network"] == "mainnet" # Default value
    assert "some_new_custom_key" not in config_data # Custom key should be gone

    # Verify the underlying JSON config file is reset
    config_file_path = os.path.join(isolated_config_dir, ".ethcli", "config.json")
    with open(config_file_path, 'r') as f:
        config_on_disk = json.load(f)
    assert config_on_disk["default_network"] == "mainnet"
    assert "some_new_custom_key" not in config_on_disk
    print("test_config_reset: Verified config reset to defaults.")


if __name__ == "__main__":
    # This allows running the test file directly for debugging, e.g., python tests/test_e2e_cli.py
    # However, it's better to use `pytest tests/`
    pytest.main(["-v", __file__])

# --- Help Command Tests ---

def test_help_main():
    """Test 'eth --help'."""
    result = run_eth_command(["--help"])
    assert result.returncode == 0
    assert "Usage: eth [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "network" in result.stdout # Check for a known command group
    assert "wallet" in result.stdout  # Check for another known command group
    assert "config" in result.stdout
    print("test_help_main: Verified main help output.")

def test_help_group():
    """Test 'eth <group> --help'."""
    result = run_eth_command(["wallet", "--help"])
    assert result.returncode == 0
    assert "Usage: eth wallet [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "create" in result.stdout  # Check for a known subcommand in wallet
    assert "import" in result.stdout
    print("test_help_group: Verified group-level help for 'wallet'.")

def test_help_command():
    """Test 'eth <group> <command> --help'."""
    result = run_eth_command(["wallet", "create", "--help"])
    assert result.returncode == 0
    assert "Usage: eth wallet create [OPTIONS]" in result.stdout
    assert "--name" in result.stdout  # Check for an option of 'wallet create'
    print("test_help_command: Verified command-level help for 'wallet create'.")

def test_help_examples_general():
    """Test 'eth help examples' for general examples."""
    result = run_eth_command(["help", "examples"])
    assert result.returncode == 0
    assert "--- Common ethcli Usage Examples ---" in result.stdout
    assert "--- Wallet Examples ---" in result.stdout # Check for wallet examples section
    assert "--- Network Examples ---" in result.stdout # Check for network examples section
    print("test_help_examples_general: Verified general output of 'help examples'.")

def test_help_examples_specific():
    """Test 'eth help examples --command <specific_command>'."""
    # Test for a group
    result_wallet = run_eth_command(["help", "examples", "--command", "wallet"])
    assert result_wallet.returncode == 0
    assert "--- Examples for 'wallet' ---" in result_wallet.stdout
    assert "ethcli wallet create" in result_wallet.stdout # Specific wallet command example
    assert "--- Network Examples ---" not in result_wallet.stdout # Should not show other groups

    # Test for a more specific command (though current examples are group-based)
    # The help example code does a startswith match, so 'tx' should match 'tx' group
    result_tx = run_eth_command(["help", "examples", "--command", "tx"])
    assert result_tx.returncode == 0
    assert "--- Examples for 'tx' ---" in result_tx.stdout
    assert "ethcli tx send" in result_tx.stdout
    print("test_help_examples_specific: Verified specific command examples output.")

# --- Wallet Command Tests (Placeholder Behavior) ---

def test_wallet_create_no_alias():
    """Test 'eth wallet create' without alias."""
    result = run_eth_command(["wallet", "create"])
    assert result.returncode == 0
    assert "Generating a new wallet..." in result.stdout
    assert "Wallet created successfully." in result.stdout # Based on placeholder
    print("test_wallet_create_no_alias: Verified placeholder output.")

def test_wallet_create_with_alias():
    """Test 'eth wallet create --name <alias>'."""
    alias = "mytestwallet"
    result = run_eth_command(["wallet", "create", "--name", alias])
    assert result.returncode == 0
    assert f"Generating a new wallet with alias: {alias}..." in result.stdout
    assert "Wallet created successfully." in result.stdout
    print("test_wallet_create_with_alias: Verified placeholder output with alias.")

def test_wallet_import_private_key():
    """Test 'eth wallet import --private-key <key>'."""
    # Using a dummy key that matches expected format for placeholder
    dummy_pk = "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    result = run_eth_command(["wallet", "import", "--private-key", dummy_pk])
    assert result.returncode == 0
    assert f"Importing wallet using private key: {dummy_pk[:4]}...{dummy_pk[-4:]}" in result.stdout
    assert "Wallet imported successfully." in result.stdout
    print("test_wallet_import_private_key: Verified placeholder output.")

def test_wallet_import_mnemonic():
    """Test 'eth wallet import --mnemonic <phrase>'."""
    dummy_mnemonic = "test junk twelve word phrase example useless random for placeholder testing only"
    result = run_eth_command(["wallet", "import", "--mnemonic", dummy_mnemonic])
    assert result.returncode == 0
    # Based on current placeholder: "Importing wallet using mnemonic: \"{mnemonic_phrase.split(' ')[0]} ... {mnemonic_phrase.split(' ')[-1]}\""
    expected_output_part = f"Importing wallet using mnemonic: \"{dummy_mnemonic.split(' ')[0]} ... {dummy_mnemonic.split(' ')[-1]}\""
    assert expected_output_part in result.stdout
    assert "Wallet imported successfully." in result.stdout
    print("test_wallet_import_mnemonic: Verified placeholder output.")

def test_wallet_import_no_option():
    """Test 'eth wallet import' with no options (should show error)."""
    result = run_eth_command(["wallet", "import"])
    assert result.returncode == 0 # The command itself doesn't exit non-zero yet
    assert "Please provide either --private-key or --mnemonic to import a wallet." in result.stderr
    print("test_wallet_import_no_option: Verified error message for missing options.")

def test_wallet_list():
    """Test 'eth wallet list'."""
    result = run_eth_command(["wallet", "list"])
    assert result.returncode == 0
    assert "Listing stored wallets..." in result.stdout
    # Check for example placeholder output
    assert "- mywallet1 (0xabc...def)" in result.stdout
    print("test_wallet_list: Verified placeholder output.")

def test_wallet_select():
    """Test 'eth wallet select <alias>'."""
    alias = "selectedwallet"
    result = run_eth_command(["wallet", "select", alias])
    assert result.returncode == 0
    assert f"Setting active wallet to: {alias}" in result.stdout
    print("test_wallet_select: Verified placeholder output.")

def test_wallet_export_no_private():
    """Test 'eth wallet export <alias>' without showing private key."""
    alias = "exportwallet"
    result = run_eth_command(["wallet", "export", alias])
    assert result.returncode == 0
    assert f"Exporting wallet information for: {alias}" in result.stdout
    assert f"Address: 0x123...abc (for {alias})" in result.stdout # Placeholder address
    assert "Private key hidden. Use --show-private to display it." in result.stdout
    print("test_wallet_export_no_private: Verified placeholder output.")

def test_wallet_export_show_private():
    """Test 'eth wallet export <alias> --show-private'."""
    alias = "exportwallet_pk"
    result = run_eth_command(["wallet", "export", alias, "--show-private"])
    assert result.returncode == 0
    assert f"Exporting wallet information for: {alias}" in result.stdout
    assert "WARNING: Displaying private key. Handle with extreme care!" in result.stdout
    assert f"Private Key: 0xPRIVATEKEYHEX... (for {alias})" in result.stdout # Placeholder PK
    print("test_wallet_export_show_private: Verified placeholder output with private key.")

def test_wallet_delete_confirm_yes():
    """Test 'eth wallet delete <alias>' with 'y' confirmation."""
    alias = "deletethiswallet"
    result = run_eth_command(["wallet", "delete", alias], input_data="y\n")
    assert result.returncode == 0
    assert f"Deleting wallet: {alias}" in result.stdout # This is after confirmation
    assert f"Wallet '{alias}' deleted successfully." in result.stdout
    # Check if the confirmation prompt appeared in stderr or stdout (click behavior)
    # click.confirm usually prints prompt to stderr if it's a TTY, or stdout if not.
    # For subprocess, it often goes to stdout.
    assert f"Are you sure you want to delete wallet '{alias}'?" in result.stdout
    print("test_wallet_delete_confirm_yes: Verified placeholder output with 'y' confirmation.")

def test_wallet_delete_confirm_no():
    """Test 'eth wallet delete <alias>' with 'n' confirmation (aborts)."""
    alias = "dontdeletethis"
    result = run_eth_command(["wallet", "delete", alias], input_data="n\n")
    # click.confirm with abort=True will call sys.exit(1) if confirmation fails
    assert result.returncode == 1
    assert "Aborted!" in result.stderr # Default abort message from Click goes to stderr
    assert f"Deleting wallet: {alias}" not in result.stdout # Should not proceed to delete
    print("test_wallet_delete_confirm_no: Verified abort with 'n' confirmation.")

# --- Basic Invocation Tests for Other Command Groups ---

# For brevity, we'll test one representative subcommand's --help for each group.
# This ensures the group and subcommand are registered and Click can generate help.

@pytest.mark.parametrize("group_command_args", [
    # account.py
    ["account", "balance", "--help"],
    ["account", "ens", "--help"],
    # analytics.py
    ["analytics", "gas", "--help"],
    ["analytics", "block", "--help"],
    # compile.py
    ["compile", "sol", "--help"],
    ["compile", "verify", "--help"],
    # contract.py
    ["contract", "deploy", "--help"],
    ["contract", "call", "--help"],
    # export.py
    ["export", "--help"], # Test group help as it has options
    ["export", "wallets", "--help"],
    ["export", "transactions", "--help"],
    # network.py
    ["network", "list", "--help"],
    ["network", "add", "--help"],
    # nft.py
    ["nft", "deploy721", "--help"],
    ["nft", "mint721", "--help"],
    ["nft", "uri", "--help"],
    ["nft", "traits", "--help"],
    # scan.py
    ["scan", "audit", "--help"], # External tool, only help
    ["scan", "check", "--help"], # Placeholder, can invoke
    # sign.py
    ["sign", "msg", "--help"],
    ["sign", "verify", "--help"],
    # sync.py
    ["sync", "status", "--help"],
    ["sync", "peers", "--help"],
    # test.py
    ["test", "run", "--help"], # External tool, only help
    ["test", "coverage", "--help"], # External tool, only help
    ["test", "fork", "--help"], # Placeholder/external, only help
    # tx.py
    ["tx", "send", "--help"],
    ["tx", "status", "--help"],
])
def test_other_group_subcommand_help(group_command_args):
    """Test that various other group subcommands show help."""
    command_str = " ".join(group_command_args)
    result = run_eth_command(group_command_args)
    assert result.returncode == 0
    # A bit generic, but 'Usage:' is common in Click's help output.
    assert "Usage:" in result.stdout
    print(f"test_other_group_subcommand_help for 'eth {command_str}': PASSED (found 'Usage:')")

# Specific invocation test for a placeholder command that doesn't just show help
def test_account_balance_invocation(isolated_config_dir): # Uses config for active wallet placeholder
    """Test basic invocation of 'eth account balance' (placeholder)."""
    result = run_eth_command(["account", "balance"])
    assert result.returncode == 0
    assert "Fetching ETH balance for address:" in result.stdout
    assert "ETH Balance: 1.2345 ETH (Example)" in result.stdout
    print("test_account_balance_invocation: Verified placeholder output.")

def test_analytics_gas_invocation():
    """Test basic invocation of 'eth analytics gas' (placeholder)."""
    result = run_eth_command(["analytics", "gas"])
    assert result.returncode == 0
    assert "Fetching current gas prices..." in result.stdout
    assert "Gas Prices (from ExampleOracle):" in result.stdout
    print("test_analytics_gas_invocation: Verified placeholder output.")

# Add more specific invocation tests if a command has simple placeholder logic
# that's worth testing beyond just its --help screen.
# For commands that call external tools (like scan audit, test run),
# only --help tests are safe without having those tools installed.
