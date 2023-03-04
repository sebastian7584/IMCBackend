from django.shortcuts import render
from firebaseDb.firebaseDb import FirebaseDb
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from datetime import date as datet

# Create your views here.

db = FirebaseDb().db

@api_view(["GET", "POST", "PUT"])
def adminAerolineaView(request):

    if request.method == "GET":
      translate=[]
      data = db.child('aerolineas').get()
      if data.val() is not None:
         for i in data.each():
            val= i.val()
            key= {'serial':i.key(), 'label':val['aerolinea']}
            newData = {**key, **val}
            translate.append(newData)
      return Response(translate)

    if request.method == "POST":
       aerolinea = request.data['aerolinea']
       now = datet.today()
       today = (f'{now.day}-{now.month}-{now.year}')
       all = db.child('aerolineas').get()
       if all.val() is not None:
         for i in all.each():
            if i.val()['aerolinea'] == aerolinea:
               raise AuthenticationFailed('Aerolinea ya creada')
       data = {'aerolinea':aerolinea, 'date':today,'active':True}
       db.child('aerolineas').push(data)
       return Response(data)
    
    if request.method == "PUT":
       serial = request.data['serial']
       aerolinea = request.data['aerolinea']
       date = request.data['date']
       active = request.data['active']
       data = {'aerolinea':aerolinea, 'date':date, 'active':active}
       db.child('aerolineas').child(serial).set(data)
       return Response(data)