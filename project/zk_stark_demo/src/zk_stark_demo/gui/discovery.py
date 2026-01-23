
import os
import pkgutil
import importlib
import argparse
import inspect
from pathlib import Path
from typing import Any, List, Dict, Optional, Type

# Import base classes to check inheritance
from zk_stark_demo.cli.base import BaseProverCLI, BaseVerifierCLI

ROOT_CLI_PACKAGE = "zk_stark_demo.cli"

def _get_cli_package_path() -> Path:
    """Get the absolute path to the CLI package directory."""
    module = importlib.import_module(ROOT_CLI_PACKAGE)
    return Path(module.__file__).parent

def get_implementations() -> List[str]:
    """
    Discover available CLI implementations by scanning subdirectories
    of the cli package.
    """
    implementations = []
    package_path = _get_cli_package_path()
    
    if not package_path.exists():
        return []

    for entry in os.scandir(package_path):
        if entry.is_dir() and not entry.name.startswith("__"):
            # Check if it looks like a CLI impl
            # Should contain prover_cli.py or verifier_cli.py
            if (Path(entry.path) / "prover_cli.py").exists() or \
               (Path(entry.path) / "verifier_cli.py").exists():
                implementations.append(entry.name)
            
    return sorted(implementations)

def _load_cli_class(implementation: str, cli_type: str) -> Optional[Type]:
    """
    Load the CLI class for a given implementation and type.
    cli_type: 'prover' or 'verifier'
    """
    try:
        module_name = f"{ROOT_CLI_PACKAGE}.{implementation}.{cli_type}_cli"
        module = importlib.import_module(module_name)
        
        base_class = BaseProverCLI if cli_type == "prover" else BaseVerifierCLI
        
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, base_class) and obj is not base_class:
                return obj
    except ImportError:
        pass
    return None

def get_schema(implementation: str, cli_type: str) -> Dict[str, Any]:
    """
    Get the argument schema for a specific implementation and type.
    Returns a dictionary describing the arguments.
    """
    cli_class = _load_cli_class(implementation, cli_type)
    if not cli_class:
        return {"error": f"No {cli_type} found for {implementation}"}
        
    # Instantiate CLI to get description and default output/proof
    # Note: Base classes require type args but we can ignore for runtime instantiation
    # or we might need to handle the fact that they are generic. 
    # Actually BaseProverCLI inherits from ABC, so we can instantiate the SUBCLASS.
    try:
        instance = cli_class()
    except Exception as e:
         return {"error": f"Failed to instantiate {cli_class.__name__}: {str(e)}"}

    parser = argparse.ArgumentParser()
    
    # Add base arguments manually to match run() method behavior if needed,
    # or just trust add_arguments.
    # Base run() adds --output or --proof. We should capture those too.
    if cli_type == "prover":
        parser.add_argument("--output", default=instance.default_output, help="Output file")
    else:
        parser.add_argument("--proof", default=instance.default_proof_file, help="Proof file")
        
    instance.add_arguments(parser)
    
    args = []
    for action in parser._actions:
        if action.dest == "help":
            continue
            
        arg_info = {
            "name": action.dest,
            "flags": action.option_strings,
            "help": action.help,
            "default": action.default,
            "type": None,
            "required": action.required
        }
        
        # Infer type
        if action.type:
            if action.type == int:
                arg_info["type"] = "number"
            elif action.type == str:
                arg_info["type"] = "text"
            # Add more types if needed
        elif action.nargs == 0: # Boolean flag
             arg_info["type"] = "boolean"
        else:
             arg_info["type"] = "text" # Default
             
        args.append(arg_info)
        
    return {
        "description": instance.description,
        "arguments": args
    }
