# Testing Quick Start Guide

## The Simple Truth ✨

**Everything happens on YOUR LAPTOP!**

```
┌─────────────────────────────────────┐
│ YOUR LAPTOP                         │
│                                     │
│ 1. Write test here:                │
│    tests/test_ads1293.py           │
│                                     │
│ 2. Run one command:                │
│    ./scripts/run-test.sh \         │
│      tests/test_ads1293.py         │
│                                     │
│ 3. Results appear here:            │
│    analysis/data/2025.../          │
│                                     │
│ 4. Analyze here:                   │
│    jupyter notebook                │
└─────────────────────────────────────┘

That's it! CM4 is used temporarily, nothing stays there.
```

---

## What `run-test.sh` Does Automatically

```
1. Copies tests to CM4           (you don't see this)
2. Runs pytest on CM4             (you see output)
3. Brings results back to laptop  (you get files)
4. Deletes everything from CM4    (cleanup)
```

**Result:** Your laptop has both tests AND results. CM4 stays clean.

---

## Quick Start

```bash
# First time only: Setup
export CM4_IP=192.168.1.100
ssh-copy-id pi@192.168.1.100

# Write test
vim tests/test_my_sensor.py

# Run test (one command!)
./scripts/run-test.sh tests/test_my_sensor.py

# Analyze results
cd analysis/data/$(ls -t analysis/data | head -1)
jupyter notebook
```

---

## Full Documentation

- **For Developers:** [DEVELOPMENT_WORKFLOW.md](docs/DEVELOPMENT_WORKFLOW.md)
- **For Stakeholders:** [TESTING_WORKFLOW.md](docs/TESTING_WORKFLOW.md)
- **JSON API Reference:** [COMPLETE_JSON_API_REFERENCE.md](docs/COMPLETE_JSON_API_REFERENCE.md)

---

**Ready to write your first test!** 🚀
