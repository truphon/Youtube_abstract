from Youtube_abstract import app
from flask import render_template,request
from youtube_transcript_api import YouTubeTranscriptApi
import time

#html表示用
@app.route('/')
def index():
    return render_template(
        'index.html'
    )

@app.route('/transcript',methods=['POST'])
def transcript():
    ##1.まずは、youtubeの動画idから、文字起こし情報を取得する。
    #動画idを取得する。
    movie_URL=request.form['URL']
    #URLから動画idを取得する。
    query_char='?v=' #URLのこの文字列以降の文字を取得したい。
    idx = movie_URL.find(query_char) #?=の一つ後の順番を取得。
    movie_id=movie_URL[idx+3:] #?=より後の文字列を取得。

    script=""#文字起こし情報を格納する変数

    #動画idから、テキスト情報を取得(テキスト情報の他に、各テキストの時間なども含む。)
    transcript_list =YouTubeTranscriptApi.list_transcripts(movie_id)

    #動画から取得した情報から、テキスト情報のみを抽出して、scriptに格納
    for transcript in transcript_list:
        for tr in transcript.fetch():
            #print(tr) # {'text': '字幕のテキスト情報', 'start': 字幕の開始時間, 'duration': 字幕が表示されている時間}
            script= script + tr['text']

    #print(script) #文字起こし情報

    ##2.次に文字起こし情報をChat-GPTに投げて、要約した結果を取得する。
    import openai

    #Chat-GPTから取得したAPI KEY
    api_key_by_GPT = "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"

    #apikeyを指定
    openai.api_key = api_key_by_GPT

    # ChatGPTのモデルを指定してAPIを呼び出す
    def ask_gpt(prompt):
        res = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}])
        return res.choices[0]['message']['content']

    #Chat-GPTのプロンプトに入力する文字列を作成
    prompt_script="次の文章を要約してください。{}".format(script)

    print(prompt_script)
    #ChatGPTへの入力した結果(要約結果)
    abstract_message=(ask_gpt(prompt_script))
    print(abstract_message)
    print('要約終了')

    return render_template(
        'index.html',
        abstract=abstract_message
    )