import sqlite3

def changeDataFromFeedback(feedback,request_id):



    try:
        conn = sqlite3.connect("db.sqlite3")                                                                        # connexion BdD
        cursor = conn.cursor()
        get_list = "SELECT * FROM url_responses WHERE request_id=?"                                                 # ici, nous cherchons toutes les urls lies au requete du client
        cursor.execute(get_list, (request_id,))
        list = cursor.fetchall()

        for i in range(0,len(list)):
            if feedback[i]['feedback']==0 :                                                                         # nous economisons des requetes en laissent les valeurs deja a zera
                change_feedback="UPDATE url_responses SET feedback=? WHERE request_id=? and image_url=?"            # nous mettons a 0 ou 1 quand le feedback est recu (sinon la valeur est 0 par defaut)
                cursor.execute(change_feedback,(feedback[i]['feedback'],request_id,list[i][2],))
        conn.commit()
        change_score = "UPDATE url_responses SET score=score/2 WHERE feedback=1 and request_id=?"                   # nous divisons par 2 le score du "mauvais feedback"
        cursor.execute(change_score, (request_id,))
        conn.commit()
        return 0                                                                                                    # Good tout est ok
    except:
        return 1                                                                                                    # Attention erreur


