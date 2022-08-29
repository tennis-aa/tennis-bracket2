import src

app = src.create_app()
app.debug = False
if __name__=='__main__':
    app.run()