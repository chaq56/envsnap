# envsnap

> CLI tool to snapshot, diff, and restore environment variable sets across projects.

---

## Installation

```bash
pip install envsnap
```

Or install from source:

```bash
git clone https://github.com/yourname/envsnap.git && cd envsnap && pip install .
```

---

## Usage

**Take a snapshot of the current environment:**
```bash
envsnap save myproject
```

**List saved snapshots:**
```bash
envsnap list
```

**Diff two snapshots:**
```bash
envsnap diff myproject staging
```

**Restore a snapshot:**
```bash
envsnap restore myproject
```

**Export a snapshot to a `.env` file:**
```bash
envsnap export myproject > .env
```

---

## How It Works

`envsnap` captures the current set of environment variables and stores them locally under a named snapshot. You can compare snapshots across branches, machines, or projects to quickly spot missing or changed variables — no more "works on my machine" surprises.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Contributions welcome. Open an issue or submit a pull request.*