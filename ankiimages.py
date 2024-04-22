import genanki
import random

class AnkiDeckCreator:
    def __init__(self, deck_name):
        # 使用随机生成的ID确保唯一性
        deck_id = random.randrange(1 << 30, 1 << 31)
        model_id = random.randrange(1 << 30, 1 << 31)
        
        self.deck = genanki.Deck(deck_id, deck_name)
        self.model = genanki.Model(
            model_id,
            'Simple Model with Image',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'FlagImage'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}',  # 显示问题和图片
                    'afmt': '{{FrontSide}}<hr id=answer>{{Answer}}{{FlagImage}}',  # 显示问题、图片和答案
                },
            ])
        self.media_files = []

    def add_card(self, question, answer, image_path=None):
        fields = [question, answer, f'<img src="{image_path}">' if image_path else ""]
        note = genanki.Note(
            model=self.model,
            fields=fields
        )
        self.deck.add_note(note)
        if image_path:
            self.media_files.append(image_path)

    def save_deck(self, file_path):
        package = genanki.Package(self.deck)
        package.media_files = self.media_files
        package.write_to_file(file_path)

# # 使用示例:
# deck_creator = AnkiDeckCreator('国家旗帜')
# deck_creator.add_card('旗帜是哪个国家的？', '加拿大', 'test4.jpg')
# deck_creator.save_deck('test.apkg')
