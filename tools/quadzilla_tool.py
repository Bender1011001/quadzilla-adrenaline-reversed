#!/usr/bin/env python3
"""
Quadzilla Adrenaline X2com Serial Communication Tool
=====================================================
Communicates with the Quadzilla Adrenaline tuner via USB CDC ACM serial port.
Implements the X2com protocol reversed from Quadzilla.dll and X2Updater.exe.

Protocol: 921600 baud, 8N1, no handshake
USB: VID 0x1A18, PID 0x0002

Opcodes:
  0x00 - LINK_CHECK     → response 0x01
  0x02 - DISCONNECT
  0x03 - BOOTLOAD_MODE  (mode)
  0x04 - MODULE_INFO    → 25 bytes
  0x06 - KEY_TRANSFER   (key×8)
  0x07 - DATA_TRANSFER  (len, data×61)
  0x0B - XFER_COMPLETE
  0x0D - SN_PROGRAM     (SN×8)
  0x0E - FEATURE_CODE   (op, code×8)
  0x10 - ABORT
  0x11 - FEATURE_READ   → (count, data)
"""
import serial
import serial.tools.list_ports
import struct
import time
import json
import argparse
import sys

# Protocol constants
BAUD_RATE = 921600
USB_VID = 0x1A18
USB_PID = 0x0002

# Opcodes
OP_LINK_CHECK    = 0x00
OP_LINK_REPLY    = 0x01
OP_DISCONNECT    = 0x02
OP_BOOTLOAD_MODE = 0x03
OP_MODULE_INFO   = 0x04
OP_KEY_TRANSFER  = 0x06
OP_DATA_TRANSFER = 0x07
OP_XFER_COMPLETE = 0x0B
OP_SN_PROGRAM    = 0x0D
OP_FEATURE_CODE  = 0x0E
OP_ABORT         = 0x10
OP_FEATURE_READ  = 0x11


class QuadzillaConnection:
    """Serial connection to a Quadzilla Adrenaline tuner."""
    
    def __init__(self, port=None, timeout=5.0):
        self.port = port
        self.timeout = timeout
        self.serial = None
        self.connected = False
    
    @staticmethod
    def find_device():
        """Auto-detect Quadzilla USB device by VID:PID."""
        for port in serial.tools.list_ports.comports():
            if port.vid == USB_VID and port.pid == USB_PID:
                return port.device
            # Also check description for Quadzilla-related strings
            desc = (port.description or '').lower()
            if 'quadzilla' in desc or 'adrenaline' in desc:
                return port.device
        return None
    
    @staticmethod
    def list_ports():
        """List all available serial ports."""
        ports = serial.tools.list_ports.comports()
        results = []
        for p in ports:
            info = {
                'device': p.device,
                'description': p.description,
                'vid': hex(p.vid) if p.vid else None,
                'pid': hex(p.pid) if p.pid else None,
                'serial': p.serial_number,
            }
            results.append(info)
        return results
    
    def connect(self, port=None):
        """Open serial connection to the tuner."""
        if port:
            self.port = port
        
        if not self.port:
            self.port = self.find_device()
            if not self.port:
                raise ConnectionError(
                    "No Quadzilla device found. Available ports:\n" +
                    "\n".join(f"  {p['device']}: {p['description']} (VID={p['vid']}, PID={p['pid']})" 
                              for p in self.list_ports())
                )
        
        self.serial = serial.Serial(
            port=self.port,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
            timeout=self.timeout,
            write_timeout=self.timeout,
        )
        
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.connected = True
        print(f"[+] Connected to {self.port} at {BAUD_RATE} baud")
        return True
    
    def disconnect(self):
        """Send disconnect command and close port."""
        if self.serial and self.serial.is_open:
            try:
                self.send_raw(bytes([OP_DISCONNECT]))
            except Exception:
                pass
            self.serial.close()
        self.connected = False
        print("[+] Disconnected")
    
    def send_raw(self, data):
        """Send raw bytes."""
        self.serial.write(data)
        self.serial.flush()
    
    def recv_raw(self, count, timeout=None):
        """Receive raw bytes."""
        old_timeout = self.serial.timeout
        if timeout:
            self.serial.timeout = timeout
        data = self.serial.read(count)
        self.serial.timeout = old_timeout
        return data
    
    def link_check(self):
        """Send link check and verify response."""
        self.send_raw(bytes([OP_LINK_CHECK]))
        resp = self.recv_raw(1, timeout=2.0)
        if resp and resp[0] == OP_LINK_REPLY:
            print("[+] Link check: OK")
            return True
        print(f"[-] Link check failed: got {resp.hex() if resp else 'no response'}")
        return False
    
    def get_module_info(self):
        """Read module information (25 bytes)."""
        self.send_raw(bytes([OP_MODULE_INFO]))
        resp = self.recv_raw(25, timeout=3.0)
        if not resp or len(resp) < 25:
            print(f"[-] Module info: insufficient data ({len(resp) if resp else 0} bytes)")
            return None
        
        info = {
            'raw': resp.hex(),
            'response_code': resp[0],
            'data': resp[1:].hex(),
            # Parse known fields from Quadzilla.dll decompilation
            'firmware_version': resp[1:5].hex(),
            'serial_number': resp[5:13].hex(),
            'device_id': resp[13:21].hex(),
            'hw_rev': resp[21:25].hex(),
        }
        
        print(f"[+] Module Info:")
        print(f"    Firmware: {info['firmware_version']}")
        print(f"    Serial:   {info['serial_number']}")
        print(f"    Device:   {info['device_id']}")
        print(f"    HW Rev:   {info['hw_rev']}")
        return info
    
    def read_feature_codes(self):
        """Read installed feature codes."""
        self.send_raw(bytes([OP_FEATURE_READ]))
        # Response: [0x11, count, data...]
        header = self.recv_raw(2, timeout=3.0)
        if not header or len(header) < 2:
            print("[-] Feature read: no response")
            return None
        
        if header[0] != OP_FEATURE_READ:
            print(f"[-] Feature read: unexpected response {header.hex()}")
            return None
        
        count = header[1]
        features = []
        if count > 0:
            data = self.recv_raw(count * 8, timeout=3.0)
            for i in range(count):
                code = data[i*8:(i+1)*8]
                features.append(code.hex())
        
        print(f"[+] Feature codes: {count} installed")
        for i, fc in enumerate(features):
            print(f"    [{i}] {fc}")
        return features
    
    def probe_aid(self, aid):
        """
        Attempt to read a single AID value using the X2com CWA (Command With Ack) pattern.
        This sends a request for the AID and waits for a response.
        
        Note: The exact packet format depends on the X2com JNI implementation.
        This is a best-effort probe based on the protocol analysis.
        """
        # The X2com protocol uses a request/response pattern
        # The exact format needs to be determined from libx2com-jni.so analysis
        # For now, we document what we know and provide the framework
        pass
    
    def scan_aids(self, start=0, end=255):
        """Scan AID range for responding parameters."""
        results = {}
        print(f"[*] Scanning AIDs {start}-{end}...")
        for aid in range(start, end + 1):
            resp = self.probe_aid(aid)
            if resp is not None:
                results[aid] = resp
                print(f"  AID {aid:3d}: {resp}")
        print(f"[+] Found {len(results)} responding AIDs")
        return results


def cmd_info(args):
    """Get module info."""
    conn = QuadzillaConnection(port=args.port)
    conn.connect()
    try:
        if conn.link_check():
            conn.get_module_info()
    finally:
        conn.disconnect()


def cmd_features(args):
    """Read feature codes."""
    conn = QuadzillaConnection(port=args.port)
    conn.connect()
    try:
        if conn.link_check():
            conn.read_feature_codes()
    finally:
        conn.disconnect()


def cmd_ports(args):
    """List available serial ports."""
    ports = QuadzillaConnection.list_ports()
    if not ports:
        print("No serial ports found")
        return
    
    print("Available serial ports:")
    for p in ports:
        marker = " <-- QUADZILLA?" if p['vid'] and int(p['vid'], 16) == USB_VID else ""
        print(f"  {p['device']:8s} {p['description']:40s} VID={p['vid']} PID={p['pid']}{marker}")


def cmd_scan(args):
    """Scan for responding AIDs."""
    conn = QuadzillaConnection(port=args.port)
    conn.connect()
    try:
        if conn.link_check():
            conn.scan_aids(args.start, args.end)
    finally:
        conn.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description='Quadzilla Adrenaline X2com Communication Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ports                    # List serial ports
  %(prog)s info                     # Get module info
  %(prog)s features                 # Read feature codes
  %(prog)s scan --start 0 --end 255 # Scan all AIDs
        """
    )
    parser.add_argument('-p', '--port', help='Serial port (auto-detect if not specified)')
    
    sub = parser.add_subparsers(dest='command', help='Command to run')
    
    sub.add_parser('ports', help='List available serial ports')
    sub.add_parser('info', help='Get module information')
    sub.add_parser('features', help='Read installed feature codes')
    
    scan_parser = sub.add_parser('scan', help='Scan AID range')
    scan_parser.add_argument('--start', type=int, default=0, help='Start AID (default: 0)')
    scan_parser.add_argument('--end', type=int, default=255, help='End AID (default: 255)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        'ports': cmd_ports,
        'info': cmd_info,
        'features': cmd_features,
        'scan': cmd_scan,
    }
    
    try:
        commands[args.command](args)
    except ConnectionError as e:
        print(f"[-] Connection error: {e}")
        sys.exit(1)
    except serial.SerialException as e:
        print(f"[-] Serial error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[!] Interrupted")
        sys.exit(0)


if __name__ == '__main__':
    main()
