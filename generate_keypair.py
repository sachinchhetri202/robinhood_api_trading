#!/usr/bin/env python3
"""
Helper script to generate Ed25519 keypair for Robinhood API

This script generates an Ed25519 keypair that you can use with Robinhood:
1. Run this script to generate a keypair
2. Copy the PRIVATE KEY (Base64) to your .env file as BASE64_PRIVATE_KEY
3. Copy the PUBLIC KEY (Base64) and provide it to Robinhood when creating your API key
4. Robinhood will give you an API_KEY that matches your public key

Usage:
    python generate_keypair.py
"""

import nacl.signing
import base64

def main():
    print("=" * 60)
    print("Ed25519 Keypair Generator for Robinhood API")
    print("=" * 60)
    print()
    print("📝 How to use this keypair:")
    print("   1. Copy the PRIVATE KEY below to your .env file as BASE64_PRIVATE_KEY")
    print("   2. Copy the PUBLIC KEY below and provide it to Robinhood when creating your API key")
    print("   3. Robinhood will give you an API_KEY that matches this public key")
    print()
    
    # Generate an Ed25519 keypair
    private_key = nacl.signing.SigningKey.generate()
    public_key = private_key.verify_key
    
    # Convert keys to base64 strings
    private_key_base64 = base64.b64encode(private_key.encode()).decode()
    public_key_base64 = base64.b64encode(public_key.encode()).decode()
    
    # Print the keys in base64 format
    print("=" * 60)
    print("PRIVATE KEY (Base64) - Add this to your .env file:")
    print("=" * 60)
    print(f"BASE64_PRIVATE_KEY={private_key_base64}\n")
    
    print("=" * 60)
    print("PUBLIC KEY (Base64) - Provide this to Robinhood:")
    print("=" * 60)
    print(f"{public_key_base64}\n")
    
    print("=" * 60)
    print("📋 Next Steps:")
    print("   1. Add BASE64_PRIVATE_KEY to your .env file")
    print("   2. Go to Robinhood Developer Portal")
    print("   3. Create a new API key and paste the PUBLIC KEY above")
    print("   4. Robinhood will give you an API_KEY - add it to .env as API_KEY")
    print("=" * 60)

if __name__ == "__main__":
    main()
