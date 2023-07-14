import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import comunity_token, acces_token
from core import VkTools
from data_store import add_user, check_user
from data_store import engine


class BotInterface():

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.interface)
        self.vk_tools = VkTools(acces_token)
        self.api = VkTools(acces_token)
        self.params = {}
        self.users = []
        self.offset = 0
        self.new_city = []
        self.new_age = 0
        self.new_city_id = []
        self.add_user_db = add_user
        self.check_user_db = check_user

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):

        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():

            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                self.params = self.api.get_profile_info(event.user_id)

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)

                    if (self.params['city'] == None) and (self.params['age'] == None or self.params['age'] == 0):
                        self.message_send(event.user_id, f'Здравствуйте, {self.params["name"]}, введите пожалуйста '
                                                         f'ваш город, в формате: город Москва '
                                                         f'и возраст в формате: мне 25 в отдельных сообщениях, '
                                                         f'после для начала работы бота введите поиск')

                    elif self.params['city'] == None:
                        self.message_send(event.user_id, f'Здравствуйте, {self.params["name"]} введите, '
                                                         f'пожалуйста ваш город, в формате: город Москва')

                    elif self.params['age'] == None or self.params['age'] == 0:
                        self.message_send(event.user_id, f'Здравствуйте, {self.params["name"]} введите, '
                                                         f'пожалуйста ваш возраст в формате: мне 25')

                    else: self.message_send(event.user_id, f'Здравствуте, {self.params["name"]} '
                                                           f'для поиска введите: поиск')
                    self.new_city = ['empty']

                elif (command.split(' '))[0] == 'город':
                    self.new_city = (command.split(' '))[1]
                    self.new_city_id = self.api.get_city_id(f'{self.new_city}')
                    if self.new_city_id == 0:
                        self.message_send(event.user_id, f'Нет города в базе данных')
                    else:
                        self.message_send(event.user_id, f'Ваш город: {self.new_city}, введите: поиск')

                elif (command.split(' '))[0] == 'мне':
                    self.new_age = (command.split(' '))[1]
                    self.message_send(event.user_id, f'Ваш возраст: {self.new_age}, введите: поиск')

                elif command == 'поиск':

                    if self.params['city'] == None and self.new_city == ['empty']:
                        self.message_send(event.user_id,
                                          f'Нет города, укажите пожалуйста ваш город, в формате: город Москва')

                    elif self.params['age'] == None and self.new_age == 0:
                        self.message_send(event.user_id,
                                          f'Нет возраста, укажите пожалуйста ваш возраст в формате: мне 25')

                    else:
                        self.params['city'] = self.new_city if self.params['city'] == None else self.params['city']
                        self.params['city_id'] = self.new_city_id
                        self.params['age'] = self.new_age if self.params['age'] == None or self.params['age'] == 0 \
                            else self.params['age']

                        # self.api.search_users(self.params, self.offset)
                        if self.users:
                            user = self.users.pop()
                            while self.check_user_db(engine, event.user_id, user['id']) == True:
                                if len(self.users) == 0:
                                    self.offset += 10
                                    self.users = self.api.search_users(self.params, self.offset)
                                    user = self.users.pop()
                                else:
                                    user = self.users.pop()
                            self.add_user_db(engine, event.user_id, user['id'])
                            photos_user = self.api.get_photos(user['id'])

                            attachment = ''

                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                                if num == 2:
                                    break

                        else:
                            self.users = self.api.search_users(self.params, self.offset)
                            if len(self.users) == 0:
                                self.offset += 10
                                self.users = self.api.search_users(self.params, self.offset)
                                user = self.users.pop()
                            else:
                                user = self.users.pop()
                            while self.check_user_db(engine, event.user_id, user['id']) == True:
                                self.offset += 10
                                if len(self.users) != 0:
                                    user = self.users.pop()
                                else: self.users = self.api.search_users(self.params, self.offset)
                            self.offset += 10
                            self.add_user_db(engine, event.user_id, user['id'])

                            photos_user = self.api.get_photos(user['id'])

                            attachment = ''

                            for num, photo in enumerate(photos_user):
                                attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                                if num == 2:
                                    break
                            self.offset += 10
                            # self.message_send(event.user_id,
                            #                   f'борода')
                        self.message_send(event.user_id,
                                          f'Встречайте {user["name"]} vk.com/id{user["id"]}',
                                          attachment=attachment
                                          )
                        # здесь логика для добавленяи в бд
                elif command == 'пока':
                    self.message_send(event.user_id, f'До новых встреч')
                    break
                else:
                    self.message_send(event.user_id, f'Команда не опознана, для начала работы введите: привет')


if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()