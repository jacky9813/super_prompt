import argparse
import typing
import os
import logging
import sys
if sys.version_info < (3, 10):
    from importlib_metadata import Entrypoint, entry_points
else:
    from importlib.metadata import EntryPoint, entry_points
import re

import mergedeep
import tabulate
import toml

from . import types

logger = logging.getLogger("super_prompt_config")

CONFIG_FILE_LOCATION = os.path.expanduser("~/.config/super-prompt.toml")

OPTION_KEY_CONSTRAIN = re.compile(r"^[a-z0-9\.]*$")

def _raise(exc):
    raise exc

def color(value: str):
    try:
        return int(value)
    except ValueError:
        pass
    match = re.search(r"\[\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*\]", value)
    if match is None:
        raise ValueError('Color must be either an ansi color code or RGB with "[<R>, <G>, <B>]" expression.')
    return [
        int(group)
        for group in match.groups()
    ]
    

core_config_hints = {
    "enabled_plugins": types.ConfigHint(
        "enabled_plugins",
        f'A list of enabled plugins. Use "{sys.argv[0]} config enable-plugin" and "{sys.argv[0]} config disable-plugin" to modify this option.',
        "[]",
        lambda x: _raise(ValueError(f'Use "{sys.argv[0]} config enable-plugin" and "{sys.argv[0]} config disable-plugin" to modify this option.'))
    ),
    "context_color": types.ConfigHint(
        "context_color",
        "The color to be used in expressing context of an application.",
        "33 (Yellow)",
        color
    )
}


def get_config() -> dict:
    if not os.path.exists(CONFIG_FILE_LOCATION):
        return {}
    with open(CONFIG_FILE_LOCATION, mode="r") as config_fd:
        config = toml.load(config_fd)
    return config


def configure_subparser(
    parser: argparse.ArgumentParser
) -> typing.Callable[[argparse.Namespace], int]:
    subparsers = parser.add_subparsers(title="Actions", dest="config_action")
    parser_disable_plugin = subparsers.add_parser(
        "disable-plugin",
        help="Disable a plugin.",
        description="Disable a plugin."
    )
    parser_disable_plugin.add_argument("plugin_name", help="The name of the plugin to be disabled.")
    parser_enable_plugin = subparsers.add_parser(
        "enable-plugin",
        help="Enable a plugin.",
        description="Enable a plugin."
    )
    parser_enable_plugin.add_argument("plugin_name", help="The name of the plugin to be enabled.")
    parser_list_installed_plugin = subparsers.add_parser(
        "list-plugins",
        help="List installed plugins.",
        description="List installed plugins."
    )
    parser_set = subparsers.add_parser(
        "set",
        help="Set value in configuration.",
        description="Set value in configuration."
    )
    parser_set.add_argument("option_key")
    parser_set.add_argument("option_value")
    parser_unset = subparsers.add_parser(
        "unset",
        help="Remove option from configuration.",
        description="Remove option from configuration."
    )
    parser_unset.add_argument("option_key")
    parser_help = subparsers.add_parser("help", help="Show this message amd exit.", add_help=False)

    
    plugin_config = {
        entry_point.name: entry_point
        for entry_point in entry_points(group="super_prompt.plugin_config")
    }

    def config_callback(args: argparse.Namespace, plugin_list: typing.Dict[str, EntryPoint]):
        current_config = get_config()
        if not args.config_action or args.config_action == "help":
            parser.print_help()
            return 0
        if args.config_action == "list-plugins":
            print(tabulate.tabulate(
                [
                    [
                        "*" if entrypoint.name in current_config.get("core", {}).get("enabled_plugins", []) else "",
                        entrypoint.name,
                        "\n".join([
                            str(config_option_help)
                            for config_option_help in (
                                plugin_config[entrypoint.name].load()
                                if entrypoint.name in plugin_config
                                else lambda : []
                            )()
                        ]) or "No config options"
                    ]
                    for entrypoint in plugin_list.values()
                ],
                [
                    "Enabled",
                    "Plugin Name",
                    "Configuration Options"
                ]
            ))
            return 0
        if args.config_action == "enable-plugin":
            if args.plugin_name not in plugin_list:
                logger.fatal("No plugin named %s", args.plugin_name)
                return 1
            if "core" not in current_config:
                current_config["core"] = {}
            if "enabled_plugins" not in current_config["core"]:
                current_config["core"]["enabled_plugins"] = []
            if args.plugin_name in current_config["core"]["enabled_plugins"]:
                logger.warning("Plugin %s has already been enabled", args.plugin_name)
                return 0
            current_config["core"]["enabled_plugins"].append(args.plugin_name)
            with open(CONFIG_FILE_LOCATION, mode="w") as config_fd:
                toml.dump(current_config, config_fd)
        if args.config_action == "disable-plugin":
            if "core" not in current_config:
                current_config["core"] = {}
            if "enabled_plugins" not in current_config["core"]:
                current_config["core"]["enabled_plugins"] = []
            if args.plugin_name not in current_config["core"]["enabled_plugins"]:
                logger.warning("Plugin %s has already been disabled", args.plugin_name)
                return 0
            current_config["core"]["enabled_plugins"].remove(args.plugin_name)
            with open(CONFIG_FILE_LOCATION, mode="w") as config_fd:
                toml.dump(current_config, config_fd)
        if args.config_action == "set":
            keys = args.option_key.split(".")
            # Search type for config
            value_type = None
            if len(keys) < 2:
                raise IndexError("No such option: %s", args.option_key)
            if keys[0] == "core":
                if len(keys) != 2:
                    raise IndexError("No such option: %s", args.option_key)
                if keys[1] not in core_config_hints:
                    raise IndexError("No such option: %s", args.option_key)
                value_type = core_config_hints[keys[1]].value_type
            elif keys[0] == "plugins" and keys[1] in plugin_config and len(keys) >= 3:
                plugin_config_options = {
                    config_option.key: config_option
                    for config_option in (plugin_config[keys[1]].load())()
                }
                if ".".join(keys[2:]) in plugin_config_options:
                    value_type = plugin_config_options[".".join(keys[2:])].value_type
            
            if value_type is None:
                raise IndexError("No such option: %s", args.option_key)

            # Convert dot notaion to dict
            change = {
                keys[-1]: value_type(args.option_value)
            }
            for key in reversed(keys[:-1]):
                change = {key: change}

            # Apply change to current config
            mergedeep.merge(current_config, change)

            with open(CONFIG_FILE_LOCATION, mode="w") as config_fd:
                toml.dump(current_config, config_fd)
        if args.config_action == "unset":
            keys = args.option_key.split(".")
            # Since referencing the content will not do deep copy of the value,
            # we can leverage this behavior to remove settings.
            cursor = current_config
            while len(keys) > 1:
                cursor = cursor[keys.pop(0)]
            
            del cursor[keys[0]]
            with open(CONFIG_FILE_LOCATION, mode="w") as config_fd:
                toml.dump(current_config, config_fd)
    
    return config_callback

