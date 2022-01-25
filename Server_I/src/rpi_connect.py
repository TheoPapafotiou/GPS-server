import os
import paramiko

class RPIConnect():

    def __init__(self, IP1, IP2, IP3):

        self.ssh1 = paramiko.SSHClient()
        self.ssh1.connect(IP1, username="pi", password="p@ssw0rd")

        self.ssh2 = paramiko.SSHClient()
        self.ssh2.connect(IP2, username="pi", password="p@ssw0rd")

        self.ssh3 = paramiko.SSHClient()
        self.ssh3.connect(IP3, username="pi", password="p@ssw0rd")
    
    def go_directory(self):

        ssh_stdin1, ssh_stdout1, ssh_stderr1 = self.ssh1.exec_command("cd ~/Desktop/VROOM_GPS-server/ServerI/")
        ssh_stdin2, ssh_stdout2, ssh_stderr2 = self.ssh2.exec_command("cd ~/Desktop/VROOM_GPS-server/ServerI/")
        ssh_stdin3, ssh_stdout3, ssh_stderr3 = self.ssh3.exec_command("cd ~/Desktop/VROOM_GPS-server/ServerI/")

    def run_gps(self):

        ssh_stdin1, ssh_stdout1, ssh_stderr1 = self.ssh1.exec_command("python3 rpi_gps.py")
        ssh_stdin2, ssh_stdout2, ssh_stderr2 = self.ssh2.exec_command("python3 rpi_gps.py")
        ssh_stdin3, ssh_stdout3, ssh_stderr3 = self.ssh3.exec_command("python3 rpi_gps.py")

    def stop_run(self):
        
        ssh_stdin1, ssh_stdout1, ssh_stderr1 = self.ssh1.exec_command("kill SIGINT <PID>")
        ssh_stdin2, ssh_stdout2, ssh_stderr2 = self.ssh2.exec_command("python3 rpi_gps.py")
        ssh_stdin3, ssh_stdout3, ssh_stderr3 = self.ssh3.exec_command("python3 rpi_gps.py")