#!/bin/bash
# Start both Watcher and Orchestrator for AI Employee (Bronze Tier)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "AI Employee - Bronze Tier"
echo "========================================"
echo "Vault: $VAULT_DIR"
echo ""

# Start watcher in background
echo "Starting Filesystem Watcher..."
cd "$SCRIPT_DIR"
python3 filesystem_watcher.py "$VAULT_DIR" &
WATCHER_PID=$!
echo "Watcher started (PID: $WATCHER_PID)"

# Start orchestrator in background
echo "Starting Orchestrator..."
python3 orchestrator.py "$VAULT_DIR" &
ORCHESTRATOR_PID=$!
echo "Orchestrator started (PID: $ORCHESTRATOR_PID)"

echo ""
echo "Both processes running."
echo "Press Ctrl+C to stop all."
echo ""

# Wait for interrupt
trap "kill $WATCHER_PID $ORCHESTRATOR_PID 2>/dev/null; exit" INT TERM

wait
