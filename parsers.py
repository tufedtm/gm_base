import os
from configparser import ConfigParser

from bs4 import BeautifulSoup
from bs4.element import Tag

from models import Magazine, Item, Image, File


class PCGamesV1:
    """
    для pc игры 2004.01.01
    """

    def __init__(self, folder):
        self.folder = f'{folder}/content'

    def get_title(self):
        return open(f'{self.folder}/cdtitle.txt').read().strip()

    def get_info(self):
        return open(f'{self.folder}/information.txt').read().strip()

    def get_sections(self):
        sections = open(f'{self.folder}/sections.txt').readlines()
        sections = [x.strip() for x in sections if x.strip() not in ['13', 'verdana'] and '$' not in x.strip()]

        return self._list_to_pair(sections)

    @staticmethod
    def _list_to_pair(items):
        return list(zip(items[::2], items[1::2]))

    def save_items(self):
        orm_magazine = Magazine.create(title=self.get_title(), info=self.get_info())
        self._save_items(orm_magazine)
        print(self.get_title())

    def _save_items(self, magazine, parent=None):

        for section in self.get_sections():
            orm_item = Item(parent=parent)
            orm_item.title = section[0]
            orm_item.path = section[1]
            orm_item.magazine = magazine
            orm_item.save()

            items = open(f'{self.folder}/{orm_item.path}/items.txt').readlines()[2:]
            items = [x.strip() for x in items]

            for item in self._list_to_pair(items):
                path = f'{self.folder}/{orm_item.path}/{item[1]}'

                orm_sub_item = Item(parent=orm_item)
                orm_sub_item.title = item[0]
                orm_sub_item.path = item[1]
                orm_sub_item.text = open(f'{path}/info.txt').read()
                orm_sub_item.magazine = magazine
                orm_sub_item.save()

                files = os.listdir(f'{path}')
                files.remove('info.txt')

                for file in files:
                    filetype = file.split('.')[-1]

                    if filetype in ['bmp', 'gif', 'jpg', 'jpeg', 'png']:
                        Image.create(item=orm_sub_item, image=file)
                    elif filetype not in ['txt']:
                        File.create(item=orm_sub_item, file=file)


class PCGamesV2(PCGamesV1):
    """
    для pc игры 2004.03.03 - pc игры 2004.09.09 (мб pc игры 2004.10.10)
    """

    def get_title(self):

        config = ConfigParser()
        config.read_file(open(f'{self.folder}/config.ini'))

        return config['Settings']['cd_title'].strip()

    def get_soup(self):
        xml_file = open(f'{self.folder}/content.xml').read()
        soup = BeautifulSoup(xml_file, 'xml')

        return soup.find('CONTENT').children

    def get_sections(self):
        pass

    def save_items(self):
        orm_magazine = Magazine.create(title=self.get_title(), info=self.get_info())
        self._save_items(self.get_soup(), orm_magazine)
        print(self.get_title())

    def _save_items(self, soup, magazine, path='', parent=None):
        for soup_item in soup:
            if parent:
                full_path = f'{path}/{soup_item["path"]}'
            else:
                full_path = f'{self.folder}/{soup_item["path"]}'

            orm_item = Item(parent=parent)
            orm_item.title = soup_item['name']
            orm_item.path = soup_item['path']
            if os.path.exists(f'{full_path}/info.txt'):
                orm_item.text = open(f'{full_path}/info.txt').read().strip()
            orm_item.magazine = magazine
            orm_item.save()

            if os.path.exists(f'{full_path}/files.ini'):
                config = ConfigParser()
                config.read_file(open(f'{full_path}/files.ini'))

                for file in config['Files'].values():
                    File.create(item=orm_item, title=config[file]['Title'], file=config[file]['File'])

            for file in os.listdir(f'{full_path}'):
                filetype = file.split('.')[-1]

                if filetype in ['bmp', 'gif', 'jpg', 'jpeg', 'png']:
                    Image.create(item=orm_item, image=file)

            if list(soup_item.children):
                self._save_items(soup_item.children, magazine, full_path, orm_item)


class PCGames2006First:
    """
    для pc игры 2006.25.01 - pc игры 2006.28.04
    """

    def __init__(self, folder):
        self.folder = folder

    def get_soup(self):
        xml_file = open(f'{self.folder}/autorun/data/config.xml').read()
        soup = BeautifulSoup(xml_file, 'xml')

        return soup

    def get_title(self):
        return self.get_soup().disk['title'].strip()

    def get_title_full(self):
        return self.get_soup().info['title'].strip()

    def get_info(self):
        return self.get_soup().info.get_text('\n', strip=True)

    def save_items(self):
        orm_magazine = Magazine.create(title=self.get_title(), title_full=self.get_title_full(), info=self.get_info())
        self._get_items(self.get_soup().disk.children, orm_magazine)
        print(self.get_title())

    @staticmethod
    def _get_item_title(item):
        return item['title'].strip()

    @staticmethod
    def _get_item_path(item):
        return item['path'].strip()

    @staticmethod
    def _get_item_head(item):
        soup = item.find('head', recursive=False)

        if soup:
            head = ''.join(str(item).strip() for item in soup.contents)

            return head if head else None

    @staticmethod
    def _get_item_text(item):
        soup = item.find('text', recursive=False)

        if soup:
            text = ''.join(str(item).strip() for item in soup.contents)

            return text if text else None

    @staticmethod
    def _get_item_images(item):
        soup = item.find('images', recursive=False)

        if soup:
            return [image['name'].strip() for image in soup.find_all('image')]

    @staticmethod
    def _get_item_files(item):
        soup = item.find('files', recursive=False)

        if soup:
            return [(file['title'].strip(), file['name'].strip()) for file in soup.find_all('file')]

    def _get_items(self, soup, magazine, parent=None):

        for soup_item in soup:
            if isinstance(soup_item, Tag) and soup_item.name == 'item':
                orm_item = Item(parent=parent)

                orm_item.title = self._get_item_title(soup_item)
                orm_item.path = self._get_item_path(soup_item)
                orm_item.head = self._get_item_head(soup_item)
                orm_item.text = self._get_item_text(soup_item)
                orm_item.magazine = magazine
                orm_item.save()

                if not soup_item.item:

                    images = self._get_item_images(soup_item)
                    if images:
                        for image in images:
                            Image.create(item=orm_item, image=image)

                    files = self._get_item_files(soup_item)
                    if files:
                        for title, file in files:
                            File.create(item=orm_item, title=title, file=file)

                else:
                    self._get_items(soup_item, magazine, orm_item)


class PCGames2006Second(PCGames2006First):
    """
    для pc игры 2006.29.05.01 - pc игры 2006.35.11
    """

    def get_soup(self):
        xml_file = open(f'{self.folder}/autorun/data/disk_contents.xml').read()
        soup = BeautifulSoup(xml_file, 'xml')

        return soup

    def get_title_full(self):
        return self.get_soup().diskinfo.title.get_text('\n', strip=True)

    def get_info(self):
        return self.get_soup().diskinfo.find('text').get_text('\n', strip=True)

    def save_items(self):
        orm_magazine = Magazine.create(title=self.get_title(), title_full=self.get_title_full(), info=self.get_info())
        self._get_items(self.get_soup().items.children, orm_magazine)
        print(self.get_title())

    def _get_items(self, soup, magazine, parent=None):

        for soup_item in soup:
            if isinstance(soup_item, Tag) and soup_item.name == 'item':
                orm_item = Item(parent=parent)

                orm_item.title = self._get_item_title(soup_item)
                orm_item.title2 = self._get_item_title2(soup_item)
                orm_item.path = self._get_item_path(soup_item)
                orm_item.head = self._get_item_head(soup_item)
                orm_item.text = self._get_item_text(soup_item)
                orm_item.magazine = magazine
                orm_item.save()

                if not soup_item.item:

                    images = self._get_item_images(soup_item)
                    if images:
                        for image in images:
                            Image.create(item=orm_item, image=image)

                    files = self._get_item_files(soup_item)
                    if files:
                        for title, file in files:
                            File.create(item=orm_item, title=title, file=file)

                else:
                    self._get_items(soup_item, magazine, orm_item)

    @staticmethod
    def _get_item_iteminfo(item):
        soup = item.find('infoitem', recursive=False)

        if soup:
            return soup

    def _get_item_title2(self, item):
        soup = self._get_item_iteminfo(item)

        if soup:
            soup = soup.find('title', recursive=False)

        if soup:
            return soup.get_text('\n', strip=True)

    def _get_item_head(self, item):
        soup = self._get_item_iteminfo(item)

        if soup:
            soup = soup.find('head', recursive=False)

        if soup:
            head = ''.join(str(item).strip() for item in soup.contents)

            return head if head else None

    def _get_item_text(self, item):
        soup = self._get_item_iteminfo(item)

        if soup:
            soup = soup.find('text', recursive=False)

        if soup:
            text = ''.join(str(item).strip() for item in soup.contents)

            return text if text else None

    @staticmethod
    def _get_item_images(item):
        soup = item.find('images', recursive=False)

        if soup:
            return [image['file'].strip() for image in soup.find_all('image')]

    @staticmethod
    def _get_item_files(item):
        soup = item.find('files', recursive=False)

        if soup:
            return [(file.get_text('\n', strip=True), file['path'].strip()) for file in soup.find_all('file')]


class PCGames2006Third(PCGames2006Second):
    """
    для pc игры 2006.36.12.01
    """

    def get_soup(self):
        xml_file = open(f'{self.folder}/content/Content.xml').read()
        soup = BeautifulSoup(xml_file, 'xml')

        return soup

    def _get_item_text(self, item):
        soup = self._get_item_iteminfo(item)

        if soup:
            soup = soup.find('text1', recursive=False)

        if soup:
            text = ''.join(str(item).strip() for item in soup.contents)

            return text if text else None
