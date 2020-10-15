from db_maker import *

for client in Client.find():
    print(client['nom'])
    if 'contrats' in client:
        list1 = list(client['contrats'])
        try:
            list2 = list(client['contratsV'])
        except:
            list2 = list([])
        for cont in client['contrats']:
            try:
                cnt = Contrat.find_one({'_id': cont})
                print(cnt['_id'])
            except:
                list2.append(cont)
                list1.remove(cont)
        # print('list1', list1)
        # print('list2', list2)
        Client.update_one({'_id': client['_id']},{'$set': {'contrats': list1}})
        Client.update_one({'_id': client['_id']},{'$set': {'contratsV': list2}})

for voiture in Voiture.find():
    print('ss')