import requests
import sys
import argparse


class Server:
    def __init__(self, bas: str, acc: str) -> None:
        self.base = bas
        self.access_key = 'accessKey ' + acc

    def __fetch_devices(self, page: int) -> dict:
        respond = requests.get(f'{self.base}/devices?page={page}&size=100',
                               headers={'Authorization': self.access_key})
        if not respond.ok:
            sys.exit(f'{respond} Check if url or accessKey are correct')

        return respond.json()

    def fetch_all_devices(self) -> list:
        print('fetching devices...')
        devices = []
        page = 0
        while True:
            data = self.__fetch_devices(page)
            if not data['items']:
                break
            devices += data['items']
            page += 1

        return devices

    def __fetch_user(self, user_id: str) -> dict:
        try:
            respond = requests.get(f'{self.base}/users/{user_id}',
                                   headers={'Authorization': self.access_key})
        except:
            print(sys.exc_info())
            return {}

        if not respond.ok:
            print(f'{respond} when try to fetch user: {user_id}')
            return {}

        return respond.json()

    def fetch_all_users(self, devices: list) -> list:
        print('fetching users...')
        data_list = []
        for key, dev in enumerate(devices):
            if 'userId' in dev.keys() and dev['userId'] != '':
                user = self.__fetch_user(dev['userId'])

                if not user:
                    continue

                firs_name = ''
                last_name = ''
                if 'firstName' in user:
                    firs_name = user['firstName']
                elif 'lastName' in user:
                    last_name = user['lastName']
                else:
                    continue

                user_name = f'{firs_name} {last_name}'

                data_list.append((dev['deviceId'], user_name))

        return data_list

    def __update_device(self, dev_id: str, user_name: str) -> bool:
        respond = requests.post(f'{self.base}/devices/{dev_id}',
                                headers={'Authorization': self.access_key},
                                json={'userName': user_name})
        return respond.ok

    def update_all_devices(self, data_list: list) -> None:
        print('updating devices...')
        success = 0
        fail = 0
        for data in data_list:
            respond = self.__update_device(data[0], data[1])
            if respond:
                success += 1
            else:
                fail += 1
        print(f'finished to update devices succeeded: {success}  failed: {fail}')

    def run(self):
        devices = self.fetch_all_devices()
        data_list = self.fetch_all_users(devices)
        self.update_all_devices(data_list)


def cli() -> tuple:
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', type=str, help='the base url for all requests')
    parser.add_argument('-a', type=str, help='key which grants access to the server')

    args = parser.parse_args()
    if not args.b or not args.a:
        sys.stdout.write("You need to provide 'base url' and 'access key' values.")
        sys.exit(1)

    return args.b, args.a


if '__main__' == __name__:
    base, access_key = cli()
    # base = 'https://admin.dev.orcam.io/api/v8'
    # access_key = 'test-key-id-1'
    server = Server(base, access_key)
    server.run()
