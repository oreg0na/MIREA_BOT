import paramiko

user_states = {}

def ssh_connect(host, port, username, password):
    global ssh_client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=host, port=int(port), username=username, password=password)
        return True, "Connected successfully to {}".format(host)
    except Exception as e:
        return False, "Failed to connect: {}".format(str(e))

def ssh_close(user_id):
    global ssh_client
    if ssh_client:
        ssh_client.close()
        ssh_client = None
        set_user_state(user_id, None)
        return "Connection closed"
    return "No active connection"

def ssh_cmd(command):
    global ssh_client
    if ssh_client:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        return stdout.read().decode() + stderr.read().decode()
    return "No active connection"

def get_user_state(user_id):
    return user_states.get(user_id, None)

def set_user_state(user_id, state):
    user_states[user_id] = state