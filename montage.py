import praw
import os
import glob
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.volumex import volumex
from moviepy.editor import *
import secret as secret

BACKGROUND_MUSIC_PATH = 'assets/darudesandstorm.mp3'
SUBREDDIT = 'overwatch'
OUTPUT_FILE = "montage.mp4"
REDDIT_BASE = "https://www.reddit.com"

def getSubmissions(reddit):
    arr = []
    for submission in reddit.subreddit(SUBREDDIT).hot(limit=100):
        arr.append(submission)
    return arr

def getHighlightSubmissions(submission_arr):
    ret_arr = []
    for x in submission_arr:
        if x.link_flair_text and x.link_flair_text == "Highlight":
            ret_arr.append(x)
            if len(ret_arr) == 5:
                return ret_arr
    return ret_arr

def getHighlightURL(arr):
    ret_dict = {}
    for sub in arr:
        ret_dict[sub.author.name]= REDDIT_BASE + sub.permalink
    return ret_dict

def removeRawVideos():
    files = glob.glob('raw_videos/*')
    for f in files:
        try:
            os.remove(f)
        except:
            continue

def fixVideoNames():
    for filename in os.listdir("raw_videos/"):
        if ".mp4" not in filename:
            os.rename(f"raw_videos/{filename}", f"raw_videos/{filename}.mp4")


def downloadVideos(data):
    if not os.path.exists('raw_videos'):
        os.makedirs('raw_videos')
    removeRawVideos()
    counter = 1
    # data[op]=link
    for link in data:
        os.system(f"youtube-dl --output raw_videos/{counter} {data[link] }")
        data[link] = f"{counter}.mp4"
        counter+=1
    fixVideoNames()

def renderVideos(data):
    cliparr = []

    for entry in data:
        #if data[entry] == "5.mp4":
            #break
        c = VideoFileClip(f"raw_videos/{data[entry]}", target_resolution=(1080, 1920))
        t = TextClip(entry, fontsize = 50, color = 'white')
        #width, height
        t = t.set_position((0.1,0.8), relative=True).set_duration(c.duration)
        c = CompositeVideoClip([c, t])  

        cliparr.append(c)


    final_clip = concatenate_videoclips(cliparr, method='compose')
    final_clip = final_clip.fx(volumex, 0.3)
    audio_background = AudioFileClip(BACKGROUND_MUSIC_PATH).set_duration(final_clip.duration)
    final_audio = CompositeAudioClip([final_clip.audio, audio_background])
    ret_clip = final_clip.set_audio(final_audio)
    return ret_clip

def addIntroOutro(filename):
    cliparr = []
    intro = VideoFileClip('assets/intro.mp4', target_resolution=(1080, 1920))
    cliparr.append(intro)
    clips = VideoFileClip(filename, target_resolution=(1080, 1920))
    cliparr.append(clips)
    outro = VideoFileClip('assets/outro.mp4', target_resolution=(1080, 1920))
    cliparr.append(outro)

    final_video = concatenate_videoclips(cliparr, method='compose')
    return final_video


def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


    reddit = praw.Reddit(
        client_id=secret.CLIENT_ID,
        client_secret=secret.CLIENT_SECRET,
        user_agent=secret.USER_AGENT,
    )

    submissions = getSubmissions(reddit)
    highlight_submissions = getHighlightSubmissions(submissions)
    links = getHighlightURL(highlight_submissions)
    downloadVideos(links)
    clipVideo = renderVideos(links)
    clipVideo.write_videofile("clips.mp4")
    removeRawVideos()
    finalVideo = addIntroOutro('clips.mp4')
    finalVideo.write_videofile(OUTPUT_FILE)
    

if __name__ == "__main__":
    main()
    #https://www.youtube.com/watch?v=-_sLKEJexYs - outro
    # i lost it already - intro