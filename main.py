import argparse
import mysql.connector as mysql
import ftplib
import traceback

from debug import Debug
import real_discount
import discudemy
import udemyfreebies


class App:
    def run(self, provider: str='realdiscount') -> list:
        valid = 0
        debug = Debug(f'logs/{provider}')
        debug.print('\nScraping started')

        try:
            for data in self.scrape(provider, debug):
                valid = valid + 1
                yield data
            debug.end()
        except KeyboardInterrupt:
            debug.print('\nStopping manually...')
            debug.is_summary(f'Successfully validated {valid} coupons')
            debug.end()
        except Exception as e:
            debug.print('\nStopping with some error...')
            debug.is_summary(f'Successfully validated {valid} coupons')
            debug.print(f'Error: {e}, {traceback.format_exc()}')
            debug.end()

    def scrape(self, selected, debug: Debug) -> list:
        if selected == 'realdiscount':
            for rd in real_discount.scrape(debug=debug):
                yield rd
        elif selected == 'discudemy':
            for dc in discudemy.scrape(debug=debug):
                yield dc
        elif selected == 'udemyfreebies':
            for uf in udemyfreebies.scrape(debug=debug):
                yield uf
        yield {'mode': 'end', 'message': 'Finished...', 'provider': selected}

    def connect(self):
        connection = mysql.connector.connect(
            host="70.39.235.94",
            user="van@tracking39j.com",  # "van",
            password="0HbvhVwW70n^&qyx",
            database="tracki19_tracker",
            port=3306
        )
        return connection

    def ftp_connect(self):
        host = 'coursedeals.net'
        user = 'van@tracking39j.com'
        password = '0HbvhVwW70n^&qyx'

        with ftplib.FTP(host, user, password) as ftp:
            ftp.cwd('/media/dev-van')
            files = ftp.nlst()
            for file in files:
                print(file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape coupons from a given provider.')
    parser.add_argument('provider', choices=['realdiscount', 'discudemy', 'udemyfreebies'], help='The provider to scrape')
    args = parser.parse_args()

    app = App()
    results = app.run(args.provider)
    for result in results:
        print(result)
