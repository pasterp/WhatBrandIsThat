# Create your views here.
import sqlite3
from images.serializers import RequestSerializer
import datetime
from bow_retrieval import test
from bow_retrieval import onlin_search
from bow_retrieval import build_json_response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from images import feedback


class ImgSearch(APIView):

    def get(self,request,format=None,**kwargs):
        if(len(kwargs)==0):
            response = Response("BAD URL REQUEST", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return response
        else:
            return self.get2_id(request, kwargs['pk'])



    def get2_id(self, request,pk, format=None,**kwargs):                                                                # GET de la liste correspondant a la requete "pk"
        conn = sqlite3.connect("db.sqlite3")                                                                            # connexion a la BdD
        cursor = conn.cursor()
        check_id="SELECT * FROM images_request WHERE id=?"
        cursor.execute(check_id,(pk,))
        results=cursor.fetchall()
        if(len(results)!=0):
            jsonresp=build_json_response.jsonize(pk)                                                                    # Stockage de l objet Json a traiter par le client android
            response = Response(jsonresp, status=status.HTTP_200_OK)
            return response                                                                                             # retourne d une response avec l objet json
        else:
            response = Response("BAD URL REQUEST",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return response


    def post(self, request, format=None, **kwargs):                                                                     # POST de l'image en base 64
        serializer = RequestSerializer(data=request.data)                                                               # contient seulement le dict 'base64'
        print(request.data)
        #print(len(request.data['base64']))
        print(request.META)
        file = open("REQUETE_LOG.txt", "w")
        file.write(str(request.data))
        file.close()

        if (len(kwargs) != 0):
            return Response("BAD URL REQUEST", status=status.HTTP_400_BAD_REQUEST)

        client_details='Adresse IP : '                                                                                  # pour le format de la string
        ip_addr=request.environ['REMOTE_ADDR']                                                                          # sert a recolter l'adresse ip du client
        client_details+= ip_addr + ' Details :'                                                                         # pour le format de la string
        agent = request.environ.get('HTTP_USER_AGENT')                                                                  # details sur la version d'android ou autre du client
        client_details+=agent                                                                                           # nous ajoutons dans le details le client (android etc...)
        date=datetime.datetime.now()                                                                                    # nous recuperons la date actuelle
        date_format=date.strftime("%d/%m/%Y %H:%M:%S.%f")                                                               # nous recuperons la date du moment de la requete
        request.data['client'] = client_details                                                                         # nous stockons dans 'client'
        request.data['request_date']=date_format                                                                        # nous gardons la date
        base_64PourAnalyse=request.data['base64']                                                                       # nous conservons dans une variable la string B64
        request.data['base64']=""                                                                                       # nous effacons l'image du client en base64 par de place dans la BdD il est possible de la sauvegarder si le client veut la dviser
        if serializer.is_valid():
            serializer.save()                                                                                           # nous ecrivons dans la BdD les datas du serializer
            conn = sqlite3.connect("db.sqlite3")                                                                        # nous nous connectons a la BdD
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM images_request WHERE request_date=?', (date_format,))                        # nous recherchons du dernier id cree
            id_cree = cursor.fetchall()                                                                                 # nous stockons de l'id
            conn.close()                                                                                                # nous fermons la connexion avec la BdD
            typeimg = ''
            if "png" in base_64PourAnalyse:                                                                             # l image est de type png
                typeimg = "png"
            else:
                typeimg = "jpg"                                                                                         # l imag est de type  jpg
            img_construite = test.buildAndReturnLabel(base_64PourAnalyse,typeimg)                                       # fonction qui nous retourne l'image construite et la compare avec les autres image

            onlin_search.return_img_list(img_construite,id_cree[0][0])                                                  # liste_similaire contient le chemin des images les plus similaires classees
            response = Response({"Location" : "/img_searches/"+ str(id_cree[0][0])} , status=status.HTTP_201_CREATED)   # nous retourne une location avec l'ID de l'objet cree en BD
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Feedback(APIView):

    def post(self, request, format=None, **kwargs):
        client_feedback=request.data['results']
        client_request_id=request.data['request_id']
        changes=feedback.changeDataFromFeedback(client_feedback,client_request_id)

        if(changes==0):
            return Response('Thank you for feedback', status=status.HTTP_200_OK)
        else:
            return Response('An error occured', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self,request,format=None, **kwargs):
        return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)