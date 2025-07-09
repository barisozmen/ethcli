# ethcli - Ethereum Command Line Interface

`ethcli` is a comprehensive command-line interface for interacting with the Ethereum blockchain, managing wallets, fetching account information, checking network status, and more.

## Features (Work in Progress)

*   Manage multiple Ethereum accounts.
*   Set and store your Ethereum address and API keys.
*   Check ETH balance for your accounts.
*   View recent transaction history for an account (via Etherscan).
*   Get current Ethereum price (via CoinGecko).
*   Fetch detailed information about specific transactions.
*   (Many other features as per the existing command structure - to be documented as they are fully implemented)

## Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd ethcli
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows, use: venv\Scripts\activate
    ```

3.  **Install the package and its dependencies:**
    The `setup.py` file includes dependencies like `click`, `web3`, and `requests`.
    ```bash
    pip install -e .
    ```
    This will install the `eth` command in your environment.

## Configuration

Before using certain features, you need to configure your Ethereum address and API keys. This is done using the `account set` command. The configuration is saved in `ethcli/config.py` (this file should be in your `.gitignore` if you fork/clone and modify).

1.  **Obtain API Keys:**
    *   **Ethereum Node Provider API Key:** You'll need an API key from a node provider like [Infura](https://infura.io/) or [Alchemy](https://www.alchemy.com/). This is required for most on-chain interactions (checking balances, nonces, sending transactions, etc.).
    *   **Etherscan API Key:** To fetch transaction history, you'll need an API key from [Etherscan](https://etherscan.io/apis).

2.  **Set Configuration:**
    Use the `eth account set` command:
    ```bash
    # Set your Ethereum address
    eth account set --address 0xYourEthereumAddress...

    # Set your Node Provider API Key
    eth account set --nodekey YOUR_NODE_PROVIDER_API_KEY

    # Set your Etherscan API Key
    eth account set --scankey YOUR_ETHERSCAN_API_KEY

    # You can also set multiple at once:
    eth account set --address 0x... --nodekey YOUR_NODE_KEY --scankey YOUR_SCAN_KEY
    ```
    If you run `eth account set` without options, it will show you the current stored values (API keys will just show as 'Set' or 'Not set' for privacy).

## Usage Examples

Once installed and configured, you can use the `eth` command followed by the desired command group and subcommand.

### Account Management

*   **Set your details (as shown in Configuration):**
    ```bash
    eth account set --address 0xYourEthAddress --nodekey YOUR_INFURA_OR_ALCHEMY_KEY --scankey YOUR_ETHERSCAN_KEY
    ```

*   **Check your ETH balance:**
    Uses the configured address by default.
    ```bash
    eth account balance
    ```
    To check for a different address:
    ```bash
    eth account balance --address 0xOtherAddress...
    ```

*   **View recent transactions:**
    Uses the configured address and Etherscan API key. Shows last 10 transactions by default.
    ```bash
    eth account transactions
    ```
    Customize the number of transactions and sort order:
    ```bash
    eth account transactions --limit 5 --sort asc
    ```
    Fetch for a different address:
    ```bash
    eth account transactions --address 0xOtherAddress... --limit 20
    ```

*   **Check account nonce:**
    ```bash
    eth account nonce
    ```
    Or for a specific address and block:
    ```bash
    eth account nonce --address 0xOtherAddress... --block latest
    ```

### Network Information

*   **Get current Ethereum price:**
    Default is Ethereum in USD.
    ```bash
    eth network price
    ```
    Get Bitcoin price in EUR:
    ```bash
    eth network price --coin bitcoin --currency eur
    ```

### Transaction Information

*   **Get status and details of a transaction:**
    ```bash
    eth tx status 0xYourTransactionHash...
    ```

## Development

(To be added: instructions for setting up a development environment, running tests, etc.)

## Contributing

(To be added: guidelines for contributing to the project.)

## License

(To be added: specify the license, e.g., MIT License. `setup.py` currently assumes MIT.)