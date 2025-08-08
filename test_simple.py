#!/usr/bin/env python3
import subprocess
import os

def test_direct():
    print("Direct execution:")
    result = subprocess.run(['tidy-viewer', '../data/iris.csv'], capture_output=True, text=True)
    print("STDOUT:")
    print(repr(result.stdout))
    print("STDERR:")
    print(repr(result.stderr))
    print("Return code:", result.returncode)

if __name__ == "__main__":
    test_direct()
