> [!CAUTION]
> **This is a purely EDUCATIONAL project. Do not run it for personal gain or benefit.**
>
> I did not benefit in the creation of this program—all posts were opened in my browser as part of normal forum usage.  
> This project is an experiment with Selenium for learning purposes only.
>
> **I am not liable** for any damages or misuse.

# Roblox DevForum Automation

![Preview](preview.gif)

A tool to automate reading the latest posts from the Roblox DevForum’s **Help and Feedback** and **Bug Reports** categories.  
It can log in automatically if you provide valid cookies and will skip replies you’ve already read.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Cookie Setup](#cookie-setup)
- [Installation](#installation)
  - [Method 1: Poetry](#method-1-poetry)
  - [Method 2: pip](#method-2-pip)
  - [Method 3: Nix](#method-3-nix)

---

## Features

- Uses cookie file for authentication
- Can log output to files with timestamps
- Set read time for replies and delays for posts
- Set percentage of replies to read in each post

You can also run the tool without arguments (provided cookies.json exists), there are optimized defaults.

---

## Prerequisites

- **Python 3.13** installed
- Poetry, pip, or Nix for installation

---

## Cookie Setup

1. Use a tool like [Cookie-Editor](https://cookie-editor.com/) to export your browser cookies as JSON.
2. **You only need to export the `ROBLOSECURITY` cookie**, but exporting all cookies is fine.
3. Save your exported cookies as `cookies.json` in the project directory, or use the `--cookie-file` option to specify a different file path.

> [!CAUTION]
> **Never share your `ROBLOSECURITY` cookie.**
>
> This cookie grants full access to your Roblox account.  
> Keep your `cookies.json` file safe and secure!

---

## Installation

Choose one of the following methods:

### Method 1: Poetry

```bash
poetry install
poetry run devforumauto --help
```

### Method 2: pip

```bash
pip install git+https://github.com/Soikr/devforumauto.git
devforumauto --help
```

### Method 3: Nix

```bash
nix run github:Soikr/devforumauto
# Or to pass arguments:
nix run github:Soikr/devforumauto -- --help
```