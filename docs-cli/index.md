# Mercury CLI

## Overview

`mercury-cli` is an interactive command-line interface (CLI) tool designed to simplify using the [Mercury OCIP](https://github.com/Fourteen-IP/mercury-ocip) Library. All automations and operations that can be performed using Mercury OCIP can now be executed through an intuitive CLI with autocomplete functionality.

### Example

```asciinema-player
{
    "file": "assets/asciinema/intro.cast",
    "title": "Intro",
    "mkap_theme": "none",
    "theme": "dracula",
    "fit": "width",
    "cols": 120,
    "rows": 24,
    "autoplay": true
}
```

## Installation

To install `mercury-cli`, use pip:

```bash
pip install mercury-cli
```

You can then run the CLI using the following command:

```bash
mercury-cli
```

!!! Info

    In some cases, windows defender may complain because the package is not signed. You can run the module directly instead:

    ```bash
    python -m mercury_cli
    ```

This runs the module and starts the interactive CLI session. From here you can run commands and do some automations!

See the Commands section for more details on commands and features available in `mercury_cli`.

## Quick Login

You can pass parameters to `mercury-cli` when starting it from the command line. For example:

```bash
mercury_cli --username your.username --password-env YOUR_PASSWORD_ENV_VARIABLE --host https://mercury.example.com/webservice/services/ProvisioningService
```

Additionally, you can use `--no-login` to skip the login process:

```bash
mercury_cli --no-login
```

or `--action` to login and immediately execute a command:

```bash
mercury_cli --username your.username --password-env YOUR_PASSWORD_ENV_VARIABLE --host https://mercury.example.com/webservice/services/ProvisioningService --action "automations find_alias SVPID GRPID 1234"
```

This will drop you directly into the CLI with the provided credentials.

<small style="opacity: 0.1;"><a href="assets/mercury/" style="color: inherit; text-decoration: none;">*Try typing the project name as a command... 🐍*</a></small>