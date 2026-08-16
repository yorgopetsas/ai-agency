# OpenCode CLI + Ollama Complete Guide

---

**Comprehensive Guide to OpenCode CLI and Ollama**

This tutorial provides a step-by-step guide to installing, configuring, and using OpenCode CLI and Ollama. Follow along to streamline your workflow and achieve greater productivity.

**Step 1: Install OpenCode CLI and Ollama**

### Installing OpenCode CLI

To install OpenCode CLI, use one of the following methods:

```bash
# Method 1: Quick install (recommended)
curl -fsSL https://opencode.ai/install | bash

# Method 2: Homebrew
brew install opencode

# Method 3: npm
npm install -g @opencode-ai/cli
```

### Installing Ollama

To install Ollama, use one of the following methods:

```bash
# Method 1: Homebrew (recommended)
brew install ollama

# Method 2: Direct download
curl -fsSL https://ollama.com/install.sh | sh
```

**Step 2: Verify Installation**

After installation, verify that OpenCode CLI and Ollama are working correctly by running the following commands:

```bash
opencode --version
ollama --version
```

**Step 3: Configure OpenCode to Use Ollama**

To configure OpenCode to use Ollama, follow these steps:

1. Install Ollama first.
2. Install OpenCode CLI.
3. Edit the `opencode.jsonc` configuration file at `~/.config/opencode/opencode.jsonc` to specify the Ollama model and other settings.

**Step 4: Test OpenCode with Ollama**

To test OpenCode with Ollama, run the following command:

```bash
opencode run "Hello from local Ollama!"
```

**Troubleshooting Tips**

### Common Issues

* "ollama: command not found" - Add `export PATH="/usr/local/bin:$PATH"` and restart your terminal.
* "opencode: command not found" - Add `export PATH="$HOME/.opencode/bin:$PATH"` to your `.zshrc` file.

### Performance Tips

* Use smaller models (e.g., Llama 3.2 3B) for faster performance.
* Close other resource-intensive applications to free up RAM.
* Enable Metal acceleration (automatic on M-series Macs) for improved performance.

**Recommended Models by RAM**

| RAM | Model |
|-----|-------|
| 8GB | Llama 3.2 3B |
| 16GB+ | Qwen 3 8B |
| 32GB+ | Llama 3.1 70B |
| 64GB+ | Llama 3.3 70B |

### Advanced Tips

* To optimize performance, use the `--model` flag followed by the desired model name.
* Use the `--prompt` flag to specify a custom prompt for your Ollama model.

**Additional Resources**

* For more information on OpenCode CLI and Ollama, visit the official documentation at [opencode.ai/docs](http://opencode.ai/docs).
* Join the OpenCode community on Discord to connect with other users and get help with any issues: [discord.gg/opencode](http://discord.gg/opencode).

By following this comprehensive guide, you'll be able to streamline your workflow and achieve greater productivity with OpenCode CLI and Ollama.