import logging

import rust_demangler
from rust_demangler.rust import TypeNotFoundError

import idaapi
import idautils

logger = logging.getLogger(__name__)


class ActionHandler(idaapi.action_handler_t):
    # Plugin registration code taken from https://gist.github.com/cmatthewbrooks/7e0c5f4e81927b9d1d6acbb702db3bfc
    def __init__(self, callback):
        idaapi.action_handler_t.__init__(self)
        self.callback = callback

    def activate(self, ctx):
        self.callback()
        return 1

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS


class RustUntanglerPlugin(idaapi.plugin_t):
    wanted_name = "Rust Untangler"
    wanted_hotkey = ""
    comment = ""
    help = ""
    # Because we set up our own entries in the Edit > Rust Untangler menu,
    # set the PLUGIN_HIDE flag here so that we don't also have an entry in the Edit > Plugins menu.
    flags = idaapi.PLUGIN_HIDE

    def register_plugin_actions(self):
        # Plugin registration code taken from https://gist.github.com/cmatthewbrooks/7e0c5f4e81927b9d1d6acbb702db3bfc
        plugin_actions = [
            {
                "id": "rust_untangler:demangle",
                "name": "Demangle Rust function names",
                "hotkey": "Ctrl+Alt+D",
                "comment": "Demangle all mangled Rust function names in the current database",
                "callback": self.demangle_action,
                "menu_location": "Edit/Rust Untangler/Demangle",
            },
        ]

        for action in plugin_actions:
            if not idaapi.register_action(
                idaapi.action_desc_t(
                    action["id"],  # Must be the unique item
                    action["name"],  # The name the user sees
                    ActionHandler(action["callback"]),  # The function to call
                    action["hotkey"],  # A shortcut, if any (optional)
                    action["comment"],  # A comment, if any (optional)
                )
            ):
                logger.error(f"Failed to register {action['id']}")

            if not idaapi.attach_action_to_menu(
                action["menu_location"],  # The menu location
                action["id"],  # The unique function ID
                0,
            ):
                logger.error(f"Failed to attach to menu {action['id']}")

    def init(self):
        """
        Callback function which IDA runs on plugin load.
        """
        logger.info("Initialized Rust Untangler plugin.")
        self.register_plugin_actions()
        # This is a persistent plugin which registers keyboard shortcuts and actions
        # rather than just running once, so use the PLUGIN_KEEP flag here.
        return idaapi.PLUGIN_KEEP

    def run(self, _arg):
        """
        Callback function which IDA runs when the main plugin action
        is invoked, either via the Edit > Plugins menu or as a script.
        Because we hide our plugin from the Edit > Plugins menu and instead
        register all our actions in the menu ourselves, this function does nothing.
        """
        pass

    def demangle_action(self):
        for func_address in idautils.Functions():
            func_name = idaapi.get_func_name(func_address)
            func_object = idaapi.get_func(func_address)

            logger.debug(f"{func_address:#x}, {func_name}")
            try:
                demangled_name = rust_demangler.demangle(func_name)
                logger.info(f"Demangled: {func_address:#x}, {demangled_name}")

                # Automatically replace invalid characters with `_` (via SN_NOCHECK),
                # and automatically append a numerical suffix to the name if it already exists (via SN_FORCE).
                result = idaapi.set_name(
                    func_address, demangled_name, idaapi.SN_NOCHECK | idaapi.SN_FORCE
                )
                logger.info(
                    f"Renaming name {func_name} at address {func_address:#x} to demangled name {demangled_name}"
                )
                if not result:
                    logger.warn(
                        f"Failed to rename name {func_name} at address {func_address:#x} to demangled name {demangled_name}"
                    )

                # Also write a comment with the actual demangled name,
                # without automatically replaced invalid characters.
                result = idaapi.set_func_cmt(func_object, demangled_name, 1)
                if not result:
                    logger.warn(
                        f"Failed to set comment for name {func_name} at address {func_address:#x} with demangled name {demangled_name}"
                    )

            except TypeNotFoundError as err:
                logger.warn(f"Unable to demangle {func_name}: {err.message}")

            except Exception as err:
                logger.error(f"Unable to demangle {func_name}: {err}")

    def term(self):
        """
        Callback function which IDA runs on plugin unload.
        """
        logger.info("Terminating Rust Untangler plugin.")


def PLUGIN_ENTRY():
    """
    Entry point for IDAPython plugins.
    """
    return RustUntanglerPlugin()
