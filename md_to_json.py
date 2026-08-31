import json
import re
from typing import List, Dict, Any
from dataclasses import asdict, dataclass

@dataclass
class Verse:
    """单句歌词"""
    verse_id: int
    japanese: str
    romaji: List[Dict[str, str]]
    translation: str
    annotations: List[Dict[str, str]]

class LyricsParser:
    def __init__(self, md_content: str):
        self.md_content = md_content
        self.verses = []
        self.metadata = {}
        self.ANNOTATION_MARKERS = set('①②③④⑤⑥⑦⑧⑨⑩')
        
    def parse(self) -> Dict[str, Any]:
        """主解析函数"""
        lines = self.md_content.split('\n')
        
        # 提取前两行作为标题
        self._extract_metadata(lines)
        
        # 按 --- 分割段落
        self._parse_verses(lines)
        
        return {
            "metadata": self.metadata,
            "verses": [asdict(v) for v in self.verses]
        }
    
    def _extract_metadata(self, lines: List[str]):
        """提取前两行作为日文和中文标题"""
        self.metadata['title'] = lines[0].strip() if len(lines) > 0 else ""
        self.metadata['title_cn'] = lines[1].strip() if len(lines) > 1 else ""
        
        # 提取作词作曲（如果存在）
        for line in lines[:10]:
            if line.startswith('作词'):
                self.metadata['lyricist'] = line.split(':')[1].strip()
            elif line.startswith('作曲'):
                self.metadata['composer'] = line.split(':')[1].strip()
    
    def _parse_verses(self, lines: List[str]):
        """按 --- 分割段落并解析"""
        verse_id = 1
        current_block = []
        
        for line in lines:
            if line.strip() == '---':
                # 处理上一个段落
                if current_block:
                    verse = self._parse_single_verse(current_block, verse_id)
                    if verse:
                        self.verses.append(verse)
                        verse_id += 1
                current_block = []
            else:
                current_block.append(line)
        
        # 处理最后一个段落
        if current_block:
            verse = self._parse_single_verse(current_block, verse_id)
            if verse:
                self.verses.append(verse)
    
    def _parse_single_verse(self, block: List[str], verse_id: int) -> Verse:
        """解析单个段落（4 行：日文、罗马音、翻译、注释...）"""
        # 过滤空行
        block = [line for line in block if line.strip()]
        
        if len(block) < 3:
            return None
        
        japanese = block[0].strip()
        romaji_line = block[1].strip()
        translation = block[2].strip()
        
        # 验证第一行是日文
        if not self._is_japanese(japanese):
            return None
        
        # 解析罗马音中的重音标记
        romaji_parsed = self._parse_romaji(romaji_line)
        
        # 收集注释（第 3 行之后的所有行）
        annotations = []
        for annotation_line in block[3:]:
            annotation = self._parse_annotation(annotation_line.strip())
            if annotation:
                annotations.append(annotation)
        
        return Verse(
            verse_id=verse_id,
            japanese=japanese,
            romaji=romaji_parsed,
            translation=translation,
            annotations=annotations
        )
    
    def _parse_romaji(self, romaji_line: str) -> List[Dict[str, str]]:
        """
        解析罗马音行中的重音标记
        **bold** → primary stress
        *italic* → secondary stress
        """
        result = []
        
        # 贪心匹配：优先匹配 **...** 和 *...*
        pattern = r'(\*\*[^*]+\*\*|\*[^*]+\*|[^*]+)'
        
        for match in re.finditer(pattern, romaji_line):
            text = match.group(0)
            
            if text.startswith('**') and text.endswith('**'):
                clean_text = text[2:-2]
                result.append({"text": clean_text, "stress": "primary"})
            elif text.startswith('*') and text.endswith('*') and not text.startswith('**'):
                clean_text = text[1:-1]
                result.append({"text": clean_text, "stress": "secondary"})
            else:
                result.append({"text": text, "stress": "none"})
        
        return result
    
    def _parse_annotation(self, annotation_line: str) -> Dict[str, str]:
        """
        解析单条注释
        支持多种格式：
        ①パッと（pa tto）：拟态词，瞬间发生的样子。
        ②良いよね（よいよね / yo i yo ne）：形容词+语尾，...
        ③のに：接续助词，逆接，表示转折。
        """
        if not annotation_line:
            return None
        
        # 检查是否以标记符开头
        first_char = annotation_line[0]
        if first_char not in self.ANNOTATION_MARKERS:
            return None
        
        marker = first_char
        rest = annotation_line[1:].strip()
        
        # 尝试提取词项和内容
        # 格式 1: 词（かな / romaji）：内容
        # 格式 2: 词（かな）：内容
        # 格式 3: 词：内容（仅有词和内容）
        
        # 模式 1: 词（...）：内容
        pattern1 = r'^([^\（：]+)（([^）]+)）：(.+)$'
        match = re.match(pattern1, rest)
        
        if match:
            term = match.group(1).strip()
            pronunciation = match.group(2).strip()
            content = match.group(3).strip()
            
            return {
                "marker": marker,
                "term": term,
                "pronunciation": pronunciation,  # 可能是 "かな" 或 "かな / romaji"
                "content": content
            }
        
        # 模式 2: 直接是内容（没有词项）
        pattern2 = r'^：(.+)$'
        match = re.match(pattern2, rest)
        if match:
            content = match.group(1).strip()
            return {
                "marker": marker,
                "term": "",
                "pronunciation": "",
                "content": content
            }
        
        # 模式 3: 词：内容（没有括号）
        if '：' in rest:
            parts = rest.split('：', 1)
            return {
                "marker": marker,
                "term": parts[0].strip(),
                "pronunciation": "",
                "content": parts[1].strip()
            }
        
        return None
    
    def _is_japanese(self, text: str) -> bool:
        """检测文本是否包含日文字符（平假名、片假名、汉字）"""
        japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'
        return bool(re.search(japanese_pattern, text))


if __name__ == "__main__":
    # 读取 MD 文件
    md_path = r'c:\Users\lenovo\Desktop\日语学习\歌词_example.md'
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        parser = LyricsParser(md_content)
        result = parser.parse()
        
        # 输出 JSON
        json_path = md_path.replace('.md', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 解析完成！")
        print(f"📄 输入文件: {md_path}")
        print(f"📊 输出文件: {json_path}")
        print(f"📈 识别段落数: {len(result['verses'])}")
        print("\n📋 元数据:")
        print(json.dumps(result['metadata'], ensure_ascii=False, indent=2))
        print("\n🎵 第一个段落预览:")
        if result['verses']:
            print(json.dumps(result['verses'][0], ensure_ascii=False, indent=2))
    
    except FileNotFoundError:
        print(f"❌ 文件不存在: {md_path}")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()