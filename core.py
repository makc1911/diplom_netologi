from pprint import pprint
from datetime import datetime
import vk_api
from vk_api.exceptions import ApiError
from config import acces_token


class VkTools():
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)


    def _bdate_toyear(self, bdate):
        len_bdate = bdate.split('.')
        if len(len_bdate) > 2:
            user_year = bdate.split('.')[2]
            now = datetime.now().year
            return now - int(user_year)
        else:
            return 0

    def get_profile_info(self, user_id):

        try:
            info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,bdate,sex,relation,home_town'
                                 }
                                )
        # return info
        except ApiError as error:
            info = {}
            print(f'error = {error}')

        user_info = {'name': (info['first_name'] + ' ' + info['last_name']) if
                     'first_name' in info and 'last_name' in info else None,
                     'id': info.get('id'),
                     'age': self._bdate_toyear(info.get('bdate')) if 'bdate' in info else None,
                     'home_town': info.get('home_town'),
                     'sex': info.get('sex'),
                     'city': info.get('city')['title'] if 'city' in info else None
                     }

        return user_info

    def get_city_id(self, city_name):
        try:
            self.api.method('database.getCities', {'country_id': 1, 'q': city_name})
            response = self.api.method('database.getCities', {'country_id': 1, 'q': city_name})
            if response == {'count': 0, 'items': []}:
                city_id = 0
            else:
                city_id = response['items'][0]['id']
            return int(city_id)
        except ApiError as error:
            print(f'Error getting city ID: {error}')
            return None

    def search_users(self, params, offset):
        try:
            users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': offset,
                                 'age_from': int((params['age'])) - 3,
                                 'age_to': int((params['age'])) + 3,
                                 'sex': 1 if params['sex'] == 2 else 2,
                                 'hometown': params['city'],
                                 'city': params['city_id'],
                                 #'status': 6,
                                 'has_photo': True
                                 }
                                )
        except ApiError as error:
            users = []
            print(f'error = {error}')

        result = [{'name': item['first_name'] + ' ' + item['last_name'], 'id': item['id']
                   } for item in users['items'] if item['is_closed'] is False]

        return result[:2]


    def get_photos(self, id):
        try:
            photos = self.api.method('photos.get',
                                 {'owner_id': id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )

        except KeyError:
            return []

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                   } for item in photos['items']
                  ]

        sort_result = []

        for photo in result:
            sort_result.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes'],
                        'comments': photo['comments'],
                        }
                       )

        sort_result.sort(key=lambda x: x['likes'] + x['comments'], reverse=True)

        return sort_result


# if __name__ == '__main__':
#     bot = VkTools(acces_token)
#     user_id = 83437969
#     params = bot.get_profile_info(user_id)
#     users = bot.search_users(params)
#     user = users.pop()
#     photos = bot.get_photos(user['id'])
#     # print(bot.get_photos(users[2]['id']))
#
#     pprint(photos)