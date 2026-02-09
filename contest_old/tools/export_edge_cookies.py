#!/usr/bin/env python3
"""
export_edge_cookies.py

Extract cookies for atcoder.jp from Microsoft Edge (Chromium) cookie DB,
decrypt Windows DPAPI-encrypted values and write a Netscape-format cookie.jar
for online-judge-tools.

Usage:
  python tools\export_edge_cookies.py

This script writes to: %LOCALAPPDATA%\online-judge-tools\online-judge-tools\cookie.jar
"""
import os
import sqlite3
import shutil
import sys
import time
import tempfile
import ctypes
from ctypes import wintypes


def dpapi_decrypt(encrypted_bytes: bytes) -> bytes:
    # If Chrome/Edge stores value with "v10" prefix, strip it
    if encrypted_bytes.startswith(b"v10"):
        encrypted_bytes = encrypted_bytes[3:]

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    pDataIn = DATA_BLOB()
    pDataIn.cbData = len(encrypted_bytes)
    pDataIn.pbData = ctypes.cast(ctypes.create_string_buffer(encrypted_bytes, len(encrypted_bytes)), ctypes.POINTER(ctypes.c_char))

    pDataOut = DATA_BLOB()
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    if crypt32.CryptUnprotectData(ctypes.byref(pDataIn), None, None, None, None, 0, ctypes.byref(pDataOut)) == 0:
        raise ctypes.WinError()

    # copy decrypted bytes
    buffer = ctypes.cast(pDataOut.pbData, ctypes.POINTER(ctypes.c_ubyte * pDataOut.cbData)).contents
    out = bytes(bytearray(buffer[:pDataOut.cbData]))

    # Free memory allocated for pDataOut
    kernel32.LocalFree(pDataOut.pbData)
    return out


def chrome_time_to_epoch(expires_utc: int) -> int:
    # Chrome/Edge stores time in microseconds since 1601-01-01
    if expires_utc == 0:
        return int(time.time()) + 31536000
    return int(expires_utc / 1000000 - 11644473600)


def export_atcoder_cookies():
    local_app = os.getenv('LOCALAPPDATA')
    if not local_app:
        print('LOCALAPPDATA not set', file=sys.stderr)
        return 1

    cookie_db = os.path.join(local_app, 'Microsoft', 'Edge', 'User Data', 'Default', 'Network', 'Cookies')
    if not os.path.exists(cookie_db):
        print('Edge cookie DB not found at', cookie_db, file=sys.stderr)
        return 1

    tmpdir = tempfile.mkdtemp()
    try:
        tmp_db = os.path.join(tmpdir, 'Cookies')
        shutil.copy2(cookie_db, tmp_db)

        conn = sqlite3.connect(tmp_db)
        cur = conn.cursor()
        # host_key may be like .atcoder.jp or atcoder.jp
        cur.execute("SELECT host_key, name, path, is_secure, expires_utc, encrypted_value FROM cookies WHERE host_key LIKE '%atcoder.jp%'")
        rows = cur.fetchall()
    finally:
        # we'll clean later
        pass

    if not rows:
        print('No atcoder.jp cookies found in Edge profile.', file=sys.stderr)
        shutil.rmtree(tmpdir)
        return 1

    out_lines = ["# Netscape HTTP Cookie File"]
    for host_key, name, path, is_secure, expires_utc, encrypted_value in rows:
        try:
            decrypted = dpapi_decrypt(encrypted_value)
            value = decrypted.decode('utf-8', errors='ignore')
        except Exception as e:
            print('Failed to decrypt cookie', name, 'skipping:', e, file=sys.stderr)
            continue

        # Build Netscape line: domain	flag	path	secure	expiration	name	value
        domain = host_key
        flag = 'TRUE' if domain.startswith('.') else 'FALSE'
        secure = 'TRUE' if is_secure else 'FALSE'
        expiry = chrome_time_to_epoch(expires_utc if expires_utc else 0)
        line = f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}"
        out_lines.append(line)

    # write to online-judge-tools cookie location
    oj_dir = os.path.join(local_app, 'online-judge-tools', 'online-judge-tools')
    os.makedirs(oj_dir, exist_ok=True)
    cookie_path = os.path.join(oj_dir, 'cookie.jar')
    with open(cookie_path, 'w', encoding='ascii', errors='ignore') as f:
        f.write('\n'.join(out_lines))

    print('Wrote cookie.jar to', cookie_path)
    shutil.rmtree(tmpdir)
    return 0


if __name__ == '__main__':
    sys.exit(export_atcoder_cookies())
