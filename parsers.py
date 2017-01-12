from bs4 import BeautifulSoup
from bs4.element import Tag

from models import Magazine, Item, Image, File


class PCGamesV1:
    """
    для pc игры 2004.01.01 - pc игры 200
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
        sections = list(zip(sections[::2], sections[1::2]))

        return sections

    def _get_items(self, magazine, parent=None):

        for item in self.get_sections():
            orm_item = Item(parent=parent)

            orm_item.title = item[0]
            orm_item.path = item[1]
            orm_item.magazine = magazine

        # for soup_item in soup:
        #     if isinstance(soup_item, Tag) and soup_item.name == 'item':
        #         orm_item = Item(parent=parent)
        #
        #         orm_item.title = self._get_item_title(soup_item)
        #         orm_item.path = self._get_item_path(soup_item)
        #         orm_item.head = self._get_item_head(soup_item)
        #         orm_item.text = self._get_item_text(soup_item)
        #         orm_item.magazine = magazine
        #         orm_item.save()
        #
        #         if not soup_item.item:
        #
        #             images = self._get_item_images(soup_item)
        #             if images:
        #                 for image in images:
        #                     Image.create(item=orm_item, image=image)
        #
        #             files = self._get_item_files(soup_item)
        #             if files:
        #                 for title, file in files:
        #                     File.create(item=orm_item, title=title, file=file)
        #
        #         else:
        #             self._get_items(soup_item, magazine, orm_item)

    def save_items(self):
        orm_magazine = Magazine.create(title=self.get_title(), info=self.get_info())

        self._get_items(orm_magazine)


asd = PCGamesV1('E:\pc игры\pc игры 2004\pc игры 2004.01.01.1')
print(asd.save_items())


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
