import click

from .commands.network import network_group
from .commands.wallet import wallet_group
from .commands.tx import tx_group
from .commands.contract import contract_group
from .commands.compile import compile_group
from .commands.account import account_group
from .commands.analytics import analytics_group
from .commands.sign import sign_group
from .commands.sync import sync_group
from .commands.test import test_group
from .commands.config import config_group
from .commands.help import help_group
from .commands.export import export_group
from .commands.scan import scan_group
from .commands.nft import nft_group
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
