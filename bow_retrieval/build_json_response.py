import sqlite3

def jsonize(request_id):

    conn = sqlite3.connect("db.sqlite3")                                                                                # nous nous connections a la BdD
    cursor = conn.cursor()
    get_date="SELECT request_date FROM images_request WHERE id=?"                                                       # nous cherchons la date de la requete
    cursor.execute(get_date, (request_id,))
    user_request = cursor.fetchone()
    date=user_request[0]

    get_client = "SELECT client FROM images_request WHERE id=?"                                                         # nous cherchons le client qui a demande cette requete
    cursor.execute(get_client, (request_id,))
    client_request = cursor.fetchone()
    client = client_request[0]

    get_urls="SELECT * FROM url_responses WHERE request_id=?"                                                           # nous cherchons les urls du resultat de la requete
    cursor.execute(get_urls, (request_id,))
    user_corresponding_result = cursor.fetchall()
    data={}                                                                                                             # nous initialisons l objet json que nous voulons renvoyer pour le GET
    data['date']=date                                                                                                   # nous atribuons une date
    data['client']=client                                                                                               # nous attribuons un client
    data['request_id']=request_id

    urls_list=[]                                                                                                        # nous listons les urls ainsi que le score
    for i in range(0,len(user_corresponding_result)):
        url_element={}                                                                                                  # un url_element correspond a une url avec son score dans le dictionnaire
        url_element['image_url']=user_corresponding_result[i][2]
        url_element['score']=user_corresponding_result[i][3]
        urls_list.append(url_element)

    data['results']=urls_list                                                                                           # nous le stockons la liste


    return data                                                                                                         # nous retournons le  resultat
