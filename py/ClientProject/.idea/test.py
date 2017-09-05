import sys, os, time, socket, subprocess, xmlrpc.client

if __name__=='__main__':
    sp = []
    for i in range(0, 15):
        #cmd = r'cmd /k python %s\client.py' % (os.path.split(os.path.realpath(__file__))[0])
        cmd = r'python %s\client.py' % (os.path.split(os.path.realpath(__file__))[0])
        sp.append(subprocess.Popen(cmd,creationflags =subprocess.CREATE_NEW_CONSOLE))
    while (input("输入shutdown停止!\n:").lower().strip()!="shutdown"):
        time.sleep(5)
    for s in sp:
        s.terminate()
        s.wait(2)