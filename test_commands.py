import click
import subprocess # For running external test runners
import os

@click.group('test')
def test_group():
    """Run contract tests locally, often using a development framework."""
    pass

@test_group.command('run')
@click.argument('test_file_or_dir', type=click.Path(exists=True), required=False)
@click.option('--framework', type=click.Choice(['hardhat', 'foundry', 'truffle', 'custom'], case_sensitive=False),
              help="Specify the testing framework. If 'custom', provide full command with --custom-command.")
@click.option('--custom-command', type=str, help="Full custom command to run tests (e.g., 'npm run test:specific').")
# We could add options like --grep to filter tests by name
def run_tests(test_file_or_dir, framework, custom_command):
    """
    Run test script(s). Detects common frameworks or uses a custom command.
    If TEST_FILE_OR_DIR is provided, it will be passed to the test runner if supported.
    """
    if custom_command:
        click.echo(f"Running custom test command: {custom_command}")
        # It's good practice to split the command string into a list for subprocess
        # For simplicity here, we assume it's well-formed or the user knows what they're doing.
        # A more robust solution would parse it carefully.
        try:
            process = subprocess.run(custom_command, shell=True, check=True, text=True, capture_output=True)
            click.echo("Custom command output:\n" + process.stdout)
            if process.stderr:
                click.echo("Custom command errors:\n" + process.stderr, err=True)
            click.echo("Custom command executed successfully.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Custom command failed with exit code {e.returncode}.", err=True)
            click.echo("Output:\n" + e.stdout, err=True)
            click.echo("Errors:\n" + e.stderr, err=True)
        except FileNotFoundError:
            click.echo(f"Error: Custom command not found. Make sure it's in your PATH or a valid script.", err=True)
        return

    detected_framework = framework
    if not detected_framework:
        # Basic framework detection
        if os.path.exists("hardhat.config.js") or os.path.exists("hardhat.config.ts"):
            detected_framework = "hardhat"
        elif os.path.exists("foundry.toml"):
            detected_framework = "foundry"
        elif os.path.exists("truffle-config.js"):
            detected_framework = "truffle"
        else:
            click.echo("Could not automatically detect testing framework (Hardhat, Foundry, Truffle).")
            click.echo("Please specify with --framework or use --custom-command.", err=True)
            return

    click.echo(f"Using testing framework: {detected_framework}")
    cmd = []
    if detected_framework == "hardhat":
        cmd = ["npx", "hardhat", "test"]
        if test_file_or_dir:
            cmd.append(test_file_or_dir)
    elif detected_framework == "foundry":
        cmd = ["forge", "test"]
        if test_file_or_dir: # Foundry test might take specific options for file/contract/test function
            click.echo(f"Note: For Foundry, targeting specific files/tests usually involves options like --match-path, --match-contract, --match-test.")
            click.echo(f"Passing '{test_file_or_dir}' directly might not work as expected without specific matching options.")
            # cmd.extend(["--match-path", test_file_or_dir]) # Example, needs refinement
    elif detected_framework == "truffle":
        cmd = ["npx", "truffle", "test"]
        if test_file_or_dir:
            cmd.append(test_file_or_dir)

    if not cmd:
        click.echo(f"Framework {detected_framework} is chosen, but automatic command construction is not fully implemented yet.", err=True)
        return

    click.echo(f"Executing command: {' '.join(cmd)}")
    try:
        # Using shell=False is generally safer if cmd is a list
        process = subprocess.run(cmd, check=True, text=True, capture_output=True) # Use capture_output to get stdout/stderr
        click.echo("Test run output:\n" + process.stdout)
        if process.stderr:
             click.echo("Test run errors (if any):\n" + process.stderr, err=True) # Some tools output to stderr even on success
        click.echo(f"{detected_framework.capitalize()} tests completed successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"{detected_framework.capitalize()} tests failed with exit code {e.returncode}.", err=True)
        click.echo("Output:\n" + e.stdout, err=True)
        click.echo("Errors:\n" + e.stderr, err=True)
    except FileNotFoundError:
        click.echo(f"Error: Command for {detected_framework} not found. Is it installed and in your PATH?", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)


@test_group.command('coverage')
@click.option('--framework', type=click.Choice(['hardhat', 'foundry', 'custom'], case_sensitive=False),
              help="Specify the testing framework. If 'custom', provide full command with --custom-command.")
@click.option('--custom-command', type=str, help="Full custom command to run coverage (e.g., 'npm run coverage').")
def show_coverage(framework, custom_command):
    """Show test coverage (requires framework support, e.g., solidity-coverage for Hardhat)."""
    if custom_command:
        click.echo(f"Running custom coverage command: {custom_command}")
        try:
            subprocess.run(custom_command, shell=True, check=True)
            click.echo("Custom coverage command executed successfully.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Custom coverage command failed with exit code {e.returncode}.", err=True)
        except FileNotFoundError:
            click.echo(f"Error: Custom command not found.", err=True)
        return

    detected_framework = framework
    if not detected_framework:
        if os.path.exists("hardhat.config.js") or os.path.exists("hardhat.config.ts"):
            detected_framework = "hardhat"
        elif os.path.exists("foundry.toml"):
            detected_framework = "foundry"
        else:
            click.echo("Could not automatically detect framework for coverage (Hardhat, Foundry).")
            click.echo("Please specify with --framework or use --custom-command.", err=True)
            return

    click.echo(f"Attempting to run coverage for framework: {detected_framework}")
    cmd = []
    if detected_framework == "hardhat":
        # Assumes solidity-coverage is installed and configured
        cmd = ["npx", "hardhat", "coverage"]
    elif detected_framework == "foundry":
        cmd = ["forge", "coverage"]
        # May need additional options like --report lcov or --report summary

    if not cmd:
        click.echo(f"Coverage for {detected_framework} is chosen, but automatic command construction is not fully implemented.", err=True)
        return

    click.echo(f"Executing command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        click.echo(f"{detected_framework.capitalize()} coverage report generated.")
        if detected_framework == "hardhat":
            click.echo("Coverage report typically found in ./coverage/index.html or terminal output.")
        elif detected_framework == "foundry":
            click.echo("Coverage report typically found in ./coverage/ or terminal output. Use 'forge coverage --report summary' for quick view.")
    except subprocess.CalledProcessError as e:
        click.echo(f"{detected_framework.capitalize()} coverage command failed.", err=True)
    except FileNotFoundError:
        click.echo(f"Error: Command for {detected_framework} coverage not found. Is it installed and configured (e.g., solidity-coverage for Hardhat)?", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred during coverage: {e}", err=True)


@test_group.command('fork')
@click.argument('network_to_fork', type=str, default="mainnet") # e.g., mainnet, goerli, or a custom RPC URL
@click.option('--block-number', type=int, help="Fork from a specific block number.")
@click.option('--port', type=int, default=8545, help="Port for the local forked node.")
# This command would typically start a local node (Anvil/Hardhat Node) configured to fork a live network.
# Then, subsequent `ethcli test run` or other commands would target this local forked node.
def run_on_fork(network_to_fork, block_number, port):
    """Run tests on a mainnet (or other network) fork. (Starts a local forked node)."""
    click.echo(f"Preparing to start a local forked node from: {network_to_fork}")
    if block_number:
        click.echo(f"Forking from block number: {block_number}")
    click.echo(f"Local node will run on port: {port}")

    # Placeholder: This requires starting a local node like Anvil or Hardhat Node
    # with appropriate forking configuration.

    # Example for Anvil (Foundry):
    # cmd_anvil = ["anvil", "--fork-url", network_to_fork_rpc_url, "--port", str(port)]
    # if block_number: cmd_anvil.extend(["--fork-block-number", str(block_number)])

    # Example for Hardhat Node:
    # This is usually configured in hardhat.config.js and run via `npx hardhat node`
    # Or can be started programmatically, but that's more involved.

    click.secho("This command is a placeholder for starting a local forked development node.", fg='yellow')
    click.echo("You would typically use a tool like Anvil (Foundry) or Hardhat Node.")
    click.echo("Example (Anvil):")
    rpc_url = f"https://{network_to_fork}.infura.io/v3/YOUR_INFURA_ID" if not network_to_fork.startswith("http") else network_to_fork
    anvil_cmd_parts = ["anvil", "--fork-url", rpc_url, "--port", str(port)]
    if block_number:
        anvil_cmd_parts.extend(["--fork-block-number", str(block_number)])
    click.echo(f"  {' '.join(anvil_cmd_parts)}")
    click.echo("\nOnce the forked node is running, configure ethcli to use it (e.g., `ethcli network use local_fork`)")
    click.echo("and then run your tests: `ethcli test run` (ensure your tests are configured for this network).")

if __name__ == '__main__':
    test_group()
