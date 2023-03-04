from django.shortcuts import render
from firebaseDb.firebaseDb import FirebaseDb
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
import datetime, jwt


# Create your views here.

db = FirebaseDb().db

@api_view(["POST"])
def newPasswordView(request):
    if request.method == "POST":
      serial = request.data['serial']
      password = request.data['password']
      password2 = request.data['password2']
      if password != password2:
         raise AuthenticationFailed('Contraseñas no coinciden')
      serialDb =db.child('users').child(serial).child('password').get()
      cedula = db.child('users').child(serial).child('cedula').get()
      if (serialDb.val()) != cedula.val():
         raise AuthenticationFailed('Primero debe solicitar reinicio de contraseña')
      if password == cedula.val():
         raise AuthenticationFailed('Debe ingresar una contraseña diferente')
      db.child('users').child(serial).child('password').set(password)
      return Response({'message':'positive'})


@api_view(["POST"])
def resetPasswordView(request):

   if request.method == "POST":
      serial = request.data['serial']
      password = request.data['password']
      password2 = request.data['password2']
      if password != password2:
         raise AuthenticationFailed('Contraseñas no coinciden')
      db.child('users').child(serial).child('password').set(password)
      return Response({'message':'positive'})


@api_view(["GET", "POST", "PUT"])
def adminUserView(request):
    
    if request.method == "GET":
      data = db.child('users').get()
      translate = []
      for i in data.each():
        i.val().pop('password')
        val= i.val()
        key= {'serial':i.key()}
        newData = {**key, **val}
        if i.val()['superadmin'] == False:
         translate.append(newData)
      
      # data ={'d':'d'}
      return Response(translate)

    if request.method == "POST":
       user = request.data['user']
       password = request.data['cedula']
       place = request.data['place']
       cedula = request.data['cedula']
       nombre = request.data['nombre']
       apellido = request.data['apellido']
       all = db.child('users').get()
       for i in all.each():
          if i.val()['user'] == user:
            raise AuthenticationFailed('Usuario ya asignado')
       data = {
          'user':user, 
          'password':password, 
          'place':place, 
          'active':True, 
          'superadmin':False,
          'cedula': cedula,
          'nombre': nombre,
          'apellido': apellido,
          }
       db.child('users').push(data)
       return Response(data)
    
    if request.method == "PUT":
       serial = request.data['serial']
       place = request.data['place']
       active = request.data['active']
       db.child('users').child(serial).child('place').set(place)
       db.child('users').child(serial).child('active').set(active)
       return Response({'message':'positive'})


@api_view(["POST", "PUT"])
def loginView(request):
   
   if request.method == "POST":
      
      user = request.data['user']
      print(user)
      password = request.data['password']
      print(password)
      all = db.child('users').get()
      coincide = False
      for i in all.each():
          if i.val()['user'] == user and i.val()['password' ] == password and i.val()['active'] == True:
            coincide = True
            break

      if coincide:
         payload = {
            'id' : i.key(),
            'adm': i.val()['superadmin'],
            'cedula': i.val()['cedula'],
            'nombre': i.val()['nombre'],
            'apellido': i.val()['apellido'],
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours= 12),
            'iat' : datetime.datetime.utcnow()
         }
         token = jwt.encode(payload, 'secret', algorithm='HS256')
         response = Response()
         response.set_cookie(key='jwt', value=token, httponly=True)
         response.data = {
            'jwt':token,
            'cc': i.val()['cedula'] 
            # 'admin':i.val()['superadmin']
            }
         return response
         
      else:
         raise AuthenticationFailed('Clave o usuario incorrecto')
          
@api_view(["POST"])
def userView(request):

   if request.method == "POST":
      token = request.data['jwt']
      if not token:
         raise AuthenticationFailed('Debes estar logueado')
      try:
         payload = jwt.decode(token, 'secret', algorithms='HS256')
         
      except jwt.ExpiredSignatureError:
         raise AuthenticationFailed('Debes estar logueado')
      return Response({'jwt':payload})   

@api_view(["POST"])
def logoutView(request):
   
   if request.method == "POST":
      
      response = Response()
      response.delete_cookie('jwt')
      response.data = {'message': 'success'}
      return response