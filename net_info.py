import ipaddress

def get_network_info(ip_str):
    """
    Calculates and displays network information for a given IP address and subnet.

    Args:
        ip_str (str): The IP address and subnet in CIDR notation (e.g., '192.168.1.50/24')
                      or with a netmask (e.g., '192.168.1.50/255.255.255.0').
    """
    try:
        # Create an IPv4Interface object. This handles both CIDR and netmask notation.
        # The 'strict=False' argument is necessary to create a network object from a host address.
        net = ipaddress.ip_network(ip_str, strict=False)
        ip_interface = ipaddress.ip_interface(ip_str)

        print("\n--- Network Information ---")
        print(f"IP Address: {ip_interface.ip}")
        print(f"Network Address: {net.network_address}")
        print(f"Broadcast Address: {net.broadcast_address}")
        print(f"Subnet Mask: {net.netmask}")
        print(f"Wildcard Mask: {net.hostmask}")
        print(f"CIDR Notation: /{net.prefixlen}")
        print(f"Total Hosts: {net.num_addresses}")
        # Usable hosts are total addresses minus the network and broadcast addresses.
        print(f"Usable Hosts: {net.num_addresses - 2 if net.prefixlen < 31 else 0}")
        print(f"Usable Host Range: {net.network_address + 1} - {net.broadcast_address - 1}")
        print(f"Is Private IP: {ip_interface.is_private}")
        print("--------------------------\n")

    except ValueError as e:
        print(f"\nError: Invalid IP address or subnet format. {e}")
        print("Please use formats like '192.168.1.100/24' or '192.168.1.100/255.255.255.0'.")

if __name__ == "__main__":
    # Get user input
    ip_input = input("Enter the IP address and subnet (e.g., 192.168.1.50/24): ")
    
    # Call the function with the user's input
    get_network_info(ip_input)
