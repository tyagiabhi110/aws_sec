import scapy.all as scapy

def scan(ip):
        arp_request = scapy.ARP(pdst=ip)
        # arp_request.show()
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        # broadcast.show()
        arp_request_broadcast = broadcast/arp_request
        # arp_request_broadcast.show()
        answered_list = scapy.srp(arp_request_broadcast, verbose=False,timeout=1)[0]


        print("IP\t\t\t\tMAC Address")
        clients_list = []
        for element in answered_list:
                client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
                clients_list.append(client_dict)
                # print(element[1].psrc + "\t\t" + element[1].hwsrc)
                # print(element[1].hwsrc)
        return clients_list
def print_result(results_list):
        print("IP\t\t\tMAC Address\n------------------------------------------")
        for client in results_list:
                print(client["ip"] + "\t\t" + client["mac"])
scan_result = scan("10.0.2.1/24")
print_result(scan_result)
