import re
from pathlib import Path

# Константы стиля ASS
ASS_HEADER = """[Script Info]
Title: Converted from SRT
ScriptType: v4.00+
PlayResX: 384
PlayResY: 288

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,16,&H0000FFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def convert_srt_time_to_ass(srt_time):
    """Конвертирует временную метку из SRT формата в ASS формат"""
    return srt_time.strip().replace(',', '.')

def parse_srt_block(block):
    """Парсит блок SRT и возвращает временные метки и текст"""
    lines = [line.strip() for line in block.split('\n') if line.strip()]
    if len(lines) < 3:
        return None
    
    time_match = re.match(
        r'(\d{1,2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.]\d{3})',
        lines[1]
    )
    if not time_match:
        return None
    
    start_time = convert_srt_time_to_ass(time_match.group(1))
    end_time = convert_srt_time_to_ass(time_match.group(2))
    text = '\\N'.join(lines[2:])  # Объединяем текст с переносами
    
    return start_time, end_time, text

def convert_srt_to_ass(srt_content):
    """Конвертирует содержимое SRT файла в ASS формат"""
    ass_lines = [ASS_HEADER]
    blocks = [b for b in srt_content.split('\n\n') if b.strip()]
    
    for block in blocks:
        parsed = parse_srt_block(block)
        if parsed:
            start, end, text = parsed
            ass_lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
    
    return '\n'.join(ass_lines)

def process_srt_file(input_path, output_path):
    """Обрабатывает один SRT файл и сохраняет как ASS"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()
        
        ass_content = convert_srt_to_ass(srt_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        return True
    except Exception as e:
        print(f"Ошибка при обработке файла {input_path}: {str(e)}")
        return False

def batch_convert(input_path, output_path=None, overwrite=False):
    """
    Конвертирует SRT файл или все SRT файлы в папке
    :param input_path: Путь к файлу или папке
    :param output_path: Путь для сохранения (None - та же директория)
    :param overwrite: Перезаписывать существующие файлы
    """
    input_path = Path(input_path)
    
    # Обработка единичного файла
    if input_path.is_file() and input_path.suffix.lower() == '.srt':
        output_file = Path(output_path) if output_path else input_path.parent
        output_file = output_file / f"{input_path.stem}.ass"
        
        if output_file.exists() and not overwrite:
            print(f"Файл уже существует, пропускаем: {output_file}")
            return
        
        if process_srt_file(input_path, output_file):
            print(f"Успешно конвертирован: {input_path} -> {output_file}")
        return
    
    # Обработка папки
    if input_path.is_dir():
        output_dir = Path(output_path) if output_path else input_path
        output_dir.mkdir(parents=True, exist_ok=True)
        
        srt_files = list(input_path.glob('*.srt'))
        if not srt_files:
            print(f"Не найдено SRT файлов в директории: {input_path}")
            return
        
        print(f"Найдено {len(srt_files)} SRT файлов для конвертации...")
        success_count = 0
        
        for srt_file in srt_files:
            ass_file = output_dir / f"{srt_file.stem}.ass"
            
            if ass_file.exists() and not overwrite:
                print(f"Файл уже существует, пропускаем: {ass_file.name}")
                continue
            
            if process_srt_file(srt_file, ass_file):
                success_count += 1
                print(f"Конвертирован: {srt_file.name} -> {ass_file.name}")
        
        print(f"\nГотово! Успешно конвертировано {success_count}/{len(srt_files)} файлов.")
        return
    
    raise FileNotFoundError(f"Указанный путь не существует или не является SRT файлом: {input_path}")

def main():
    input_path = input("Введите путь к файлу или папке в формате C:/path/to/file: ")
    output_path = input("Введите путь для сохранения (или оставьте пустым для сохранения в той же директории) в формате C:/path/to/file: ")
    try:
        batch_convert(
            input_path,
            output_path,
            False
        )
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()