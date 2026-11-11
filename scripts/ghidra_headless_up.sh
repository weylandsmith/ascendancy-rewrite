#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# Start the GhidraMCP headless server (HTTP on 127.0.0.1:8089) unless already up.
# The Hermes 'ghidra' MCP bridge (stdio) multiplexes onto this server.
# Idempotent; safe to call at the start of any turn that needs Ghidra.
set -eu
GHIDRA_HOME=${GHIDRA_HOME:-$HOME/tools/ghidra}
JAR=$(ls "$HOME/tools/ghidra-mcp/target/GhidraMCP-"*".jar" 2>/dev/null | grep -v sources | head -1 || true)
if [ -z "${JAR}" ]; then
  echo "GhidraMCP jar not built yet; building with maven (this takes ~10 min first time)"
  (cd "$HOME/tools/ghidra-mcp" && JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 \
    GHIDRA_INSTALL_DIR="$GHIDRA_HOME" mvn -q package -DskipTests)
  JAR=$(ls "$HOME/tools/ghidra-mcp/target/GhidraMCP-"*".jar" | grep -v sources | head -1)
fi
if curl -s -m 2 http://127.0.0.1:8089/health >/dev/null 2>&1; then
  echo "ghidra headless already running: $(curl -s -m 2 http://127.0.0.1:8089/health | head -c 200)"
  exit 0
fi
CP="$JAR"
for jar in "$GHIDRA_HOME"/Ghidra/Framework/*/lib/*.jar "$GHIDRA_HOME"/Ghidra/Features/*/lib/*.jar "$GHIDRA_HOME"/Ghidra/Processors/*/lib/*.jar; do CP="$CP:$jar"; done
mkdir -p "$HOME/projects/ascendancy/.logs"
# run_script_inline is gated by this env var in GhidraMCP >= 5.4.1; P2 needs
# scripted analysis (create functions / bulk xrefs) because a raw binary gets
# 0 function symbols from auto-analysis alone.
export GHIDRA_MCP_ALLOW_SCRIPTS=1
nohup java -Xmx3g -XX:+UseG1GC -Dghidra.home="$GHIDRA_HOME" -Dapplication.name=GhidraMCP \
  -classpath "$CP" com.xebyte.headless.GhidraMCPHeadlessServer \
  --port 8089 --bind 127.0.0.1 > "$HOME/projects/ascendancy/.logs/ghidra_headless.log" 2>&1 &
echo "starting ghidra headless (pid $!), log: ~/projects/ascendancy/.logs/ghidra_headless.log"
for i in $(seq 1 60); do
  sleep 2
  curl -s -m 2 http://127.0.0.1:8089/health >/dev/null 2>&1 && { echo "UP after ~$((i*2))s"; exit 0; }
done
echo "FAILED to come up in 120s; tail of log:"; tail -20 "$HOME/projects/ascendancy/.logs/ghidra_headless.log"; exit 1
