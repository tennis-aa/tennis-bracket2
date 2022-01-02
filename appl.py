import app

appl = app.create_app()
appl.debug = False
if __name__=='__main__':
    appl.run()