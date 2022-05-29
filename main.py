import converter
import os
from srt import SrcFormatBuilder
from converter.draft_content import CaptionsTracker


user_home = os.path.expanduser("~")
jianying_dir = "/Library/Containers/com.lemon.lvpro/Data/Movies/JianyingPro"
base_dir = user_home + jianying_dir + '/User Data/Projects/com.lveditor.draft'


if __name__ == '__main__':
    subtitle_file = "draft_info.json"
    counter = 0
    while True:
        capdir = input("请输入字幕文件目录：")
        filepath = base_dir + "/" + capdir + "/" + subtitle_file
        tracks = CaptionsTracker(filepath).read().caption_source
        srt_source = SrcFormatBuilder(tracks).build()
        with open('./subtitles.srt', 'w', encoding='utf-8') as f:
            f.write(srt_source)
            f.close()
        converter.srt_to_fcpxml('./subtitles.srt', './subtitles.fcpxml')
        counter += 1
        print('fcpxml字幕文件已生成-%s' % counter)

