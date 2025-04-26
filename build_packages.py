#!/usr/bin/env python
# build_packages.py - Master Packaging Script for Hospital Management System

import os
import sys
import subprocess
import argparse
import time


def run_script(script_name):
    """Run a Python script and return success status"""
    print(f"\nRunning {script_name}...")
    
    try:
        result = subprocess.run([sys.executable, script_name], check=False)
        if result.returncode == 0:
            print(f"{script_name} completed successfully.")
            return True
        else:
            print(f"{script_name} failed with exit code {result.returncode}.")
            return False
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def build_server():
    """Build the server package"""
    print("=== Building Server Package ===")
    return run_script("package_server.py")

def build_client():
    """Build the client package"""
    print("=== Building Client Package ===")
    return run_script("package_client.py")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Build Hospital Management System packages")
    parser.add_argument("--server", action="store_true", help="Build server package")
    parser.add_argument("--client", action="store_true", help="Build client package")
    parser.add_argument("--all", action="store_true", help="Build both server and client packages")
    
    args = parser.parse_args()
    
    # If no options specified, show help
    if not (args.server or args.client or args.all):
        parser.print_help()
        return 1
    
    start_time = time.time()
    
    results = []
    
    # Build server
    if args.server or args.all:
        server_result = build_server()
        results.append(("Server", server_result))
    
    # Build client
    if args.client or args.all:
        client_result = build_client()
        results.append(("Client", client_result))
    
    # Print summary
    print("\n=== Build Summary ===")
    all_success = True
    for component, success in results:
        status = "Success" if success else "Failed"
        print(f"{component}: {status}")
        if not success:
            all_success = False
    
    elapsed_time = time.time() - start_time
    print(f"\nTotal build time: {elapsed_time:.2f} seconds")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())