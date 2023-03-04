from django.shortcuts import render
from firebaseDb.firebaseDb import FirebaseDb
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from datetime import date as datet

# Create your views here.

db = FirebaseDb().db

@api_view(["GET", "POST", "PUT"])
def adminBaseView(request):

    if request.method == "GET":
      translate=[]
      data = db.child('bases').get()
      if data.val() is not None:
         for i in data.each():
            val= i.val()
            key= {'serial':i.key(), 'label':val['base']}
            newData = {**key, **val}
            translate.append(newData)
      return Response(translate)

    if request.method == "POST":
       base = request.data['base']
       now = datet.today()
       today = (f'{now.day}-{now.month}-{now.year}')
       all = db.child('bases').get()
       if all.val() is not None:
         for i in all.each():
            if i.val()['base'] == base:
               raise AuthenticationFailed('Base ya creada')
       data = {'base':base, 'date':today,'active':True}
       db.child('bases').push(data)
       return Response(data)
    
    if request.method == "PUT":
       serial = request.data['serial']
       base = request.data['base']
       date = request.data['date']
       active = request.data['active']
       data = {'base':base, 'date':date, 'active':active}
       db.child('bases').child(serial).set(data)
       return Response(data)


