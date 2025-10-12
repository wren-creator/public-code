import socket
import threading
import subprocess
import sys
import os

# Functions

def netstat_route():
    """Executes netstat and route commands to display network configuration."""
    print("\n--- Netstat & Route (Static Output) ---")
    try:
        if os.name == 'nt':  # Windows
            # 'route print' for routing table, 'netstat -an' for connections
            subprocess.run("route print", shell=True, check=True)
            subprocess.run("netstat -an", shell=True, check=True)
        else:  # Linux/macOS/Unix-like
            # netstat -rn for routing table, netstat -an for connections
            # Security Note: shell=False is preferred, but for combined commands like 'netstat -rn; netstat -an'
            # and compatibility with various systems, we'll stick with a simple structure here.
            # Using simple 'subprocess.call' for quick execution as in the original.
            print("\nRouting Table (netstat -rn):")
            subprocess.call(["netstat", "-rn"])
            print("\nAll Connections (netstat -an):")
            subprocess.call(["netstat", "-an"])

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    except FileNotFoundError:
        print("Error: 'netstat' or 'route' command not found. Ensure they are in your PATH.")


def tcpdump_like():
    """A basic raw socket packet sniffer (requires elevated privileges)."""
    import struct

    # Check for correct OS and elevated privileges
    if sys.platform != 'linux':
        print("Packet capture using raw sockets (AF_PACKET) is typically only available on Linux.")
        return

    print("\n--- Real Packet Capture (Press Ctrl+C to stop) ---")

    try:
        # socket.ntohs(3) is ETH_P_ALL for all protocols
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    except PermissionError:
        print("Permission denied: Run this script with elevated privileges (e.g., sudo).")
        return
    except OSError as e:
        print(f"Error creating socket: {e}. Check OS/interface permissions.")
        return

    try:
        while True:
            raw_data, _ = s.recvfrom(65536)

            # --- Ethernet Frame Parsing ---
            if len(raw_data) < 14: continue # Too short for Ethernet header
            # !6s6sH: 6 bytes dest MAC, 6 bytes src MAC, 2 bytes EtherType
            _, _, proto_type = struct.unpack('!6s6sH', raw_data[:14])
            proto_type = socket.htons(proto_type) # Convert to host byte order

            if proto_type == 0x0800:  # IPv4 (8)
                # --- IP Packet Parsing ---
                ip_header = raw_data[14:34] # Assuming no IP options (standard 20-byte header)
                if len(ip_header) < 20: continue
                # !BBHHHBBH4s4s: Version/IHL, ToS, Total Length, ID, Flags/Fragment Offset, TTL, Protocol, Checksum, Src IP, Dest IP
                iph = struct.unpack('!BBHHHBBH4s4s', ip_header)

                # IHL is in the first byte (Version/IHL); & 0xF gets the IHL (lower 4 bits)
                ip_header_length = (iph[0] & 0xF) * 4
                if ip_header_length != 20: # Skip non-standard IP header lengths
                    continue

                protocol = iph[6]
                src_ip = socket.inet_ntoa(iph[8])
                dest_ip = socket.inet_ntoa(iph[9])

                # Optional: Add TCP/UDP info here based on 'protocol' variable

                print(f"Packet: {src_ip} -> {dest_ip} | Protocol ID: {protocol}")

            # Optional: elif proto_type == 0x0806: ARP

    except KeyboardInterrupt:
        print("\nCapture stopped.")
    finally:
        s.close() # Ensure socket is closed


def netcat_server(ip, port):
    """Starts a simple single-connection TCP server."""
    print(f"\n--- Netcat-like Server on {ip}:{port} (Running in thread) ---")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows reuse of the address
            s.bind((ip, port))
            s.listen(1)
            print("Server listening...")

            # Use 'with' for the connection socket as well
            conn, addr = s.accept()
            with conn:
                print(f"Connection established from {addr[0]}:{addr[1]}")
                data = conn.recv(1024)
                print(f"Received: {data.decode('utf-8', errors='ignore')}")

                response = b'Hello from server'
                conn.sendall(response)
                print(f"Sent: {response.decode('utf-8')}")

    except OSError as e:
        print(f"Server Error (Port {port}): {e}. Is the port in use or IP incorrect?")
    except Exception as e:
        print(f"An unexpected server error occurred: {e}")


def netcat_client(ip, port):
    """Connects to a TCP server, sends data, and prints response."""
    print(f"\n--- Netcat-like Client to {ip}:{port} (Running in thread) ---")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5) # Set a timeout for connection/recv
            s.connect((ip, port))

            message = b'Ping from client'
            s.sendall(message)
            print(f"Sent: {message.decode('utf-8')}")

            data = s.recv(1024)
            print(f"Received: {data.decode('utf-8', errors='ignore')}")

    except ConnectionRefusedError:
        print(f"Client Error: Connection refused by {ip}:{port}. Is the server running?")
    except socket.timeout:
        print(f"Client Error: Connection or data transfer timed out after 5 seconds.")
    except OSError as e:
        print(f"Client Error: {e}. Check IP/Port validity.")
    except Exception as e:
        print(f"An unexpected client error occurred: {e}")


def mini_webserver(ip, port):
    """Starts a basic HTTP server with a simple 'Hello World' page."""
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class HelloHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # A more robust and modern way to send HTML
            response_html = f"""
            <html>
                <head><title>Python Mini Server</title></head>
                <body>
                    <h1>Hello World from Python Web Server!</h1>
                    <p>Served from {self.server.server_address[0]}:{self.server.server_address[1]}</p>
                </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response_html.encode('utf-8'))

        def log_message(self, format, *args):
            # Suppress default log messages to keep the terminal cleaner
            pass

    print(f"\n--- Starting Web Server on http://{ip}:{port} (Press Ctrl+C in thread to stop) ---")

    try:
        server = HTTPServer((ip, port), HelloHandler)
        # To stop the server gracefully, you'd need an additional method/thread control,
        # but for this simple toolkit, we'll keep it running until the main program exits.
        print("Web server running...")
        server.serve_forever()
    except OSError as e:
        print(f"Web Server Error (Port {port}): {e}. Is the port in use or IP incorrect?")
    except KeyboardInterrupt:
        # This only catches if Ctrl+C is pressed directly in the server thread (not common with this menu structure)
        server.shutdown()
        print("Web server stopped.")
    except Exception as e:
        print(f"An unexpected web server error occurred: {e}")


# Menu and Execution

def get_network_input():
    """Prompts for and validates IP and Port input."""
    ip = input("Enter IP address to use (e.g., 127.0.0.1): ").strip()
    try:
        # Basic check if it's a valid IPv4 address structure
        socket.inet_aton(ip)
    except socket.error:
        print("Invalid IP address format.")
        return None, None

    try:
        port = int(input("Enter port number to use (e.g., 9999): ").strip())
        if not 1 <= port <= 65535:
            print("Port must be between 1 and 65535.")
            return None, None
    except ValueError:
        print("Invalid port number.")
        return None, None

    return ip, port


def menu():
    """Main menu loop for the network toolkit."""
    while True:
        print("\n" + "="*30)
        print("--- Python Network Toolkit Menu ---")
        print("="*30)
        print("1: Show Netstat & Route Info (System Command)")
        print("2: Packet Capture (Raw Socket - Requires sudo/root on Linux)")
        print("3: Start Netcat-like Server (TCP)")
        print("4: Run Netcat-like Client (TCP)")
        print("5: Start Mini Web Server (HTTP)")
        print("q: Quit")
        choice = input("Select an option: ").strip().lower()

        if choice == 'q':
            print("Exiting Network Toolkit. Goodbye!")
            break

        # Options that require IP and Port input
        if choice in ['3', '4', '5']:
            ip, port = get_network_input()
            if ip and port:
                if choice == '3':
                    # Server functions run in a thread to keep the menu active
                    threading.Thread(target=netcat_server, args=(ip, port), daemon=True).start()
                elif choice == '4':
                    # Client functions run in a thread to prevent blocking the menu
                    threading.Thread(target=netcat_client, args=(ip, port), daemon=True).start()
                elif choice == '5':
                    # Web server runs in a thread
                    threading.Thread(target=mini_webserver, args=(ip, port), daemon=True).start()

        elif choice == '1':
            # Run netstat/route in a thread
            threading.Thread(target=netstat_route, daemon=True).start()

        elif choice == '2':
            # Packet capture in a thread
            threading.Thread(target=tcpdump_like, daemon=True).start()

        else:
            print("❌ Invalid choice. Please select an option from the menu.")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting.")
        sys.exit(0)
