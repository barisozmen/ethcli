import click

from network_commands import network_group
from wallet_commands import wallet_group
from tx_commands import tx_group
from contract_commands import contract_group
from compile_commands import compile_group
from account_commands import account_group
from analytics_commands import analytics_group
from sign_commands import sign_group
from sync_commands import sync_group
from test_commands import test_group
from config_commands import config_group
from help_commands import help_group
from export_commands import export_group
from scan_commands import scan_group
from nft_commands import nft_group
# ... and so on for all other command groups

@click.group()
def ethcli():
    """
    Ethereum CLI Tool

    A comprehensive command-line interface for interacting with the Ethereum blockchain,
    managing wallets, deploying contracts, and more.
    """
    pass

ethcli.add_command(network_group)
ethcli.add_command(wallet_group)
ethcli.add_command(tx_group)
ethcli.add_command(contract_group)
ethcli.add_command(compile_group)
ethcli.add_command(account_group)
ethcli.add_command(analytics_group)
ethcli.add_command(sign_group)
ethcli.add_command(sync_group)
ethcli.add_command(test_group)
ethcli.add_command(config_group)
ethcli.add_command(help_group)
ethcli.add_command(export_group)
ethcli.add_command(scan_group)
ethcli.add_command(nft_group)
# ... and so on

if __name__ == '__main__':
    ethcli()
