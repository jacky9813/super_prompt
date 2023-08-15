import sys
import argparse
import logging
import logging.handlers
import os
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

import argcomplete

from . import config
from . import color
from . import types

CONFIG_FILE = "~/.config/super_prompt"

logger = logging.getLogger("super_prompt")


def main():
    # Log Setup
    if not os.path.exists(os.path.expanduser("~/.local/log")):
        os.makedirs(os.path.expanduser("~/.local/log"), exist_ok=True)
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s %(filename)s:%(lineno)d(%(name)s) - %(message)s",
        level=logging.WARNING,
        handlers=[
            logging.handlers.RotatingFileHandler(
                os.path.expanduser("~/.local/log/super-prompt.log"),
                backupCount=3,
                maxBytes=4000
            ),
            *(
                [] if "run" in sys.argv else [
                    logging.StreamHandler()
                ]
            )
        ]
    )

    # Argparser setup
    parser = argparse.ArgumentParser(add_help=True)
    parser_action = parser.add_subparsers(title="Actions", dest="action")

    parser_action.add_parser("help", help="Show help message.")

    parser_run = parser_action.add_parser("run", help="Generate super prompt", add_help=False)

    parser_config = parser_action.add_parser("config", help="Configure super prompt", add_help=False)
    config_callback = config.configure_subparser(parser_config)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # Enumerate plugins
    discovered_plugins = {
        ep.name: ep
        for ep in entry_points(group='super_prompt.plugins')
    }
    program_config = config.get_config()

    if not args.action or args.action == "help":
        # Default to help if no action mentioned
        parser.print_help()
        exit(0)
    elif args.action == "run":
        result_list = []
        context_color_raw = program_config.get("core", {}).get("context_color", 33)
        if hasattr(context_color_raw, "__iter__") and len(context_color_raw) == 3:
            context_color = color.rgb_color(*context_color_raw)
        elif isinstance(context_color_raw, int):
            context_color = color.ansi_color(context_color_raw)
        else:
            context_color = color.ansi_color(33) # Yellow
        for enabled_plugin in program_config.get("core", {}).get("enabled_plugins", []):
            if enabled_plugin in discovered_plugins:
                result: types.PluginResponse = (discovered_plugins[enabled_plugin].load())(
                    program_config.get("plugins", {}).get(enabled_plugin, {})
                )
                if result is not None:
                    result_list.append(
                        f'{color.color(result.logo_color)}{result.logo} {context_color}{result.context}{color.reset_color()}'
                    )
            else:
                logger.error("Plugin not found: %s", enabled_plugin)
        print(" ".join(result_list), end="")
    elif args.action == "config":
        
        exit(config_callback(args, discovered_plugins))

if __name__ == "__main__":
    main()
