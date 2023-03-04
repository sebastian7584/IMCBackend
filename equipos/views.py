from django.shortcuts import render
from firebaseDb.firebaseDb import FirebaseDb
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from datetime import date as datet

# Create your views here.

db = FirebaseDb().db

@api_view(["GET", "POST", "PUT"])
def adminEquipoView(request):

    if request.method == "GET":
      translate=[]
      data = db.child('equipos').get()
      if data.val() is not None:
         for i in data.each():
            val= i.val()
            key= {'serial':i.key(), 'label':val['equipo']}
            newData = {**key, **val}
            translate.append(newData)
      return Response(translate)

    if request.method == "POST":
       equipo = request.data['equipo']
       now = datet.today()
       today = (f'{now.day}-{now.month}-{now.year}')
       all = db.child('equipos').get()
       if all.val() is not None:
         for i in all.each():
            if i.val()['equipo'] == equipo:
               raise AuthenticationFailed('Equipo ya creado')
       data = {'equipo':equipo, 'date':today, 'state':'nuevo', 'active':True}
       db.child('equipos').push(data)
       return Response(data)
    
    if request.method == "PUT":
       serial = request.data['serial']
       equipo = request.data['equipo']
       date = request.data['date']
       state = request.data['state']
       active = request.data['active']
       data = {'equipo':equipo, 'date':date, 'state':state, 'active':active}
       db.child('equipos').child(serial).set(data)
       return Response(data)


