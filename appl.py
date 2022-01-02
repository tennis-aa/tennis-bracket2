import app

appl = app.create_app()
appl.debug = True
if __name__=='__main__':
    appl.run()