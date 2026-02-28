#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Игра для изучения английского языка с распознаванием речи
"""

import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from googletrans import Translator
import random
import os
import time
import sys

# Инициализация переводчика
translator = Translator()

# 💡 Несколько подсказок:
# — Словарь слов по уровням сложности (easy / medium / hard)
# — Сначала выбор уровня, потом случайное слово: random.choice(words_by_level[level])
# — Цепочка: запись речи → распознавание → перевод → сравнение
# — Счёт и ошибки (жизни); при 3 ошибках — конец игры
# — Для сравнения всё в нижний регистр: recognized = recognized.lower()

words_by_level = {
    'easy': [
        'кот', 'собака', 'дом', 'машина', 'яблоко', 'книга', 'стол', 'стул',
        'вода', 'хлеб', 'солнце', 'луна', 'звезда', 'дерево', 'цветок', 'птица',
        'рыба', 'море', 'небо', 'земля', 'огонь', 'ветер', 'дождь', 'снег', 'жизнь', 'рука', 'нога', 'волосы'
    ],
    'medium': [
        'компьютер', 'телефон', 'школа', 'университет', 'библиотека', 'больница',
        'ресторан', 'магазин', 'аэропорт', 'вокзал', 'музей', 'театр', 'кино',
        'спорт', 'музыка', 'живопись', 'литература', 'математика', 'физика', 'программирование',
        'химия', 'биология', 'история', 'география', 'философия', 'игра', 'футбол', 'хоккей', 'волейбол', 'улица'
    ],
    'hard': [
        'достижение', 'возможность', 'ответственность', 'обстоятельство',
        'предпринимательство', 'интеллектуальный', 'эмоциональный', 'психологический',
        'философский', 'теоретический', 'практический', 'профессиональный',
        'индивидуальный', 'коллективный', 'демократический', 'экономический',
        'политический', 'социальный', 'культурный', 'исторический', 'биологический'
    ]
}

class EnglishGame:
    def __init__(self):
        self.score = 0
        self.level = 'easy'
        self.lives = 3
        self.recognizer = sr.Recognizer()
        self.translator = Translator()
        self.stats = {'correct': 0, 'wrong': 0, 'total': 0}
        
    def print_header(self):
        """Красивый заголовок игры"""
        header = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎓 ИГРА ДЛЯ ИЗУЧЕНИЯ АНГЛИЙСКОГО ЯЗЫКА 🎓            ║
║                                                              ║
║              🗣️  Распознавание речи 🗣️                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(header)
        
    def print_separator(self):
        """Разделитель"""
        print("=" * 60)
        
    def choose_level(self):
        """Выбор уровня сложности"""
        self.print_separator()
        print("\n📚 ВЫБЕРИТЕ УРОВЕНЬ СЛОЖНОСТИ:\n")
        print("1️⃣  Легкий (Easy) - простые слова")
        print("2️⃣  Средний (Medium) - средние слова")
        print("3️⃣  Сложный (Hard) - сложные слова")
        print("\n" + "=" * 60)
        
        while True:
            choice = input("\n👉 Введите номер уровня (1-3): ").strip()
            if choice == '1':
                self.level = 'easy'
                print("\n✅ Выбран легкий уровень! 🟢")
                break
            elif choice == '2':
                self.level = 'medium'
                print("\n✅ Выбран средний уровень! 🟡")
                break
            elif choice == '3':
                self.level = 'hard'
                print("\n✅ Выбран сложный уровень! 🔴")
                break
            else:
                print("❌ Неверный выбор! Попробуйте снова.")
                
    def get_translation(self, word):
        """Получить перевод слова"""
        try:
            translation = self.translator.translate(word, src='ru', dest='en')
            return translation.text.lower()
        except Exception as e:
            print(f"⚠️ Ошибка перевода: {e}")
            return None
            
    def record_audio(self, duration=6):
        """Записать аудио"""
        print(f"\n🎤 Говорите перевод слова... (запись {duration} секунд)")
        print("⏱️  Запись началась...")
        
        try:
            # Запись аудио (16000 Hz — стандарт для распознавания речи)
            fs = 16000
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
            sd.wait()  # Ждем окончания записи

            # Конвертируем в 16-bit PCM (SpeechRecognition ожидает такой формат)
            recording_int16 = (np.clip(recording, -1.0, 1.0) * 32767).astype(np.int16)

            # Сохраняем во временный файл
            filename = "temp_audio.wav"
            wav.write(filename, fs, recording_int16)
            
            print("✅ Запись завершена!")
            return filename
        except Exception as e:
            print(f"❌ Ошибка записи: {e}")
            return None
            
    def recognize_speech(self, audio_file):
        """Распознать речь из аудио файла"""
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                
            # Используем Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language='en-US')
            recognized = text if text else ""
            recognized = recognized.lower()
            return recognized
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"❌ Ошибка распознавания: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
            
    def check_answer(self, user_answer, correct_answer):
        """Проверить ответ пользователя"""
        if not user_answer:
            return False
            
        # Удаляем знаки препинания и приводим к нижнему регистру
        user_clean = ''.join(c for c in user_answer if c.isalnum() or c.isspace())
        correct_clean = ''.join(c for c in correct_answer if c.isalnum() or c.isspace())
        
        # Проверяем точное совпадение или частичное
        if user_clean == correct_clean:
            return True
        elif user_clean in correct_clean or correct_clean in user_clean:
            return True
        else:
            # Проверяем по словам (на случай если пользователь сказал несколько слов)
            user_words = set(user_clean.split())
            correct_words = set(correct_clean.split())
            if user_words & correct_words:  # Есть общие слова
                return True
        return False
        
    def play_round(self):
        """Один раунд игры"""
        # Выбираем случайное слово
        word = random.choice(words_by_level[self.level])
        correct_translation = self.get_translation(word)
        
        if not correct_translation:
            print("❌ Не удалось получить перевод. Пропускаем слово.")
            return False
            
        self.print_separator()
        print(f"\n📖 Слово на русском: {word.upper()}")
        print(f"💡 Подсказка: слово начинается с '{correct_translation[0].upper()}'")
        
        # Записываем аудио
        audio_file = self.record_audio(duration=6)
        if not audio_file:
            return False
            
        # Распознаем речь
        print("\n🔍 Распознавание речи...")
        user_answer = self.recognize_speech(audio_file)
        if user_answer is not None:
            user_answer = user_answer.lower()

        # Удаляем временный файл
        try:
            os.remove(audio_file)
        except:
            pass
            
        # Проверяем ответ
        if user_answer:
            print(f"🎤 Вы сказали: '{user_answer}'")
        else:
            print("❌ Не удалось распознать речь. Попробуйте говорить четче.")
            return False
            
        is_correct = self.check_answer(user_answer, correct_translation)
        
        if is_correct:
            self.score += 10
            self.stats['correct'] += 1
            print(f"\n✅ ПРАВИЛЬНО! 🎉")
            print(f"✅ Правильный ответ: '{correct_translation}'")
            print(f"💰 Ваши баллы: {self.score} 🏆")
        else:
            self.lives -= 1
            self.stats['wrong'] += 1
            print(f"\n❌ НЕПРАВИЛЬНО! 😔")
            print(f"✅ Правильный ответ: '{correct_translation}'")
            print(f"💔 Осталось жизней: {self.lives} ❤️")
            
        self.stats['total'] += 1
        return True
        
    def show_stats(self):
        """Показать статистику"""
        self.print_separator()
        print("\n📊 СТАТИСТИКА ИГРЫ:\n")
        print(f"✅ Правильных ответов: {self.stats['correct']}")
        print(f"❌ Неправильных ответов: {self.stats['wrong']}")
        print(f"📈 Всего слов: {self.stats['total']}")
        if self.stats['total'] > 0:
            accuracy = (self.stats['correct'] / self.stats['total']) * 100
            print(f"🎯 Точность: {accuracy:.1f}%")
        print(f"💰 Итоговые баллы: {self.score} 🏆")
        self.print_separator()
        
    def game_over(self):
        """Экран Game Over"""
        self.print_separator()
        print("\n" + "=" * 60)
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    💀 GAME OVER 💀                          ║
║                                                              ║
║              У вас закончились жизни!                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        self.show_stats()
        print("\n🎮 Спасибо за игру! До встречи! 👋\n")
        
    def show_instructions(self):
        """Показать инструкции"""
        instructions = """
╔══════════════════════════════════════════════════════════════╗
║                    📋 ИНСТРУКЦИЯ                             ║
╚══════════════════════════════════════════════════════════════╝

🎯 ЦЕЛЬ ИГРЫ:
   Вам будет показано слово на русском языке.
   Вы должны произнести его перевод на английском.
   Программа запишет ваш голос и проверит правильность.

🎮 ПРАВИЛА:
   • У вас есть 3 жизни ❤️❤️❤️
   • За правильный ответ: +10 баллов 💰
   • За неправильный ответ: -1 жизнь 💔
   • Игра заканчивается, когда жизни закончатся

💡 СОВЕТЫ:
   • Говорите четко и громко
   • Используйте микрофон правильно
   • Не торопитесь, у вас есть 6 секунд на запись

🎯 УРОВНИ:
   • Легкий: простые слова (кот, дом, стол)
   • Средний: средние слова (компьютер, школа)
   • Сложный: сложные слова (достижение, ответственность)

        """
        print(instructions)
        input("👉 Нажмите Enter, чтобы начать игру...")
        
    def play(self):
        """Основной цикл игры"""
        self.print_header()
        self.show_instructions()
        self.choose_level()
        
        print("\n🎮 ИГРА НАЧАЛАСЬ! Удачи! 🍀\n")
        time.sleep(1)
        
        while self.lives > 0:
            if not self.play_round():
                continue
                
            if self.lives > 0:
                print("\n⏳ Следующее слово через 2 секунды...")
                time.sleep(2)
                
        self.game_over()
        
        # Предложение сыграть снова
        play_again = input("\n🔄 Хотите сыграть еще раз? (да/нет): ").lower()
        if play_again in ['да', 'yes', 'y', 'д']:
            self.__init__()
            self.play()

def main():
    """Главная функция"""
    try:
        game = EnglishGame()
        game.play()
    except KeyboardInterrupt:
        print("\n\n👋 Игра прервана пользователем. До свидания!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        print("Пожалуйста, проверьте установку всех библиотек.")
        sys.exit(1)

if __name__ == "__main__":
    main()