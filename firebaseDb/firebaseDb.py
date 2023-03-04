import pyrebase

class FirebaseDb:

    def __init__(self):

        firebaseConfig = {
        "apiKey": "ZIwd24yiayxRP0fx6hsPB9CtiOImhsVorWcupXsm",
        "authDomain": "imcseguridad-3155e-default-rtdb.firebaseapp.com",
        "databaseURL": "https://imcseguridad-3155e-default-rtdb.firebaseio.com",
        "storageBucket": "imcseguridad-3155e-default-rtdb.appspot.com"
        }
        firebase = pyrebase.initialize_app(firebaseConfig)
        self.db = firebase.database()
       
    
   

