from fabric.api import settings, abort, run, cd, sudo, put, env, prompt, get

def test_task():
    run("cd /")


def move_file():
    put("testfile", "~/testfile")
    

def install_puppet():
    sudo("apt-get install -y puppet")