# openai-toolbelt

> Batteries-included helper layer on top of the official [openai-python](https://github.com/openai/openai-python) SDK.

![PyPI](https://img.shields.io/pypi/v/openai-toolbelt) ![License](https://img.shields.io/github/license/yourname/openai-toolbelt)

---

## ✨ Why?

The OpenAI SDK already covers every endpoint, but real-world apps need:

* Centralized config (model defaults, organization IDs, etc.)
* Automatic retries & exponential back-off
* Cost and token accounting
* Transparent request/response logging
* Easy caching for deterministic prompts
* Opinionated helpers for common patterns (chat, embeddings, audio, images, file upload)
* Async *and* sync flavours with identical APIs

`openai-toolbelt` gives you those features in one import, so you can focus on building.

---

## 🔧 Installation

```bash
pip install openai-toolbelt    # pulls in openai>=X.XX as a dependency
