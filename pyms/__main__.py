''' Allows pyms to run as a module '''

if __name__ == '__main__':
    print('Running pyms as module')
    from . import gui
    gui.run()
