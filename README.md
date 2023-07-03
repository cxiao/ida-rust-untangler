# IDA Rust Untangler

## Usage

Use the plugin by clicking _Edit > Rust Untangler > Demangle Rust function names_ in IDA's menu, or by pressing `Ctrl+Alt+D`.

![Screenshot of the Edit > Rust Untangler > Demangle Rust function names entry in the IDA menu](images/plugin-menu-entry-screenshot.png)

Before:

![Image of a decompiled function with the Rust-mangled name `_$LT$alloc..string..String$u20$as$u20$core..fmt..Write$GT$::write_str::h461a5a8697e61a03`](images/decompiler-window-before-demangle-screenshot.png)

After:

![Image of a decompiled function with the original demangled Rust name `<alloc::string::String as core::fmt::Write>::write_str::h461a5a8697e61a03`](images/decompiler-window-after-demangle-screenshot.png)

Because IDA has limitations on the characters that can be used in function names, not all functions can be directly renamed to their demangled equivalents. In cases where a function cannot be renamed to the actual demangled name, a comment with the actual demangled name is set on the function.

## FAQ

_Why are there strings like `h461a5a8697e61a03` after all my functions, even after demangling?_

This is a hash, unique per-function, applied by the Rust compiler when mangling names. The purpose of the hash is to disambiguate between symbols which may have the same name.

You can read more about the reasons for needing this disambiguating hash in [Rust RFC 2603](https://rust-lang.github.io/rfcs/2603-rust-symbol-name-mangling-v0.html#requirements-for-a-symbol-mangling-scheme), which proposes a new name mangling scheme to replace the current one:

> "Unambiguous" means that no two distinct compiler-generated entities (that is, mostly object code for functions) must be mapped to the same symbol name. This disambiguation is the main purpose of the hash-suffix in the current, legacy mangling scheme.

The presence of this hash does not mean that the demangling failed; some demangling tools / libs [like rustc_demangle have the option to drop it when demangling](https://github.com/rust-lang/rustc-demangle/pull/5), but it's left intact in this plugin.

## Installation

1. Install the Python dependencies from this repository's [`requirements.txt`](requirements.txt).

In the Python environment used by IDA, run
```
pip install -r requirements.txt
```

2. Copy [`ida_rust_untangler.py`](ida_rust_untangler.py) into your IDA plugins directory.

The exact location of the IDA plugins directory will vary by operating system, as well as the location of your IDA user directory (`$IDAUSR`). By default, they are in the following locations:

Windows:

```
%APPDATA%/Hex-Rays/IDA Pro/plugins/
```

MacOS / Linux:

```
$HOME/.idapro/plugins/
```

Alternatively, you can find the location of the IDA plugins directory on your system by running the following snippet of Python code in IDA's Python console:

```python
import idaapi, os; print(os.path.join(idaapi.get_user_idadir(), "plugins"))
```

## Attribution

The main demangling logic in this plugin is performed by the [`rust_demangler`](https://github.com/teambi0s/rust_demangler) Python library, by Team bi0s.
