from src.youtube_client import YouTubeClient
from src.video_processor import VideoProcessor
from src.summarizer import VideoSummarizer
from src.insight_generator import InsightGenerator
from config.config import PLAYLIST_ID

def main():
    # 初始化组件
    youtube_client = YouTubeClient()
    video_processor = VideoProcessor()
    summarizer = VideoSummarizer()
    insight_generator = InsightGenerator()
    
    # 获取视频列表
    print("获取播放列表视频...")
    videos = youtube_client.get_playlist_videos(PLAYLIST_ID)
    print(f"找到 {len(videos)} 个视频")
    
    # 过滤industry相关视频
    industry_videos = video_processor.filter_industry_videos(videos)
    print(f"找到 {len(industry_videos)} 个industry相关视频")
    
    # 生成摘要
    summaries = []
    for video in industry_videos:
        print(f"正在生成视频摘要: {video['title']}")
        summary = summarizer.generate_summary(video)
        summaries.append(summary)
    
    # 生成整体洞察
    print("生成整体洞察...")
    insights = insight_generator.generate_insights(summaries)
    
    # 输出结果
    print("\n=== 最终洞察 ===")
    print(insights)

if __name__ == "__main__":
    main() 