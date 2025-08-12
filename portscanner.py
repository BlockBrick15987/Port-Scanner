import socket
import threading
import dearpygui.dearpygui as dpg

open_ports = []
closed_ports = []


# ---------------- Port Scanner ---------------- #
class PortScanner:
    def __init__(self, ip, start_port, end_port):
        self.ip = ip
        self.start_port = start_port
        self.end_port = end_port

    def scan_single(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, port))
            open_ports.append(port)
        except:
            closed_ports.append(port)
        finally:
            sock.close()

    def scan_range(self, ip, start_port, end_port):
        threads = []
        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=self.scan_single, args=(ip, port))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()


# ---------------- GUI Functions ---------------- #
def log_message(msg):
    """Writes a message to the log console."""
    dpg.add_text(msg, parent="log_window")


def clear_results():
    """Remove only table rows, not the header."""
    children = dpg.get_item_children("results_table", 1)  # 1 = slots for rows
    if children:
        for child in children:
            dpg.delete_item(child)


def start_scan():
    open_ports.clear()
    closed_ports.clear()
    clear_results()

    ip = dpg.get_value("ip_input")
    mode = dpg.get_value("mode_radio")

    log_message(f"Starting scan on {ip} in mode '{mode}'...")

    if mode == "Single Port":
        port = int(dpg.get_value("port_input"))
        scanner = PortScanner(ip, port, port)
        scanner.scan_single(ip, port)
    elif mode == "Range":
        start_port = int(dpg.get_value("start_port_input"))
        end_port = int(dpg.get_value("end_port_input"))
        scanner = PortScanner(ip, start_port, end_port)
        scanner.scan_range(ip, start_port, end_port)
    else:
        log_message("❌ Invalid mode")
        return

    # Sort results
    open_ports.sort()
    closed_ports.sort()

    # Add results
    for port in open_ports:
        with dpg.table_row(parent="results_table"):
            dpg.add_text(str(port))
            dpg.add_text("Open")

    for port in closed_ports:
        with dpg.table_row(parent="results_table"):
            dpg.add_text(str(port))
            dpg.add_text("Closed")

    log_message("✅ Scan finished.")


# ---------------- GUI Layout ---------------- #
dpg.create_context()

with dpg.window(label="Port Scanner", width=900, height=600):
    # Input section
    dpg.add_text("IP Address:")
    dpg.add_input_text(tag="ip_input", default_value="127.0.0.1")

    dpg.add_text("Mode:")
    dpg.add_radio_button(items=["Single Port", "Range"], tag="mode_radio", default_value="Single Port")

    dpg.add_text("Single Port:")
    dpg.add_input_int(tag="port_input", default_value=80)

    dpg.add_text("Start Port:")
    dpg.add_input_int(tag="start_port_input", default_value=20)

    dpg.add_text("End Port:")
    dpg.add_input_int(tag="end_port_input", default_value=25)

    dpg.add_button(label="Start Scan", callback=start_scan)
    dpg.add_separator()

    # Results in a bigger child window
    dpg.add_text("Scan Results:")
    with dpg.child_window(width=-1, height=350, border=True):
        with dpg.table(tag="results_table", header_row=True,
                       resizable=True, borders_innerH=True, borders_outerH=True,
                       borders_innerV=True, borders_outerV=True):
            dpg.add_table_column(label="Port")
            dpg.add_table_column(label="Status")

    dpg.add_separator()

    # Log console
    dpg.add_text("Log:")
    with dpg.child_window(tag="log_window", autosize_x=True, height=120, border=True):
        pass

dpg.create_viewport(title="Port Scanner", width=920, height=640)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
