from django.shortcuts import render
from firebaseDb.firebaseDb import FirebaseDb
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from datetime import datetime
import json

# Create your views here.

db = FirebaseDb().db

@api_view(["POST"])
def openFormView(request):

  if request.method == "POST":
    consecutivo = request.data['consecutivo']
    data= db.child('formularios').child(consecutivo).get()
    return Response(data.val())



@api_view(["GET", "POST", "PUT"])
def adminFormView(request):
    
    if request.method == "GET":
      translate = []
      data = db.child('formularios').get()
      if data.val() is not None:
        for i in data.each():
          if i.val() is None:
            continue
          # print(i.val())
          val = i.val()
          key= {'serial':i.key(), 'label':i.key()}
          print(val['metaData'])
          if val['metaData']['aerolinea']=="":
            aerolinea = ""
          else:
            aerolinea= val['metaData']['aerolinea']['aerolinea']
          if val['metaData']['base'] =="":
            base=""
          else:
            base= val['metaData']['base']['base']
          estado= val['paso']
          if estado ==0:
            estado="CREADO"
          elif estado ==1:
            estado="DESABORDADO"
          elif estado ==2:
            estado="PESADO"
          elif estado ==3:
            estado="ABORDADO"

          dataFormulario = {'aerolinea':aerolinea,'base':base,'estado':estado}
          newData = {**key, **dataFormulario}
          translate.append(newData)
      return Response(translate.reverse())

    if request.method == "POST":
       
       formulario = request.data['formulario']
       consecutivo = formulario['consecutivo']
       dataFormulario = formulario['data']
       paso = dataFormulario['paso']
       fecha= datetime.now().strftime("%d-%m-%Y")
       if consecutivo == "":
          consecutivoDb = db.child('consecutivo').get().val()
          db.child('consecutivo').set(consecutivoDb+1)
          dataFormulario['metaData']['consecutivo'] = consecutivoDb
          hora= datetime.now().strftime("%H:%M")
           
          db.child('formularios').child(consecutivoDb).set(dataFormulario)
          dataFormulario['desabordado']['inicio'] = f'{hora}'
          dataFormulario['desabordado']['fecha'] = f'{fecha}'
          dataFormulario['desabordado']['firmas']['responsable'] = dataFormulario['metaData']['usuario']
          dataFormulario['paso'] = paso+1
                    

          
       else:

        # DESABORDADO
        if paso == 1:
          base = dataFormulario['metaData']['base']
          if base == "": raise AuthenticationFailed('Asignar Base')
          aerolinea = dataFormulario['metaData']['aerolinea']
          if aerolinea == "": raise AuthenticationFailed('Asignar Aerolinea')
          matricula = dataFormulario['desabordado']['matricula']
          if matricula == "": raise AuthenticationFailed('Asignar Matricula')
          vuelo = dataFormulario['desabordado']['noVuelo']
          if vuelo == "": raise AuthenticationFailed('Asignar Vuelo')

          cantidad = dataFormulario['desabordado']['cantidad']
          if cantidad<0: cantidad = 0
          if cantidad>10: cantidad = 10
          dataFormulario['desabordado']['cantidad'] = cantidad
          detalle = dataFormulario['desabordado']['detalle']
          listaEquipos=[]
          for i in range (0,cantidad):
            if detalle[i]['equipo'] is None or detalle[i]['equipo']=="":
              raise AuthenticationFailed(f'Seleccione Equipo para espacio numero {i+1} o elimine el campo')
            equipo = detalle[i]['equipo']['equipo']
            estado = detalle[i]['equipo']['state']
            if equipo not in listaEquipos:
              listaEquipos.append(equipo)
            else:
              raise AuthenticationFailed(f'Equipo {equipo} seleccionado multiples veces')
            if estado == 'pesado' or estado == 'desabordado':
              raise AuthenticationFailed(f'Equipo {equipo} se encuentra {estado} y no puede ser usado')
          nombreConductor = dataFormulario['desabordado']['firmas']['conductor']
          if nombreConductor == "": raise AuthenticationFailed('Asignar Nombre Conductor')
          placaVehiculo = dataFormulario['desabordado']['firmas']['placa']
          if placaVehiculo == "": raise AuthenticationFailed('Asignar Placa de Vehiculo')
          selloSeguridad = dataFormulario['desabordado']['firmas']['sello1']
          if selloSeguridad == "": raise AuthenticationFailed('Asignar al menos un sello de seguridad')
          supervisor = dataFormulario['desabordado']['firmas']['supervisor']
          if supervisor == "": raise AuthenticationFailed('Asignar Supervisor')
          for i in range (0, cantidad):
            serial = detalle[i]['equipo']['serial']
            db.child('equipos').child(serial).child('state').set('desabordado')
          hora= datetime.now().strftime("%H:%M")
          dataFormulario['desabordado']['final'] = f'{hora}'
          db.child('formularios').child(consecutivo).set(dataFormulario)
          dataFormulario['paso'] = paso+1
          dataFormulario['lavado']['inicio'] = f'{hora}'
          dataFormulario['lavado']['fecha'] = f'{fecha}'
          dataFormulario['lavado']['responsable'] = dataFormulario['metaData']['usuario']


        # LAVADO
        if paso == 2:
          print('paso 2')
          cantidad = dataFormulario['lavado']['cantidad']
          if cantidad<0: cantidad = 0
          if cantidad>10: cantidad = 10
          dataFormulario['lavado']['cantidad'] = cantidad
          detalle = dataFormulario['lavado']['detalle']
          listaEquipos=[]
          for i in range (0,cantidad):
            if detalle[i]['equipo'] is None or detalle[i]['equipo']=="":
              raise AuthenticationFailed(f'Seleccione Equipo para espacio numero {i+1} o elimine el campo')
            equipo = detalle[i]['equipo']['equipo']
            estado = detalle[i]['equipo']['state']
            peso = detalle[i]['pesaje']
            try:
              float(peso)
            except ValueError:
              raise AuthenticationFailed(f'Equipo {equipo} tiene un peso invalido {peso}')
            if equipo not in listaEquipos:
              listaEquipos.append(equipo)
            else:
              raise AuthenticationFailed(f'Equipo {equipo} seleccionado multiples veces')
            if estado == 'pesado' or estado == 'abordaje':
              raise AuthenticationFailed(f'Equipo {equipo} se encuentra {estado} y no puede ser usado')
          for i in range (0, cantidad):
            serial = detalle[i]['equipo']['serial']
            db.child('equipos').child(serial).child('state').set('pesado')
          db.child('formularios').child(consecutivo).set(dataFormulario)
          dataFormulario['paso'] = paso+1
          hora= datetime.now().strftime("%H:%M")
          dataFormulario['abordaje']['inicio'] = f'{hora}'
          dataFormulario['abordaje']['fecha'] = f'{fecha}'
          dataFormulario['abordaje']['firmas']['responsable'] = dataFormulario['metaData']['usuario']

        # ABORDAJE
        if paso == 3:
          matricula = dataFormulario['abordaje']['matricula']
          if matricula =="": raise AuthenticationFailed('Asignar Matricula')
          noVuelo = dataFormulario['abordaje']['noVuelo']
          if noVuelo =="": raise AuthenticationFailed('Asignar numero de vuelo')
          horaSalidaPlanta = dataFormulario['abordaje']['salida']
          if horaSalidaPlanta =="": raise AuthenticationFailed('Asignar Hora de Salida Planta')

          cantidad = dataFormulario['abordaje']['cantidad']
          if cantidad<0: cantidad = 0
          if cantidad>10: cantidad = 10
          dataFormulario['abordaje']['cantidad'] = cantidad
          detalle = dataFormulario['abordaje']['detalle']
          listaEquipos = []
          for i in range (0,cantidad):
            if detalle[i]['equipo'] is None or detalle[i]['equipo']=="":
              raise AuthenticationFailed(f'Seleccione Equipo para espacio numero {i+1} o elimine el campo')
            equipo = detalle[i]['equipo']['equipo']
            estado = detalle[i]['equipo']['state']
            peso = detalle[i]['pesaje']
            try:
              float(peso)
            except ValueError:
              raise AuthenticationFailed(f'Equipo {equipo} tiene un peso invalido {peso}')
            if equipo not in listaEquipos:
              listaEquipos.append(equipo)
            else:
              raise AuthenticationFailed(f'Equipo {equipo} seleccionado multiples veces')
            if estado == 'desabordado' or estado == 'abordaje':
              raise AuthenticationFailed(f'Equipo {equipo} se encuentra {estado} y no puede ser usado')
          nombreConductor = dataFormulario['abordaje']['firmas']['nombreConductor']
          if nombreConductor == "": raise AuthenticationFailed('Asignar nombre de conductor')
          placaVehiculo = dataFormulario['abordaje']['firmas']['placaVehiculo']
          if placaVehiculo =="": raise AuthenticationFailed('Asignar placa de vehiculo')
          selloSeguridad = dataFormulario['abordaje']['firmas']['sello1']
          if selloSeguridad =="": raise AuthenticationFailed('Asignar al menos un sello de seguridad')
          hora= datetime.now().strftime("%H:%M")
          dataFormulario['abordaje']['final'] = f'{hora}'
          for i in range (0, cantidad):
            serial = detalle[i]['equipo']['serial']
            db.child('equipos').child(serial).child('state').set('abordaje')
          db.child('formularios').child(consecutivo).set(dataFormulario)
          dataFormulario['paso'] = paso+1


       return Response(dataFormulario)
    
    if request.method == "PUT":
       serial = request.data['serial']
       user = request.data['user']
       password = request.data['password']
       place = request.data['place']
       active = request.data['active']
       data = {'user':user, 'password':password, 'place':place, 'active':active, 'superadmin':False}
       db.child('users').child(serial).set(data)
       return Response(data)
