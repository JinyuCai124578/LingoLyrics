from json_to_ppt import LyricsPPTGenerator
from md_to_json import LyricsParser
import json


md_path = r'c:\Users\lenovo\Desktop\日语学习\蜡烛\歌词_格式化.md'
json_path = md_path.replace('.md', '.json')
output_path= md_path.replace('.md', '.pptx')
    
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


try:
    generator = LyricsPPTGenerator(json_path)
    generator.generate(output_path)
    print(f"✅ 成功生成 PPT")
    print(f"📊 文件位置: {output_path}")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()