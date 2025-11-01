#!/usr/bin/env bash
set -euo pipefail

echo "== verify g++ version =="
g++ --version || true

echo "== compile test (C++23) =="
cat > /tmp/test.cpp <<'CPP'
#include <iostream>
int main(){
    std::cout << "devcontainer: g++ is working (C++23)\n";
    return 0;
}
CPP

g++ -std=gnu++23 -O2 /tmp/test.cpp -o /tmp/test.out && /tmp/test.out || true

echo "== finished post-create checks =="
