import os
import subprocess

class Proxy:
    """

    Class Proxy:

    This class represents a proxy that can be used for intercepting and manipulating network traffic.

    Attributes:
    - filename (str): The name of the dump file to store intercepted network traffic. Default value is 'dump.har'.
    - port (int): The port number on which the proxy will be running. Default value is 8080.

    Methods:
    - __init__(filename: str = 'dump.har', port: int = 8080): Initializes the Proxy object and starts the mitmdump process.
        Parameters:
            - filename (str): The name of the dump file to store intercepted network traffic. Default value is 'dump.har'.
            - port (int): The port number on which the proxy will be running. Default value is 8080.
    - stop(): Stops the running proxy by terminating the mitmdump process.

    Example usage:
    proxy = Proxy()
    do_stuff()
    proxy.stop()

    """
    def __init__(self, filename : str = 'dump.har', port : int = 8080):
        cmd = f"mitmdump  --set hardump={filename} -p {port}"
        self.process = subprocess.Popen(cmd, shell=True)

    def stop(self):
        self.process.terminate()

